"""AI 对话服务 - 支持流式输出和 Skills 调用."""

import json
import os
from collections.abc import AsyncGenerator
from dotenv import load_dotenv

from openai import AsyncOpenAI

from app.skills.leave_skills import LEAVE_SKILLS, execute_skill

# 加载环境变量
load_dotenv()

SYSTEM_PROMPT = """你是一个智能请假助手，帮助员工查询假期余额和提交请假申请。

你可以帮助用户完成以下操作：
1. **查询假期余额**：查询年假、调休、带薪病假、2022福利年假、2023福利年假、育儿假的余额
2. **提交请假申请**：帮助用户填写并提交请假申请

请假类型包括：事假、病假、年假、调休、带薪病假

提交请假需要以下信息：
- 姓名
- 部门
- 员工编号
- 请假类型
- 请假事由
- 请假开始时间（YYYY-MM-DD格式）
- 请假结束时间（YYYY-MM-DD格式）
- 请假天数

重要行为规范：
- 当用户提供的信息不完整时，请主动询问缺少的信息。
- 回答要简洁、专业、友好。
- 查询余额后，前端会自动展示可视化卡片，你只需用一两句话做简要总结即可（如"以上是您的假期余额概况"），不要再以列表形式重复所有数据。
- 提交请假后，前端会自动展示结果卡片，你只需做简要确认说明即可。
- 在收集请假信息时，如果已知员工编号，可以先调用查询接口获取姓名和部门，避免重复询问。
- 使用 **加粗** 来强调关键信息。

模拟员工数据（可用于测试）：
- EMP001: 张三，技术部
- EMP002: 李四，产品部
- EMP003: 王五，市场部
"""


def _get_client() -> AsyncOpenAI:
    """获取 OpenAI 客户端.

    支持通过环境变量配置不同的 API 提供商（如 DeepSeek、通义千问等）。
    """
    import httpx
    
    api_key = os.getenv("OPENAI_API_KEY", "")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("OPENAI_MODEL", "gpt-4o")
    
    print(f"DEBUG: API Key: {api_key[:10]}...")
    print(f"DEBUG: Base URL: {base_url}")
    print(f"DEBUG: Model: {model}")
    
    # 禁用SSL验证（仅用于测试，生产环境应使用正确证书）
    transport = httpx.AsyncHTTPTransport(retries=3, verify=False)
    
    return AsyncOpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=httpx.Timeout(60.0, connect=10.0),  # 总超时60秒，连接超时10秒
        http_client=httpx.AsyncClient(
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
            transport=transport,
        ),
    )


def _get_model() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-4o")


def _build_messages(
    user_message: str,
    history: list[dict],
    employee_id: str | None = None,
) -> list[dict]:
    """构建消息列表."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if employee_id:
        messages.append(
            {
                "role": "system",
                "content": f"当前用户的员工编号是: {employee_id}",
            }
        )

    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": user_message})
    return messages


async def chat_stream(
    user_message: str,
    history: list[dict] | None = None,
    employee_id: str | None = None,
) -> AsyncGenerator[str, None]:
    """流式对话，支持 skills 调用.

    使用 SSE (Server-Sent Events) 格式输出。
    """
    client = _get_client()
    model = _get_model()
    messages = _build_messages(user_message, history or [], employee_id)

    try:
        # 第一次请求（可能触发 tool_call）
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            tools=LEAVE_SKILLS,
            stream=True,
        )

        collected_content = ""
        tool_calls_data: dict[int, dict] = {}

        async for chunk in response:
            delta = chunk.choices[0].delta if chunk.choices else None
            if not delta:
                continue

            # 收集文本内容并流式输出
            if delta.content:
                collected_content += delta.content
                yield f"data: {json.dumps({'type': 'content', 'content': delta.content}, ensure_ascii=False)}\n\n"

            # 收集 tool_calls
            if delta.tool_calls:
                for tc in delta.tool_calls:
                    idx = tc.index
                    if idx not in tool_calls_data:
                        tool_calls_data[idx] = {
                            "id": "",
                            "function": {"name": "", "arguments": ""},
                        }
                    if tc.id:
                        tool_calls_data[idx]["id"] = tc.id
                    if tc.function:
                        if tc.function.name:
                            tool_calls_data[idx]["function"]["name"] += tc.function.name
                        if tc.function.arguments:
                            tool_calls_data[idx]["function"]["arguments"] += tc.function.arguments

        # 如果有 tool_calls，执行并继续对话
        if tool_calls_data:
            # 构建 assistant 消息
            assistant_msg = {
                "role": "assistant",
                "content": collected_content or None,
                "tool_calls": [
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": tc["function"],
                    }
                    for tc in tool_calls_data.values()
                ],
            }
            messages.append(assistant_msg)

            # 执行每个 tool_call
            for tc in tool_calls_data.values():
                func_name = tc["function"]["name"]
                func_args = tc["function"]["arguments"]

                yield f"data: {json.dumps({'type': 'skill_call', 'skill': func_name, 'arguments': func_args}, ensure_ascii=False)}\n\n"

                try:
                    result = await execute_skill(func_name, func_args)
                except Exception as e:
                    result = json.dumps(
                        {"error": f"调用 {func_name} 失败: {e!s}"},
                        ensure_ascii=False,
                    )

                yield f"data: {json.dumps({'type': 'skill_result', 'skill': func_name, 'result': result}, ensure_ascii=False)}\n\n"

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": result,
                    }
                )

            # 第二次请求，让模型根据 tool 结果生成最终回复
            response2 = await client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
            )

            async for chunk in response2:
                delta = chunk.choices[0].delta if chunk.choices else None
                if not delta:
                    continue
                if delta.content:
                    yield f"data: {json.dumps({'type': 'content', 'content': delta.content}, ensure_ascii=False)}\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': f'服务异常: {e!s}'}, ensure_ascii=False)}\n\n"

    yield f"data: {json.dumps({'type': 'done'})}\n\n"
