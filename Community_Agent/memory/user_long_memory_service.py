"""用户长期记忆服务。"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from models.factory import chat_model
from utils.config_handler import agent_config
from utils.logger_handler import logger
from utils.path_tool import get_abs_path


class UserLongMemoryService:
    """按用户保存长期偏好，并用模型判断 query 是否值得沉淀。"""

    VALID_CATEGORIES = {
        "profile",
        "communication_preferences",
        "food_preferences",
        "community_preferences",
        "avoidances",
        "contact_preferences",
    }

    def __init__(self):
        config = agent_config.get("memory", {}).get("user_long_memory", {})
        self.enabled = config.get("enabled", True)
        self.base_path = get_abs_path(config.get("path", "memory/users"))
        self.max_items_per_category = int(config.get("max_items_per_category", 20))
        self.max_context_chars = int(config.get("max_context_chars", 1600))
        os.makedirs(self.base_path, exist_ok=True)

    def build_memory_context(self, user_id: int | None, community_id: int | None) -> str:
        """构造每次请求注入 prompt 的用户长期记忆。"""
        if not self.enabled or user_id is None or community_id is None:
            return ""
        memory = self.load_user_memory(user_id, community_id)
        lines: list[str] = []
        self._append_category(lines, "用户画像", memory.get("profile", []))
        self._append_category(lines, "交流偏好", memory.get("communication_preferences", []))
        self._append_category(lines, "餐饮偏好", memory.get("food_preferences", []))
        self._append_category(lines, "社区服务关注偏好", memory.get("community_preferences", []))
        self._append_category(lines, "联系方式偏好", memory.get("contact_preferences", []))
        self._append_category(lines, "禁忌与不喜欢", memory.get("avoidances", []))
        if not lines:
            return ""
        text = (
            "【用户长期记忆】\n"
            "以下内容只用于理解用户长期偏好和习惯。若与实时工具结果、社区公告、菜单、订单状态冲突，"
            "必须以实时工具或 RAG 检索结果为准。不能把长期记忆当作实时事实。"
            "如果你仅依据这份长期记忆作答，不要表述成‘系统查询结果’、‘刚刚查到’或‘数据库显示’，而应明确说明这是基于已知长期记忆。\n"
            + "\n".join(lines)
        )
        return self._clip(text, self.max_context_chars)

    def update_from_query(
        self,
        user_id: int | None,
        community_id: int | None,
        query: str,
        answer: str = "",
    ) -> dict[str, Any]:
        """用模型校验 query 是否包含长期记忆，符合要求才保存。"""
        if not self.enabled or user_id is None or community_id is None or not query.strip():
            return {"saved": False, "reason": "memory disabled or missing required fields"}
        memory = self.load_user_memory(user_id, community_id)
        result = self._extract_with_llm(query, answer, memory)
        if not result.get("should_save"):
            return {"saved": False, "reason": result.get("reason", "模型判断无需保存")}
        candidates = self._normalize_candidates(result.get("memories", []))
        if not candidates:
            return {"saved": False, "reason": "没有有效长期记忆候选"}
        changed = self._merge(memory, candidates)
        if not changed:
            return {"saved": False, "reason": "长期记忆已存在"}
        memory["updated_at"] = datetime.now().isoformat(timespec="seconds")
        self.save_user_memory(user_id, community_id, memory)
        return {"saved": True, "count": len(candidates), "memories": candidates}

    def get_user_email(self, user_id: int | None, community_id: int | None) -> str | None:
        """从长期记忆中读取用户邮箱。"""
        if not self.enabled or user_id is None or community_id is None:
            return None
        memory = self.load_user_memory(user_id, community_id)
        for item in reversed(memory.get("contact_preferences", [])):
            content = item.get("content", "") if isinstance(item, dict) else str(item)
            match = self._extract_email(content)
            if match:
                return match
        return None

    def save_user_email(self, user_id: int | None, community_id: int | None, email: str) -> dict[str, Any]:
        """把用户邮箱确定性保存到长期记忆。"""
        if not self.enabled or user_id is None or community_id is None:
            return {"saved": False, "reason": "memory disabled or missing required fields"}
        normalized_email = self._extract_email(email or "")
        if not normalized_email:
            return {"saved": False, "reason": "邮箱格式不正确"}
        memory = self.load_user_memory(user_id, community_id)
        content = f"用户邮箱是 {normalized_email}，发送图表或分析报告邮件时可优先使用该邮箱"
        candidate = {
            "category": "contact_preferences",
            "content": content,
            "scope": "email_delivery",
            "confidence": 1.0,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        changed = self._merge(memory, [candidate])
        if not changed:
            return {"saved": False, "reason": "邮箱已存在", "email": normalized_email}
        memory["updated_at"] = datetime.now().isoformat(timespec="seconds")
        self.save_user_memory(user_id, community_id, memory)
        return {"saved": True, "email": normalized_email}

    def _extract_email(self, text: str) -> str | None:
        match = re.search(r"[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+", str(text or ""))
        return match.group(0) if match else None

    def load_user_memory(self, user_id: int, community_id: int) -> dict[str, Any]:
        path = self._file_path(user_id, community_id)
        default = self._empty_memory(user_id, community_id)
        if not os.path.exists(path):
            return default
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logger.warning(f"[UserMemory] 读取失败，使用空记忆: {e}")
            return default
        if not isinstance(data, dict):
            return default
        default.update(data)
        for category in self.VALID_CATEGORIES:
            if not isinstance(default.get(category), list):
                default[category] = []
        return default

    def save_user_memory(self, user_id: int, community_id: int, memory: dict[str, Any]) -> None:
        path = self._file_path(user_id, community_id)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)

    def _extract_with_llm(self, query: str, answer: str, memory: dict[str, Any]) -> dict[str, Any]:
        prompt = f"""
