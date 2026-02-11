# AI 请假助手

基于 AI Skills (Function Calling) 的智能请假 OA 系统，支持通过自然语言对话完成假期查询和请假申请，流式 API 输出。

## 功能

- **假期余额查询**：年假、调休、带薪病假、2022福利年假、2023福利年假、育儿假
- **请假申请提交**：事假、病假、年假、调休、带薪病假
- **流式对话**：基于 SSE 的流式 AI 对话
- **AI Skills**：自动识别用户意图，调用对应的 OA 接口

## 技术架构

```
├── app/
│   ├── main.py              # FastAPI 应用入口
│   ├── api/routes.py         # API 路由
│   ├── models/schemas.py     # 数据模型
│   ├── services/
│   │   ├── oa_client.py      # OA 接口客户端（预留，当前模拟数据）
│   │   └── chat_service.py   # AI 对话服务（流式 + Skills）
│   ├── skills/
│   │   └── leave_skills.py   # Skills 定义与执行
│   └── static/index.html     # 前端对话页面
├── requirements.txt
└── .env.example
```

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 API Key

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 `http://localhost:8000` 即可使用对话界面。

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/chat/stream` | POST | 流式 AI 对话 (SSE) |
| `/api/leave/balance` | POST | 查询假期余额 |
| `/api/leave/request` | POST | 提交请假申请 |

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `OPENAI_API_KEY` | API 密钥 | - |
| `OPENAI_BASE_URL` | API 地址（支持兼容接口） | `https://api.openai.com/v1` |
| `OPENAI_MODEL` | 模型名称 | `gpt-4o` |

## OA 接口对接

当前 OA 接口使用模拟数据，对接真实系统时修改 `app/services/oa_client.py` 中的实现即可。
