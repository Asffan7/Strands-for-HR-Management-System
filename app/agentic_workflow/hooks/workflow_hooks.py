from strands.hooks import HookProvider, HookRegistry
from strands.hooks.events import (
    BeforeToolCallEvent,
)


class WorkflowHookProvider(HookProvider):
    """Hook provider for lightweight workflow observability and guardrails."""

    def register_hooks(self, registry: HookRegistry, **kwargs) -> None:
        registry.add_callback(BeforeToolCallEvent, self.on_before_tool_call)

    def on_before_tool_call(self, event: BeforeToolCallEvent) -> None:
        tool_name = event.tool_use.get("name")
        if tool_name in {"hrms_find_employee", "hrms_get_leave_balance"} and not event.tool_use.get("input"):
            event.cancel_tool = f"{tool_name} requires input"
