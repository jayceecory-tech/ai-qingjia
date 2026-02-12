"""API 路由定义."""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.models.schemas import (
    ChatRequest,
    LeaveBalanceQuery,
    LeaveBalanceResponse,
    LeaveRequest,
    LeaveResponse,
)
from app.services.chat_service import chat_stream
from app.services.oa_client import oa_client

router = APIRouter()


# ==================== 对话接口 ====================


@router.post("/api/chat/stream")
async def chat_stream_api(req: ChatRequest):
    """流式对话接口 (SSE).

    通过自然语言对话实现请假查询和申请。
    """
    history = [{"role": m.role, "content": m.content} for m in req.history]

    return StreamingResponse(
        chat_stream(
            user_message=req.message,
            history=history,
            employee_id=req.employee_id,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ==================== OA 直接接口（预留） ====================


@router.post("/api/leave/balance", response_model=LeaveBalanceResponse)
async def query_leave_balance(query: LeaveBalanceQuery):
    """查询假期余额接口."""
    return await oa_client.query_leave_balance(
        employee_id=query.employee_id,
        leave_type=query.leave_type,
    )


@router.post("/api/leave/request", response_model=LeaveResponse)
async def submit_leave_request(request: LeaveRequest):
    """提交请假申请接口."""
    return await oa_client.submit_leave_request(request)
