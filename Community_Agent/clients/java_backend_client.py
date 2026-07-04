"""Java 后端客户端模块。

职责：
1. 统一封装 Python Agent 对 Java 服务的 HTTP 调用。
2. 提供订单历史、订单草稿、订单确认等业务接口。
"""

from typing import Any, Optional

import httpx

from utils.config_handler import load_java_config

config = load_java_config()


class JavaBackendClient:
    """Java 后端 HTTP 客户端。"""

    # 这里集中管理 Agent 到 Java 服务的调用路径，目的是把业务工具与 HTTP 细节隔离开。

    def __init__(self):
        self.base_url = config["java_backend"]["base_url"]

    def _post(self, path: str, token: str, json_data: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """发送 POST 请求到 Java 后端。"""
        response = httpx.post(
            f"{self.base_url}{path}",
            headers={"token": token},
            json=json_data,
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()

    def _get(self, path: str, token: str) -> dict[str, Any]:
        """发送 GET 请求到 Java 后端。"""
        response = httpx.get(
            f"{self.base_url}{path}",
            headers={"token": token},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()

    def get_user_order_history(self, token: str) -> dict[str, Any]:
        """查询用户历史餐饮订单。"""
        return self._get("/user/ordersCtl/userEatOrder", token)

    def get_food_list(self, token: str) -> dict[str, Any]:
        """查询菜品列表。"""
        # 这里走 Agent 专用内部接口，便于后续在不影响用户公开接口的前提下扩展返回结构。
        return self._get("/user/agent/internal/all-foods", token)

    def save_food_order_draft(self, token: str, draft_data: dict[str, Any]) -> dict[str, Any]:
        """保存待确认的订单草稿。"""
        return self._post("/user/agent/internal/save-food-order-draft", token, draft_data)

    def update_food_order_draft(self, token: str, draft_data: dict[str, Any]) -> dict[str, Any]:
        """修改当前待确认的订单草稿。"""
        return self._post("/user/agent/internal/update-food-order-draft", token, draft_data)

    def get_current_food_order_draft(self, token: str) -> dict[str, Any]:
        """获取当前待确认的订单草稿。"""
        return self._get("/user/agent/internal/current-food-order-draft", token)

    def confirm_food_order(self, token: str, session_id: str) -> dict[str, Any]:
        """确认并创建正式订单。"""
        return self._post(
            "/user/agent/internal/confirm-food-order",
            token,
            {"sessionId": session_id}
        )

    def send_chart_email(self, token: str, email_data: dict[str, Any]) -> dict[str, Any]:
        """发送 Agent 生成的图表和分析信息到用户邮箱。"""
        return self._post("/user/agent/internal/send-chart-email", token, email_data)

    def send_agent_email(self, token: str, email_data: dict[str, Any]) -> dict[str, Any]:
        """发送 Agent 生成的通用文本内容到用户邮箱。优先走通用接口，便于支持订单摘要、报告摘要等非图表场景。"""
        return self._post("/user/agent/internal/send-agent-email", token, email_data)

    def get_weather(self, token: str, city_id: int = 2250) -> dict[str, Any]:
        """查询天气预报，city_id 当前固定使用 2250。"""
        return self._post("/api/weatherCtl/weather?cityId={}".format(city_id), token)
