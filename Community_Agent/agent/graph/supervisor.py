"""Supervisor 路由节点 — 使用轻量 LLM 判断意图并分发到子 Agent。"""

from __future__ import annotations

import json
import re

from langchain_core.messages import HumanMessage, SystemMessage

from models.factory import chat_model
from utils.logger_handler import logger

SUPERVISOR_PROMPT = """你是社区智能助手的路由调度器。根据用户当前问题和最近对话，判断应该交给哪个子 Agent 处理。

可选路由：
- knowledge: 社区公告、通知、社区服务、办事流程、规则、知识库问答
- order: 餐饮下单、菜单查询、订单推荐、修改订单、确认下单（仅限下单操作本身）
- report: 图表生成、可视化、数据分析、发送邮件；若用户要对历史订单/菜品数据做可视化或统计分析，也路由到 report
- weather: 天气查询、天气预报、未来天气

路由优先级规则（重要）：
1. 只要涉及"生成图表/可视化/发送邮件"，必须包含 report，即使数据来源是历史订单
2. 涉及"天气"必须包含 weather
3. order 仅用于"用户明确要下单/点餐/查菜单"等下单操作，不用于数据分析
4. 用户说"根据历史订单数据生成图表"→ 路由 report（不是 order）
5. 涉及多个领域时返回多个路由，顺序按执行依赖关系排列：
   - 若 report 需要用到 weather 的数据（如"把天气也一起发邮件"），则 weather 必须排在 report 之前
   - 若 report 需要用到 knowledge 的数据，则 knowledge 排在 report 之前
   - 无依赖关系时 report 优先

如果无法判断，默认返回 order。

只输出 JSON：
{"routes": ["weather", "report"], "reason": "先查天气，再由 report 汇总生成图表并发送邮件"}
"""


def supervisor_route(query: str, history_summary: str = "") -> list[str]:
    """调用 LLM 判断用户意图，返回路由列表。

    参数说明：
    - query: 用户当前轮问题。
    - history_summary: 最近历史对话的压缩摘要，帮助路由更准确。
    """
    user_content = f"用户问题：{query}"
    if history_summary:
        user_content += f"\n最近对话摘要：{history_summary}"

    try:
        response = chat_model.invoke([
            SystemMessage(content=SUPERVISOR_PROMPT),
            HumanMessage(content=user_content),
        ])
        text = _extract_text(response.content).strip()
        parsed = _parse_json(text)
        if isinstance(parsed, dict) and "routes" in parsed:
            routes = parsed["routes"]
            if isinstance(routes, list) and routes:
                valid = [r for r in routes if r in {"knowledge", "order", "report", "weather"}]
                if valid:
                    logger.info(f"[Supervisor] routes={valid} reason={parsed.get('reason', '')}")
                    return valid
    except Exception as e:
        logger.warning(f"[Supervisor] LLM 路由失败，回退关键词: {e}")

    return _fallback_keyword_route(query)


def _fallback_keyword_route(query: str) -> list[str]:
    """当 LLM 路由失败时，使用关键词规则兜底。

    优先级说明：
    - report / weather / knowledge 优先于 order，
      避免"根据历史订单生成图表"等跨领域请求被误路由到 order。
    - order 仅在查询不涉及图表、邮件、天气、社区知识时才作为主路由，
      否则降为补充路由（仅在用户同时明确提到下单/菜单等才追加）。
    """
    routes = []

    is_report = any(k in query for k in ["图表", "可视化", "柱状图", "折线图", "饼图", "雷达图", "词云", "趋势图", "看板", "邮箱", "邮件", "发送"])
    is_weather = any(k in query for k in ["天气", "气温", "下雨", "晴天", "预报", "温度"])
    is_knowledge = any(k in query for k in ["公告", "通知", "社区服务", "办事流程", "规则", "政策"])
    # order 路由：仅当用户明确提到下单/点餐/菜单相关，且不是把"订单数据"作为分析素材时才追加
    is_order_primary = any(k in query for k in ["下单", "点餐", "确认下单", "修改订单", "查看菜单", "菜单查询"])
    is_order_data_source = any(k in query for k in ["历史订单", "订单数据", "订单记录", "消费记录"])

    if is_report:
        routes.append("report")
    if is_weather:
        routes.append("weather")
    if is_knowledge:
        routes.append("knowledge")
    # 只有在明确下单/点餐操作，且不是把订单当分析数据源时，才加 order
    if is_order_primary and not (is_report or is_weather):
        routes.append("order")
    # 如果只是把历史订单作为数据源（用于图表/分析），不追加 order
    if not routes:
        # 兜底：含"订单"但没命中其他规则，才路由 order
        if any(k in query for k in ["订单", "菜品", "推荐"]):
            routes.append("order")
        else:
            routes.append("order")
    return routes


def _extract_text(content) -> str:
    """从模型返回内容中提取纯文本。"""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            item if isinstance(item, str) else item.get("text", "")
            for item in content
        )
    return str(content) if content else ""


def _parse_json(text: str):
    """尽量从模型输出中解析出 JSON 路由结果。"""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    return None
