"""请假 OA 系统数据模型定义."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class LeaveType(str, Enum):
    """请假类型."""

    PERSONAL = "事假"
    SICK = "病假"
    ANNUAL = "年假"
    COMPENSATORY = "调休"
    PAID_SICK = "带薪病假"


class LeaveBalanceType(str, Enum):
    """假期余额类型."""

    ANNUAL = "年假"
    COMPENSATORY = "调休"
    PAID_SICK = "带薪病假"
    WELFARE_2022 = "2022福利年假"
    WELFARE_2023 = "2023福利年假"
    PARENTAL = "育儿假"


class LeaveBalanceQuery(BaseModel):
    """假期余额查询请求."""

    employee_id: str = Field(..., description="员工编号")
    leave_type: Optional[LeaveBalanceType] = Field(None, description="假期类型，不传则查询全部")


class LeaveBalanceItem(BaseModel):
    """单项假期余额."""

    leave_type: str = Field(..., description="假期类型")
    total_days: float = Field(..., description="总天数")
    used_days: float = Field(..., description="已使用天数")
    remaining_days: float = Field(..., description="剩余天数")


class LeaveBalanceResponse(BaseModel):
    """假期余额查询响应."""

    employee_id: str
    employee_name: str
    department: str
    balances: list[LeaveBalanceItem]


class LeaveRequest(BaseModel):
    """请假申请."""

    employee_name: str = Field(..., description="姓名")
    department: str = Field(..., description="部门")
    employee_id: str = Field(..., description="员工编号")
    leave_type: LeaveType = Field(..., description="请假类型")
    reason: str = Field(..., description="请假事由")
    start_date: str = Field(..., description="请假开始时间，格式: YYYY-MM-DD")
    end_date: str = Field(..., description="请假结束时间，格式: YYYY-MM-DD")
    days: float = Field(..., gt=0, description="请假天数")


class LeaveResponse(BaseModel):
    """请假申请响应."""

    success: bool
    request_id: Optional[str] = None
    message: str


class ChatMessage(BaseModel):
    """对话消息."""

    role: str = Field(..., description="角色: user 或 assistant")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    """对话请求."""

    message: str = Field(..., description="用户消息")
    employee_id: Optional[str] = Field(None, description="员工编号")
    history: list[ChatMessage] = Field(default_factory=list, description="对话历史")
