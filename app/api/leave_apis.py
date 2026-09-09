from fastapi import APIRouter
import random
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/leaves", tags=["leaves"])


class LeaveBalance(BaseModel):
    total_leave_balance_allocated: int
    leave_balance_used_this_month: float
    leave_balance_remaining: float


class EmployeeLeave(BaseModel):
    employee_id: int
    employee_name: str
    employee_email: EmailStr
    total_leave_balance_allocated: int
    leave_balance_used_this_month: float
    leave_balance_remaining: float


class SendEmailRequest(BaseModel):
    employee_id: int
    employee_name: str
    employee_email: EmailStr
    subject: str
    body: str


class SendEmailResponse(BaseModel):
    status: str
    message: str


EMPLOYEES = [
    {"employee_id": 101, "employee_name": "Aarav Sharma", "employee_email": "aarav.sharma@example.com"},
    {"employee_id": 102, "employee_name": "Isha Verma", "employee_email": "isha.verma@example.com"},
    {"employee_id": 103, "employee_name": "Rohan Iyer", "employee_email": "rohan.iyer@example.com"},
    {"employee_id": 104, "employee_name": "Neha Joshi", "employee_email": "neha.joshi@example.com"},
]


@router.get("/leave_balances", response_model=LeaveBalance)
async def get_leave() -> LeaveBalance:
    total_leave_balance_allocated = random.randint(8, 24)
    leave_balance_used_this_month = round(random.uniform(0, total_leave_balance_allocated), 1)
    leave_balance_remaining = round(total_leave_balance_allocated - leave_balance_used_this_month, 1)

    return LeaveBalance(
        total_leave_balance_allocated=total_leave_balance_allocated,
        leave_balance_used_this_month=leave_balance_used_this_month,
        leave_balance_remaining=leave_balance_remaining,
    )


@router.get("/employee_leave_balances", response_model=list[EmployeeLeave])
async def get_employee_leave_balances() -> list[EmployeeLeave]:
    employee_leaves: list[EmployeeLeave] = []
    for employee in EMPLOYEES:
        total_allocated = random.randint(10, 24)
        used = round(random.uniform(0, total_allocated), 1)
        remaining = round(total_allocated - used, 1)

        employee_leaves.append(
            EmployeeLeave(
                employee_id=employee["employee_id"],
                employee_name=employee["employee_name"],
                employee_email=employee["employee_email"],
                total_leave_balance_allocated=total_allocated,
                leave_balance_used_this_month=used,
                leave_balance_remaining=remaining,
            )
        )

    return employee_leaves


@router.post("/send_email", response_model=SendEmailResponse)
async def send_email(payload: SendEmailRequest) -> SendEmailResponse:
    return SendEmailResponse(
        status="sent",
        message=f"Email queued for {payload.employee_name} <{payload.employee_email}>",
    )
    