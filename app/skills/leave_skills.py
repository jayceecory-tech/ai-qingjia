"""AI Skills 定义 - 请假相关工具函数.

定义供 AI 模型调用的 tools (function calling / skills)。
"""

import json

from app.models.schemas import LeaveBalanceType, LeaveRequest, LeaveType
from app.services.oa_client import oa_client

# Skills 定义（OpenAI function calling 格式）
LEAVE_SKILLS = [
    {
        "type": "function",
        "function": {
            "name": "query_leave_balance",
            "description": "查询员工的假期余额信息，包括年假、调休、带薪病假、2022福利年假、2023福利年假、育儿假等各类假期的总天数、已使用天数和剩余天数",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {
                        "type": "string",
                        "description": "员工编号，例如 EMP001",
                    },
                    "leave_type": {
                        "type": "string",
                        "enum": [t.value for t in LeaveBalanceType],
                        "description": "要查询的假期类型，不传则查询全部假期余额",
                    },
                },
                "required": ["employee_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "submit_leave_request",
            "description": "提交请假申请。需要员工姓名、部门、员工编号、请假类型、请假事由、开始日期、结束日期和请假天数",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_name": {
                        "type": "string",
                        "description": "员工姓名",
                    },
                    "department": {
                        "type": "string",
                        "description": "所属部门",
                    },
                    "employee_id": {
                        "type": "string",
                        "description": "员工编号",
                    },
                    "leave_type": {
                        "type": "string",
                        "enum": [t.value for t in LeaveType],
                        "description": "请假类型: 事假、病假、年假、调休、带薪病假",
                    },
                    "reason": {
                        "type": "string",
                        "description": "请假事由",
                    },
                    "start_date": {
                        "type": "string",
                        "description": "请假开始日期，格式 YYYY-MM-DD",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "请假结束日期，格式 YYYY-MM-DD",
                    },
                    "days": {
                        "type": "number",
                        "description": "请假天数",
                    },
                },
                "required": [
                    "employee_name",
                    "department",
                    "employee_id",
                    "leave_type",
                    "reason",
                    "start_date",
                    "end_date",
                    "days",
                ],
            },
        },
    },
]


async def execute_skill(name: str, arguments: str) -> str:
    """执行 skill 并返回结果."""
    try:
        args = json.loads(arguments)
    except json.JSONDecodeError as e:
        return json.dumps(
            {"error": f"参数解析失败: {e!s}"}, ensure_ascii=False
        )

    if name == "query_leave_balance":
        leave_type = None
        if args.get("leave_type"):
            try:
                leave_type = LeaveBalanceType(args["leave_type"])
            except ValueError:
                return json.dumps(
                    {"error": f"不支持的假期类型: {args['leave_type']}"},
                    ensure_ascii=False,
                )
        employee_id = args.get("employee_id", "")
        if not employee_id:
            return json.dumps(
                {"error": "缺少员工编号 employee_id"}, ensure_ascii=False
            )
        result = await oa_client.query_leave_balance(
            employee_id=employee_id,
            leave_type=leave_type,
        )
        return result.model_dump_json(ensure_ascii=False)

    elif name == "submit_leave_request":
        required_fields = [
            "employee_name", "department", "employee_id",
            "leave_type", "reason", "start_date", "end_date", "days",
        ]
        missing = [f for f in required_fields if not args.get(f)]
        if missing:
            return json.dumps(
                {"error": f"缺少必要字段: {', '.join(missing)}"},
                ensure_ascii=False,
            )
        try:
            request = LeaveRequest(
                employee_name=args["employee_name"],
                department=args["department"],
                employee_id=args["employee_id"],
                leave_type=LeaveType(args["leave_type"]),
                reason=args["reason"],
                start_date=args["start_date"],
                end_date=args["end_date"],
                days=float(args["days"]),
            )
        except (ValueError, TypeError) as e:
            return json.dumps(
                {"error": f"参数校验失败: {e!s}"}, ensure_ascii=False
            )
        result = await oa_client.submit_leave_request(request)
        return result.model_dump_json(ensure_ascii=False)

    return json.dumps({"error": f"未知的 skill: {name}"}, ensure_ascii=False)