你是用户长期记忆审查器。判断【当前用户输入】中是否包含值得跨会话保存的用户长期记忆，并提取为严格 JSON。

只允许保存：
- profile：用户长期身份、角色、稳定背景。
- communication_preferences：回答风格、格式、详细程度等长期偏好。
- food_preferences：长期口味、忌口、常点偏好、用餐人数习惯、备注习惯。
- community_preferences：长期关注的社区服务主题。
- contact_preferences：用户明确提供并允许用于接收图表、报告或通知的邮箱等联系方式偏好。
- avoidances：长期不喜欢、不希望、不允许的内容或行为。

严禁保存：当前一次任务、当前订单、当前菜单、当前公告、当前图表需求、工具可实时查询的事实、临时要求、模型推测、完整手机号、详细住址、证件号。
例外：如果用户明确提供邮箱用于后续接收图表、分析报告或通知，可以保存到 contact_preferences。
如果只是查询公告、查看菜单、下单、修改订单、确认下单、生成图表，should_save 必须为 false。
只根据用户输入提取，不要从助手回答中凭空提取。

已有长期记忆：
{self._format_existing(memory)}

当前用户输入：
{query}

助手回答，仅辅助理解：
{self._clip(answer or "", 1000)}

只输出 JSON：
{{"should_save": true, "reason": "原因", "memories": [{{"category": "food_preferences", "content": "用户不吃辣，推荐菜品时应避免辣味菜", "scope": "food_order", "confidence": 0.95}}]}}
如果不保存：{{"should_save": false, "reason": "原因", "memories": []}}
""".strip()
        try:
            response = chat_model.invoke([
                SystemMessage(content="你只输出严格 JSON，不输出 Markdown。"),
                HumanMessage(content=prompt),
            ])
            return self._parse_json(self._extract_text(getattr(response, "content", response)).strip())
        except Exception as e:
            logger.warning(f"[UserMemory] 模型校验长期记忆失败: {e}")
            return {"should_save": False, "reason": str(e), "memories": []}

    def _normalize_candidates(self, candidates: Any) -> list[dict[str, Any]]:
        if not isinstance(candidates, list):
            return []
        output = []
        for item in candidates:
            if not isinstance(item, dict):
                continue
            category = str(item.get("category", "")).strip()
            content = self._sanitize(str(item.get("content", "")).strip())
            confidence = self._safe_float(item.get("confidence", 0.0))
            if category not in self.VALID_CATEGORIES or not content or confidence < 0.7:
                continue
            output.append({
                "category": category,
                "content": content,
                "scope": str(item.get("scope", "all") or "all").strip(),
                "confidence": confidence,
                "created_at": datetime.now().isoformat(timespec="seconds"),
            })
        return output

    def _merge(self, memory: dict[str, Any], candidates: list[dict[str, Any]]) -> bool:
        changed = False
        for item in candidates:
            items = memory.setdefault(item["category"], [])
            if not isinstance(items, list):
                items = []
                memory[item["category"]] = items
            if self._exists(item["content"], items):
                continue
            items.append({
                "content": item["content"],
                "scope": item["scope"],
                "confidence": item["confidence"],
                "created_at": item["created_at"],
            })
            memory[item["category"]] = items[-self.max_items_per_category:]
            changed = True
        return changed

    def _append_category(self, lines: list[str], title: str, items: Any) -> None:
        if not isinstance(items, list) or not items:
            return
        lines.append(f"{title}：")
        for item in items[-self.max_items_per_category:]:
            content = item.get("content", "") if isinstance(item, dict) else str(item)
            scope = item.get("scope", "all") if isinstance(item, dict) else "all"
            if str(content).strip():
                lines.append(f"- [{scope}] {str(content).strip()}")

    def _format_existing(self, memory: dict[str, Any]) -> str:
        lines = []
        for category in sorted(self.VALID_CATEGORIES):
            items = memory.get(category, [])
            if not isinstance(items, list):
                continue
            for item in items[-20:]:
                content = item.get("content", "") if isinstance(item, dict) else str(item)
                if content:
                    lines.append(f"- {category}: {content}")
        return "\n".join(lines) if lines else "无"

    def _empty_memory(self, user_id: int, community_id: int) -> dict[str, Any]:
        return {
            "user_id": user_id,
            "community_id": community_id,
            "profile": [],
            "communication_preferences": [],
            "food_preferences": [],
            "community_preferences": [],
            "avoidances": [],
            "contact_preferences": [],
            "updated_at": "",
        }

    def _file_path(self, user_id: int, community_id: int) -> str:
        return os.path.join(self.base_path, f"community_{self._safe(community_id)}_user_{self._safe(user_id)}.json")

    def _safe(self, value: Any) -> str:
        return re.sub(r"[^0-9A-Za-z_-]", "_", str(value))

    def _exists(self, content: str, items: list[Any]) -> bool:
        target = self._normalize_text(content)
        for item in items:
            existing = item.get("content", "") if isinstance(item, dict) else str(item)
            if self._normalize_text(existing) == target:
                return True
        return False

    def _parse_json(self, text: str) -> dict[str, Any]:
        try:
            data = json.loads(text)
            return data if isinstance(data, dict) else {"should_save": False, "reason": "非对象 JSON", "memories": []}
        except json.JSONDecodeError:
            match = re.search(r"\{[\s\S]*\}", text)
            if not match:
                return {"should_save": False, "reason": "未输出 JSON", "memories": []}
            try:
                data = json.loads(match.group(0))
                return data if isinstance(data, dict) else {"should_save": False, "reason": "非对象 JSON", "memories": []}
            except json.JSONDecodeError as e:
                return {"should_save": False, "reason": f"JSON 解析失败: {e}", "memories": []}

    def _extract_text(self, content: Any) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "".join(str(item.get("text", "")) if isinstance(item, dict) else str(item) for item in content)
        return str(content) if content is not None else ""

    def _sanitize(self, content: str) -> str:
        content = re.sub(r"\b1[3-9]\d{9}\b", "[手机号已省略]", content)
        content = re.sub(r"\d{15,18}[0-9Xx]?", "[敏感证件号已省略]", content)
        return self._clip(content, 180)

    def _normalize_text(self, text: str) -> str:
        return re.sub(r"\s+", "", str(text).strip().lower())

    def _safe_float(self, value: Any) -> float:
        try:
            return float(value)
        except Exception:
            return 0.0

    def _clip(self, text: str, max_chars: int) -> str:
        return text if len(text) <= max_chars else text[:max_chars] + "..."
