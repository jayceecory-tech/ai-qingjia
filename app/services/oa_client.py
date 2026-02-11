"""OA 系统接口客户端 - 预留接口，当前使用模拟数据.

TODO: 对接真实 OA 系统时，替换各方法中的模拟逻辑为真实 HTTP 调用。
"""

import uuid

from app.models.schemas import (
    LeaveBalanceItem,
    LeaveBalanceResponse,
    LeaveBalanceType,
    LeaveRequest,
    LeaveResponse,
)

# 模拟员工数据
_MOCK_EMPLOYEES = {
    "EMP001": {
        "name": "张三",
        "department": "技术部",
    },
    "EMP002": {
        "name": "李四",
        "department": "产品部",
    },
    "EMP003": {
        "name": "王五",
        "department": "市场部",
    },
}

# 模拟假期余额数据
_MOCK_BALANCES = {
    "EMP001": {
        LeaveBalanceType.ANNUAL: {"total": 10, "used": 3},
        LeaveBalanceType.COMPENSATORY: {"total": 5, "used": 1},
        LeaveBalanceType.PAID_SICK: {"total": 10, "used": 0},
        LeaveBalanceType.WELFARE_2022: {"total": 2, "used": 2},
        LeaveBalanceType.WELFARE_2023: {"total": 2, "used": 0},
        LeaveBalanceType.PARENTAL: {"total": 10, "used": 2},
    },
    "EMP002": {
        LeaveBalanceType.ANNUAL: {"total": 10, "used": 5},
        LeaveBalanceType.COMPENSATORY: {"total": 3, "used": 2},
        LeaveBalanceType.PAID_SICK: {"total": 10, "used": 1},
        LeaveBalanceType.WELFARE_2022: {"total": 2, "used": 1},
        LeaveBalanceType.WELFARE_2023: {"total": 2, "used": 0},
        LeaveBalanceType.PARENTAL: {"total": 10, "used": 0},
    },
    "EMP003": {
        LeaveBalanceType.ANNUAL: {"total": 15, "used": 7},
        LeaveBalanceType.COMPENSATORY: {"total": 4, "used": 4},
        LeaveBalanceType.PAID_SICK: {"total": 10, "used": 3},
        LeaveBalanceType.WELFARE_2022: {"total": 2, "used": 0},
        LeaveBalanceType.WELFARE_2023: {"total": 2, "used": 1},
        LeaveBalanceType.PARENTAL: {"total": 10, "used": 5},
    },
}


class OAClient:
    """OA 系统客户端.

    当前使用模拟数据，后续对接真实 OA 系统时替换实现。
    预留接口地址配置:
        - base_url: OA 系统基础地址
        - api_key: 接口鉴权密钥
    """

    def __init__(self, base_url: str = "", api_key: str = ""):
        self.base_url = base_url
        self.api_key = api_key

    async def query_leave_balance(
        self, employee_id: str, leave_type: LeaveBalanceType | None = None
    ) -> LeaveBalanceResponse:
        """查询假期余额.

        TODO: 替换为真实 OA 接口调用
        真实接口示例:
            GET {base_url}/api/leave/balance?employee_id={employee_id}&type={leave_type}
        """
        if employee_id not in _MOCK_EMPLOYEES:
            return LeaveBalanceResponse(
                employee_id=employee_id,
                employee_name="未知",
                department="未知",
                balances=[],
            )

        emp = _MOCK_EMPLOYEES[employee_id]
        emp_balances = _MOCK_BALANCES.get(employee_id, {})

        balances = []
        if leave_type:
            # 查询指定类型
            if leave_type in emp_balances:
                b = emp_balances[leave_type]
                balances.append(
                    LeaveBalanceItem(
                        leave_type=leave_type.value,
                        total_days=b["total"],
                        used_days=b["used"],
                        remaining_days=b["total"] - b["used"],
                    )
                )
        else:
            # 查询全部
            for lt, b in emp_balances.items():
                balances.append(
                    LeaveBalanceItem(
                        leave_type=lt.value,
                        total_days=b["total"],
                        used_days=b["used"],
                        remaining_days=b["total"] - b["used"],
                    )
                )

        return LeaveBalanceResponse(
            employee_id=employee_id,
            employee_name=emp["name"],
            department=emp["department"],
            balances=balances,
        )

    async def submit_leave_request(self, request: LeaveRequest) -> LeaveResponse:
        """提交请假申请.

        TODO: 替换为真实 OA 接口调用
        真实接口示例:
            POST {base_url}/api/leave/request
            Body: LeaveRequest JSON
        """
        # 验证员工信息
        if request.employee_id not in _MOCK_EMPLOYEES:
            return LeaveResponse(
                success=False,
                message=f"未找到员工编号 {request.employee_id} 的信息",
            )

        # 模拟提交成功
        request_id = f"LR-{uuid.uuid4().hex[:8].upper()}"
        return LeaveResponse(
            success=True,
            request_id=request_id,
            message=f"请假申请已提交成功，申请单号: {request_id}，等待审批。",
        )


# 全局单例
oa_client = OAClient()
