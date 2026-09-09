from typing import Literal

from pydantic import BaseModel, EmailStr


class EmployeeLeave(BaseModel):
    employee_id: str
    employee_name: str
    employee_email: EmailStr
    total_leave_balance_allocated: float
    leave_balance_used_this_month: float
    leave_balance_remaining: float


class MCPEmployee(BaseModel):
    employee: str
    employee_name: str
    employee_email: EmailStr


class MCPLeaveBalance(BaseModel):
    employee: str
    total_leave_balance_allocated: float
    leave_balance_remaining: float
    leave_balance_used_this_month: float = 0.0


class LeaveRiskAssessment(BaseModel):
    is_low_balance: bool
    is_lop_risk: bool
    alert_reason: str


class LeaveEmailDraft(BaseModel):
    subject: str
    body: str


class PendingReviewEmail(BaseModel):
    employee: EmployeeLeave
    draft: LeaveEmailDraft
    risk: LeaveRiskAssessment


class WorkflowEmployeeResult(BaseModel):
    employee_id: str
    employee_name: str
    employee_email: EmailStr
    status: Literal["sent", "pending_review", "rejected", "failed"]
    message: str


class WorkflowSummary(BaseModel):
    total_employees_processed: int
    sent_count: int
    pending_review_count: int
    failed_count: int
    results: list[WorkflowEmployeeResult]


class TriggerWorkflowRequest(BaseModel):
    pass


class ReviewDecisionRequest(BaseModel):
    action: Literal["approve", "reject"]


class PendingReviewsResponse(BaseModel):
    pending_reviews: list[PendingReviewEmail]
