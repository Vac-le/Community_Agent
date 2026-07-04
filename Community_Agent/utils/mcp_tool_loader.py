"""MCP 工具加载模块。

职责：
1. 从配置文件读取 MCP Server 信息。
2. 将 MCP Server 暴露的工具转换为 LangChain Agent 可用工具。
3. 在依赖缺失或连接失败时优雅降级，避免影响本地工具链启动。
"""

from __future__ import annotations

import asyncio
import os
import re
import threading
from typing import Any

import yaml
from langchain_core.tools import StructuredTool

from utils.logger_handler import logger
from utils.path_tool import get_abs_path

_ENV_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


def load_mcp_config(config_path: str = get_abs_path("config/mcp.yml"), encoding: str = "utf-8") -> dict[str, Any]:
    """加载 MCP 配置。"""
    if not os.path.exists(config_path):
        return {"enabled": False, "servers": {}}
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader) or {}


def _resolve_env_vars(value: Any) -> Any:
    """递归替换配置中的 ${ENV_NAME} 占位符。"""
    if isinstance(value, str):
        return _ENV_PATTERN.sub(lambda match: os.getenv(match.group(1), ""), value)
    if isinstance(value, list):
        return [_resolve_env_vars(item) for item in value]
    if isinstance(value, dict):
        return {key: _resolve_env_vars(item) for key, item in value.items()}
    return value


def _build_client_config(servers: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """转换为 MultiServerMCPClient 需要的配置结构。"""
    client_config: dict[str, dict[str, Any]] = {}

    for name, server in servers.items():
        if not isinstance(server, dict):
            logger.warning(f"[MCP] 跳过无效服务配置: {name}")
            continue

        if server.get("enabled") is False:
            logger.info(f"[MCP] 服务已禁用: {name}")
            continue

        transport = server.get("transport") or server.get("type") or "sse"
        headers = _resolve_env_vars(server.get("headers", {}))

        if transport == "stdio":
            command = server.get("command")
            if not command:
                logger.warning(f"[MCP] stdio 服务缺少 command: {name}")
                continue
            client_config[name] = {
                "transport": "stdio",
                "command": command,
                "args": _resolve_env_vars(server.get("args", [])),
                "env": _resolve_env_vars(server.get("env", {})),
            }
            continue

        if transport in {"sse", "streamable_http"}:
            url = server.get("url") or server.get("baseUrl")
            if not url:
                logger.warning(f"[MCP] HTTP/SSE 服务缺少 url/baseUrl: {name}")
                continue
            client_config[name] = {
                "transport": transport,
                "url": url,
                "headers": headers,
            }
            continue

        logger.warning(f"[MCP] 不支持的 transport={transport}: {name}")

    return client_config


def _run_coroutine_sync(coro):
    """在同步工具调用中执行异步 MCP 调用。"""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    raise RuntimeError("当前线程已有运行中的事件循环，无法同步执行 MCP 工具")


def _wrap_mcp_tool_for_sync(tool):
    """把 MCP 异步工具包装为同步 StructuredTool，适配当前 Agent stream 调用链。"""
    tool_name = getattr(tool, "name", "")
    description = getattr(tool, "description", "") or tool_name
    args_schema = getattr(tool, "args_schema", None)

    def _sync_func(**kwargs):
        return _run_coroutine_sync(tool.ainvoke(kwargs))

    async def _async_func(**kwargs):
        return await tool.ainvoke(kwargs)

    return StructuredTool.from_function(
        func=_sync_func,
        coroutine=_async_func,
        name=tool_name,
        description=description,
        args_schema=args_schema,
    )


async def _load_mcp_tools_async():
    """异步加载 MCP 工具。"""
    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
    except ImportError:
        logger.warning("[MCP] 未安装 langchain-mcp-adapters，已跳过 MCP 工具加载")
        return []

    config = load_mcp_config()
    if not config.get("enabled", False):
        logger.info("[MCP] MCP 配置未启用")
        return []

    client_config = _build_client_config(config.get("servers", {}) or {})
    if not client_config:
        logger.warning("[MCP] 没有可用的 MCP Server 配置")
        return []

    try:
        client = MultiServerMCPClient(client_config)
        tools = await client.get_tools()
        wrapped_tools = [_wrap_mcp_tool_for_sync(tool) for tool in tools]
        logger.info(f"[MCP] 已加载 MCP 工具数量: {len(wrapped_tools)}")
        return wrapped_tools
    except Exception as e:
        logger.warning(f"[MCP] MCP 工具加载失败，已跳过: {e}")
        return []


def _run_async_in_new_thread(coro):
    """在独立线程中运行协程，避免当前线程已有事件循环时无法 asyncio.run。"""
    result: dict[str, Any] = {"value": None, "error": None}

    def runner():
        try:
            result["value"] = asyncio.run(coro)
        except Exception as e:
            result["error"] = e

    thread = threading.Thread(target=runner, daemon=True)
    thread.start()
    thread.join()

    if result["error"] is not None:
        raise result["error"]
    return result["value"]


def load_mcp_tools_sync():
    """同步加载 MCP 工具，供 Agent 初始化阶段调用。"""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(_load_mcp_tools_async())

    logger.info("[MCP] 当前线程已有运行中的事件循环，切换到独立线程加载 MCP 工具")
    return _run_async_in_new_thread(_load_mcp_tools_async())
