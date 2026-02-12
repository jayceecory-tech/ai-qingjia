"""示例Skills - 展示如何创建自定义Skills"""

import json
import random
from datetime import datetime, timedelta
from typing import Optional, List
import aiohttp
import asyncio

# ==================== 示例1：计算器Skill ====================

async def calculate_expression(expression: str) -> str:
    """计算数学表达式
    
    支持加减乘除、幂运算等基本数学运算
    注意：实际项目中应使用更安全的eval替代方案
    """
    try:
        # 安全限制：只允许数学运算
        allowed_chars = set("0123456789+-*/.() ")
        if not all(c in allowed_chars for c in expression):
            return json.dumps({
                "error": "表达式包含非法字符",
                "allowed_chars": list(allowed_chars)
            }, ensure_ascii=False)
        
        # 使用eval计算（生产环境应使用更安全的方法）
        result = eval(expression)
        
        return json.dumps({
            "expression": expression,
            "result": result,
            "type": type(result).__name__
        }, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({
            "error": "计算失败",
            "expression": expression,
            "message": str(e)
        }, ensure_ascii=False)


CALCULATOR_SKILL = {
    "type": "function",
    "function": {
        "name": "calculate_expression",
        "description": "计算数学表达式，支持加减乘除、幂运算等基本运算",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "数学表达式，例如：2+3*4、(10-5)/2、2**3"
                }
            },
            "required": ["expression"]
        }
    }
}


# ==================== 示例2：时间管理Skill ====================

async def schedule_reminder(
    task: str,
    due_date: str,
    due_time: Optional[str] = None,
    priority: str = "medium"
) -> str:
    """安排提醒任务
    
    创建一个提醒任务，可以设置截止日期、时间和优先级
    """
    # 验证优先级
    valid_priorities = ["low", "medium", "high", "urgent"]
    if priority not in valid_priorities:
        return json.dumps({
            "error": "无效的优先级",
            "valid_priorities": valid_priorities
        }, ensure_ascii=False)
    
    # 生成任务ID
    task_id = f"TASK-{random.randint(1000, 9999)}"
    
    # 创建提醒记录
    reminder = {
        "task_id": task_id,
        "task": task,
        "due_date": due_date,
        "due_time": due_time or "23:59",
        "priority": priority,
        "created_at": datetime.now().isoformat(),
        "status": "pending"
    }
    
    # 这里可以保存到数据库
    # await save_to_database(reminder)
    
    return json.dumps({
        "success": True,
        "message": f"提醒任务已创建：{task}",
        "task_id": task_id,
        "reminder": reminder,
        "next_action": f"请在{due_date} {due_time or '23:59'}前完成"
    }, ensure_ascii=False)


async def list_reminders(
    status: Optional[str] = None,
    priority: Optional[str] = None
) -> str:
    """列出提醒任务
    
    可以根据状态和优先级筛选任务
    """
    # 模拟从数据库获取数据
    # 实际项目中应该从数据库查询
    sample_reminders = [
        {
            "task_id": "TASK-1001",
            "task": "完成项目报告",
            "due_date": "2024-01-15",
            "due_time": "18:00",
            "priority": "high",
            "status": "pending"
        },
        {
            "task_id": "TASK-1002",
            "task": "团队会议",
            "due_date": "2024-01-10",
            "due_time": "14:00",
            "priority": "medium",
            "status": "completed"
        }
    ]
    
    # 筛选任务
    filtered_reminders = sample_reminders
    
    if status:
        filtered_reminders = [r for r in filtered_reminders if r["status"] == status]
    
    if priority:
        filtered_reminders = [r for r in filtered_reminders if r["priority"] == priority]
    
    return json.dumps({
        "count": len(filtered_reminders),
        "filters": {
            "status": status,
            "priority": priority
        },
        "reminders": filtered_reminders
    }, ensure_ascii=False)


TIME_MANAGEMENT_SKILLS = [
    {
        "type": "function",
        "function": {
            "name": "schedule_reminder",
            "description": "安排提醒任务，可以设置任务内容、截止日期、时间和优先级",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "任务内容描述"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "截止日期，格式：YYYY-MM-DD"
                    },
                    "due_time": {
                        "type": "string",
                        "description": "截止时间，格式：HH:MM，24小时制，可选"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "urgent"],
                        "description": "任务优先级，默认：medium"
                    }
                },
                "required": ["task", "due_date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_reminders",
            "description": "列出提醒任务，可以根据状态和优先级筛选",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed", "cancelled"],
                        "description": "任务状态筛选，可选"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "urgent"],
                        "description": "任务优先级筛选，可选"
                    }
                },
                "required": []
            }
        }
    }
]


