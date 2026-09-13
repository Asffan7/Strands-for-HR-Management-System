import atexit
import logging
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from strands import Agent, tool
from strands.models.mistral import MistralModel
from strands.tools.mcp import MCPClient

from app.configuration.config import Settings, get_mcp_headers, get_settings
from app.agentic_workflow.callbacks.workflow_callback_handler import WorkflowCallbackHandler
from app.agentic_workflow.hooks.workflow_hooks import WorkflowHookProvider
from app.agentic_workflow.instructions.system_instructions import WORKFLOW_SYSTEM_PROMPT
from app.agentic_workflow.schemas.workflow_schemas import WorkflowSummary
from app.agentic_workflow.services.workflow_service import trigger_leave_workflow
from app.agentic_workflow.skills.leave_email_skills import WORKFLOW_SKILLS_PLUGIN


def configure_verbose_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logging.getLogger("strands").setLevel(
        os.getenv("STRANDS_LOG_LEVEL", "INFO").upper()
    )
    for logger_name in (
        "httpcore",
        "httpx",
        "mcp",
        "strands.telemetry",
    ):
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    logging.getLogger("mcp.client.streamable_http").setLevel(logging.ERROR)


@tool
def run_leave_email_workflow() -> WorkflowSummary:
    """Trigger leave workflow: fetch leave data, draft emails, and send/pending based on risk."""
    return trigger_leave_workflow()


_MCP_CLIENTS: list[MCPClient] = []


def _load_mcp_tools(settings: Settings) -> tuple[MCPClient, list[object]]:
    client = MCPClient(
        url=settings.FRAPPE_MCP_URL.strip(),
        headers=get_mcp_headers(settings),
    )
    client.start()
    atexit.register(lambda: client.stop(None, None, None))
    _MCP_CLIENTS.append(client)
    tools = client.list_tools_sync(
        tool_filters={"allowed": ["hrms_find_employee", "hrms_get_leave_balance"]}
    )
    return client, list(tools)


def build_leave_agent() -> Agent:
    settings = get_settings()
    _, mcp_tools = _load_mcp_tools(settings)
    model = MistralModel(
        api_key=settings.MISTRAL_API_KEY,
        client_args={"server_url": settings.MISTRAL_SERVER_URL.strip()},
        model_id="ministral-3b-2512",
    )

    agent = Agent(
        model,
        tools=[run_leave_email_workflow, *mcp_tools],
        system_prompt=WORKFLOW_SYSTEM_PROMPT,
        callback_handler=WorkflowCallbackHandler(),
        hooks=[WorkflowHookProvider()],
        plugins=[WORKFLOW_SKILLS_PLUGIN],
    )
    return agent


agent: Agent | None = None


if __name__ == "__main__":
    configure_verbose_logging()
    agent = build_leave_agent()
    response = agent(
        """
        Trigger the leave email workflow now.
        Use hrms_find_employee and hrms_get_leave_balance from the connected MCP server
        when inspecting employee leave data.
        Use the run_leave_email_workflow tool. Fetch leave balances, draft
        personalized emails, send safe emails, and place low-balance or
        Loss-of-Pay risk emails into human review.
        """
    )
    print("\nFinal workflow response:")
    print(response)
