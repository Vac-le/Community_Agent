"""提示词加载模块。

职责：
1. 根据配置读取各 Agent 系统提示词。
2. 读取 RAG 总结提示词。
"""

from utils.config_handler import prompt_config
from utils.logger_handler import logger
from utils.path_tool import get_abs_path


def _load_prompt_by_config_key(config_key: str, log_name: str) -> str:
    try:
        prompt_path = get_abs_path(prompt_config[config_key])
    except KeyError as e:
        logger.error(f"[{log_name}] 缺少 {config_key} 配置项")
        raise e
    try:
        return open(prompt_path, "r", encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[{log_name}] 解析提示词出错")
        raise e


def load_knowledge_prompt():
    """加载知识问答 Agent 系统提示词。"""
    return _load_prompt_by_config_key("knowledge_prompt_path", "load_knowledge_prompt")


def load_order_prompt():
    """加载订单 Agent 系统提示词。"""
    return _load_prompt_by_config_key("order_prompt_path", "load_order_prompt")


def load_report_prompt():
    """加载报告 Agent 系统提示词。"""
    return _load_prompt_by_config_key("report_prompt_path", "load_report_prompt")


def load_weather_prompt():
    """加载天气 Agent 系统提示词。"""
    return _load_prompt_by_config_key("weather_prompt_path", "load_weather_prompt")


def load_rag_prompt():
    """加载 RAG 总结提示词。"""
    return _load_prompt_by_config_key("rag_summarize_prompt_path", "load_rag_prompt")
