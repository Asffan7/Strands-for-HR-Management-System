import json
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from typing import Any

from mcp.client.streamable_http import streamable_http_client
from strands.tools.mcp import MCPClient

from app.agentic_workflow.schemas.workflow_schemas import EmployeeLeave
from app.configuration.config import Settings


def _as_mapping(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if isinstance(value, dict):
        return value
    return value


def _result_payload(result: Any) -> Any:
    structured = _as_mapping(getattr(result, "structuredContent", None))
    if structured:
        return structured

    content = getattr(result, "content", None)
    if content is None and isinstance(result, dict):
        content = result.get("content")
    values: list[Any] = []
    for item in content or []:
        item = _as_mapping(item)
        if isinstance(item, dict):
            if "text" in item:
                text = item["text"]
                try:
                    values.append(json.loads(text))
                except (TypeError, json.JSONDecodeError):
                    values.append(text)
            elif "data" in item:
                values.append(item["data"])
        else:
            values.append(item)

    if len(values) == 1:
        return values[0]
    return values


def _items(payload: Any, *keys: str) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for key in keys:
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        return [payload]
    raise ValueError("MCP returned an unsupported payload")


def _first_value(data: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = data.get(key)
        if value not in (None, ""):
            return value
    return None


def _employee_id(data: dict[str, Any]) -> str:
    value = _first_value(data, "employee", "employee_id", "name", "id")
    if value is None:
        raise ValueError("MCP employee result is missing an employee identifier")
    return str(value)


def _employee_record(data: dict[str, Any]) -> tuple[str, str, str]:
    employee_id = _employee_id(data)
    name = _first_value(data, "employee_name", "full_name", "name")
    email = _first_value(data, "employee_email", "company_email", "email", "user_id")
    if not name or not email:
        raise ValueError(f"MCP employee {employee_id} is missing name or email")
    return employee_id, str(name), str(email)


def _balance_record(data: dict[str, Any]) -> tuple[float, float, float]:
    allocated = _first_value(
        data,
        "total_leave_balance_allocated",
        "allocated",
        "total_allocated",
        "allocated_leave",
    )
    remaining = _first_value(
        data,
        "leave_balance_remaining",
        "remaining",
        "remaining_leave",
    )
    used = _first_value(data, "leave_balance_used_this_month", "used_this_month")
    if allocated is None or remaining is None:
        raise ValueError("MCP leave balance result is missing allocated or remaining leave")
    allocated_value = float(allocated)
    remaining_value = float(remaining)
    used_value = allocated_value - remaining_value if used is None else float(used)
    return allocated_value, used_value, remaining_value


@contextmanager
def mcp_client(settings: Settings) -> Iterator[MCPClient]:
    client = MCPClient(lambda: streamable_http_client(settings.FRAPPE_MCP_URL.strip()))
    with client:
        yield client


def get_employee_leave_balances(settings: Settings) -> list[EmployeeLeave]:
    with mcp_client(settings) as client:
        employee_query = {"query": settings.MCP_EMPLOYEE_QUERY, "status": "Active", "limit": 50}
        employees_result = client.call_tool_sync(
            tool_use_id=f"find-employees-{uuid.uuid4()}",
            name="hrms_find_employee",
            arguments=employee_query,
        )
        employee_items = _items(_result_payload(employees_result), "employees", "data", "results")
        employees: list[EmployeeLeave] = []
        for employee_data in employee_items:
            employee_id, employee_name, employee_email = _employee_record(employee_data)
            balance_input = {
                "employee": employee_id,
                "date": date.today().isoformat(),
            }
            balance_result = client.call_tool_sync(
                tool_use_id=f"leave-balance-{uuid.uuid4()}",
                name="hrms_get_leave_balance",
                arguments=balance_input,
            )
            balance_payload = _result_payload(balance_result)
            balance_items = _items(balance_payload, "balance", "data", "result")
            allocated, used, remaining = _balance_record(balance_items[0])
            employees.append(
                EmployeeLeave(
                    employee_id=employee_id,
                    employee_name=employee_name,
                    employee_email=employee_email,
                    total_leave_balance_allocated=allocated,
                    leave_balance_used_this_month=used,
                    leave_balance_remaining=remaining,
                )
            )
    return employees