# ==================== 示例3：外部API集成Skill ====================

async def get_joke(category: Optional[str] = None) -> str:
    """获取笑话
    
    从公开API获取笑话，可以按类别筛选
    """
    categories = ["programming", "general", "knock-knock"]
    
    if category and category not in categories:
        return json.dumps({
            "error": "无效的笑话类别",
            "available_categories": categories
        }, ensure_ascii=False)
    
    try:
        # 使用公开的笑话API
        url = "https://v2.jokeapi.dev/joke/"
        if category:
            url += f"{category}"
        else:
            url += "Any"
        
        url += "?type=single"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("error", False):
                        return json.dumps({
                            "error": "API返回错误",
                            "message": data.get("message", "未知错误")
                        }, ensure_ascii=False)
                    
                    return json.dumps({
                        "category": data.get("category", "unknown"),
                        "joke": data.get("joke", "No joke found"),
                        "flags": data.get("flags", {}),
                        "safe": data.get("safe", True)
                    }, ensure_ascii=False)
                else:
                    return json.dumps({
                        "error": "API请求失败",
                        "status": response.status,
                        "message": "无法获取笑话"
                    }, ensure_ascii=False)
                    
    except asyncio.TimeoutError:
        return json.dumps({
            "error": "请求超时",
            "message": "笑话API响应超时"
        }, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({
            "error": "获取笑话失败",
            "message": str(e)
        }, ensure_ascii=False)


async def get_fact(topic: Optional[str] = None) -> str:
    """获取有趣的事实
    
    获取关于各种主题的有趣事实
    """
    topics = ["history", "science", "technology", "nature", "space"]
    
    if topic and topic not in topics:
        return json.dumps({
            "error": "无效的主题",
            "available_topics": topics
        }, ensure_ascii=False)
    
    # 模拟事实数据（实际项目可以使用API）
    facts = {
        "history": "古埃及人是最早使用牙膏的文明之一，他们的牙膏由牛蹄灰、烧焦的蛋壳和浮石粉制成。",
        "science": "人的大脑在思考时消耗的能量相当于一个20瓦的灯泡。",
        "technology": "第一个计算机病毒是在1983年创建的，名为'Elk Cloner'，它感染了Apple II系统。",
        "nature": "一棵成熟的橡树每年可以生产约10万颗橡子。",
        "space": "如果你在太空中哭泣，眼泪不会流下来，而是会形成一个小球漂浮在你面前。"
    }
    
    if topic:
        fact = facts.get(topic, "没有找到关于该主题的事实")
    else:
        # 随机选择一个主题
        random_topic = random.choice(list(facts.keys()))
        fact = facts[random_topic]
        topic = random_topic
    
    return json.dumps({
        "topic": topic,
        "fact": fact,
        "source": "知识库",
        "timestamp": datetime.now().isoformat()
    }, ensure_ascii=False)


EXTERNAL_API_SKILLS = [
    {
        "type": "function",
        "function": {
            "name": "get_joke",
            "description": "获取笑话，可以按类别筛选（编程、一般、敲门笑话等）",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["programming", "general", "knock-knock"],
                        "description": "笑话类别，可选"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_fact",
            "description": "获取有趣的事实，可以按主题筛选（历史、科学、技术、自然、太空等）",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "enum": ["history", "science", "technology", "nature", "space"],
                        "description": "事实主题，可选"
                    }
                },
                "required": []
            }
        }
    }
]


# ==================== 示例4：工作流Skill ====================

async def plan_workday(
    tasks: List[str],
    work_hours: int = 8,
    break_time: int = 60
) -> str:
    """规划工作日
    
    根据任务列表和工作时间，智能规划工作日安排
    """
    if not tasks:
        return json.dumps({
            "error": "任务列表不能为空",
            "message": "请提供至少一个任务"
        }, ensure_ascii=False)
    
    if work_hours <= 0 or work_hours > 24:
        return json.dumps({
            "error": "无效的工作时间",
            "message": "工作时间应在1-24小时之间"
        }, ensure_ascii=False)
    
    # 计算每个任务的时间分配
    total_tasks = len(tasks)
    task_duration = (work_hours * 60 - break_time) / total_tasks
    
    # 生成时间表
    schedule = []
    start_time = datetime.now().replace(hour=9, minute=0, second=0)  # 9:00开始
    
    for i, task in enumerate(tasks):
        task_start = start_time + timedelta(minutes=i * task_duration)
        task_end = task_start + timedelta(minutes=task_duration)
        
        schedule.append({
            "task_number": i + 1,
            "task": task,
            "start_time": task_start.strftime("%H:%M"),
            "end_time": task_end.strftime("%H:%M"),
            "duration_minutes": task_duration
        })
    
    # 添加休息时间
    break_start = start_time + timedelta(minutes=(total_tasks * task_duration) / 2)
    schedule.append({
        "task_number": "休息",
        "task": "休息时间",
        "start_time": break_start.strftime("%H:%M"),
        "end_time": (break_start + timedelta(minutes=break_time)).strftime("%H:%M"),
        "duration_minutes": break_time
    })
    
    return json.dumps({
        "workday_plan": {
            "total_tasks": total_tasks,
            "work_hours": work_hours,
            "break_time_minutes": break_time,
            "task_duration_minutes": task_duration,
            "schedule": schedule
        },
        "recommendations": [
            "按照时间表执行任务",
            "保持专注，避免分心",
            "休息时间充分放松"
        ]
    }, ensure_ascii=False)


