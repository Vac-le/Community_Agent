"""子 Agent 工厂 — 创建各领域专用 Agent。"""

from __future__ import annotations

import os

from langchain.agents import create_agent

from agent.tools.agent_tools import (
    confirm_food_order,
    get_pending_food_order,
    prepare_food_order,
    query_all_foods,
    query_user_order_history,
    query_weather_forecast,
    rag_summarize,
    save_user_email_to_memory,
    send_agent_chart_email,
    send_agent_text_email,
    update_food_order_draft,
)
from agent.tools.middleware import log_before_model, monitor_tool
from models.factory import chat_model
from utils.mcp_tool_loader import load_mcp_tools_sync
from utils.prompt_loader import (
    load_knowledge_prompt,
    load_order_prompt,
    load_report_prompt,
    load_weather_prompt,
)

os.environ["LANGSMITH_TRACING"] = os.getenv("LANGSMITH_TRACING", "true")
os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT", "https://apac.api.smith.langchain.com")
if os.getenv("LANGSMITH_API_KEY"):
    os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGSMITH_PROJECT"] = "智慧社区"


def create_knowledge_agent():
    """创建知识问答子 Agent。

    使用场景：社区公告、通知、规则、办事流程、知识库问答。
    """
    return create_agent(
        model=chat_model,
        system_prompt=load_knowledge_prompt(),
        tools=[rag_summarize],
        middleware=[monitor_tool, log_before_model],
    )


def create_order_agent():
    """创建订单业务子 Agent。

    使用场景：菜单、历史订单、推荐菜品、生成草稿、修改草稿、确认下单。
    """
    return create_agent(
        model=chat_model,
        system_prompt=load_order_prompt(),
        tools=[
            query_all_foods,
            query_user_order_history,
            prepare_food_order,
            update_food_order_draft,
            get_pending_food_order,
            confirm_food_order,
        ],
        middleware=[monitor_tool, log_before_model],
    )


def create_report_agent():
    """创建数据分析与图表子 Agent。

    使用场景：历史数据分析、图表生成、邮件发送。
    """
    mcp_tools = load_mcp_tools_sync()
    return create_agent(
        model=chat_model,
        system_prompt=load_report_prompt(),
        tools=[
            query_user_order_history,
            query_all_foods,
            save_user_email_to_memory,
            send_agent_chart_email,
            send_agent_text_email,
        ] + mcp_tools,
        middleware=[monitor_tool, log_before_model],
    )


def create_weather_agent():
    """创建天气子 Agent。

    使用场景：天气查询与天气预报说明。
    """
    return create_agent(
        model=chat_model,
        system_prompt=load_weather_prompt(),
        tools=[query_weather_forecast],
        middleware=[monitor_tool, log_before_model],
    )