WORKFLOW_SKILLS = [
    {
        "type": "function",
        "function": {
            "name": "plan_workday",
            "description": "规划工作日安排，根据任务列表和工作时间智能分配时间",
            "parameters": {
                "type": "object",
                "properties": {
                    "tasks": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "任务列表，每个元素是一个任务描述"
                    },
                    "work_hours": {
                        "type": "integer",
                        "description": "工作时间（小时），默认：8"
                    },
                    "break_time": {
                        "type": "integer",
                        "description": "休息时间（分钟），默认：60"
                    }
                },
                "required": ["tasks"]
            }
        }
    }
]


# ==================== 所有Skills汇总 ====================

# 所有示例Skills
EXAMPLE_SKILLS = [
    CALCULATOR_SKILL,
    *TIME_MANAGEMENT_SKILLS,
    *EXTERNAL_API_SKILLS,
    *WORKFLOW_SKILLS
]

# Skills名称到函数的映射
SKILL_FUNCTIONS = {
    "calculate_expression": calculate_expression,
    "schedule_reminder": schedule_reminder,
    "list_reminders": list_reminders,
    "get_joke": get_joke,
    "get_fact": get_fact,
    "plan_workday": plan_workday
}


async def execute_example_skill(name: str, arguments: str) -> str:
    """执行示例skill"""
    if name not in SKILL_FUNCTIONS:
        return json.dumps({
            "error": f"未知的skill: {name}",
            "available_skills": list(SKILL_FUNCTIONS.keys())
        }, ensure_ascii=False)
    
    try:
        args = json.loads(arguments)
        func = SKILL_FUNCTIONS[name]
        
        # 根据函数签名调用
        import inspect
        sig = inspect.signature(func)
        params = sig.parameters
        
        # 准备参数
        kwargs = {}
        for param_name in params:
            if param_name in args:
                kwargs[param_name] = args[param_name]
        
        # 调用函数
        result = await func(**kwargs)
        return result
        
    except json.JSONDecodeError:
        return json.dumps({
            "error": "参数格式错误",
            "message": "参数必须是有效的JSON格式"
        }, ensure_ascii=False)
        
    except TypeError as e:
        return json.dumps({
            "error": "参数错误",
            "message": str(e),
            "expected_parameters": list(params.keys())
        }, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({
            "error": "执行失败",
            "message": str(e),
            "skill": name
        }, ensure_ascii=False)


# ==================== 使用说明 ====================

"""
如何使用这些示例Skills：

1. 导入到主skills文件：
   from app.skills.example_skills import EXAMPLE_SKILLS, execute_example_skill

2. 添加到LEAVE_SKILLS列表：
   LEAVE_SKILLS.extend(EXAMPLE_SKILLS)

3. 在execute_skill函数中添加处理：
   if name in SKILL_FUNCTIONS:
       return await execute_example_skill(name, arguments)

4. 测试skill：
   curl -X POST http://localhost:8000/api/chat/stream \
     -H "Content-Type: application/json" \
     -d '{
       "message": "帮我计算一下(10+5)*2等于多少？",
       "history": [],
       "employee_id": "EMP001"
     }'
"""

if __name__ == "__main__":
    # 测试代码
    async def test_skills():
        """测试所有skills"""
        test_cases = [
            ("calculate_expression", '{"expression": "(10+5)*2"}'),
            ("schedule_reminder", '{"task": "测试任务", "due_date": "2024-01-20"}'),
            ("list_reminders", '{}'),
            ("get_joke", '{"category": "programming"}'),
            ("get_fact", '{"topic": "science"}'),
            ("plan_workday", '{"tasks": ["写代码