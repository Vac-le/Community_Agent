"""项目入口模块。

职责：
1. 创建 FastAPI 应用。
2. 挂载 Agent 路由。
3. 提供健康检查接口，便于部署后探活。
"""

from fastapi import FastAPI

from agent.api.agent_api import router

# 创建 FastAPI 应用。
app = FastAPI(
    title="Agent RAG Service",
    description="Community_Agent 社区智能助手 Python 流式服务",
    version="1.0.0"
)

# 注册 Agent 路由。
app.include_router(router)


@app.get("/health")
def health():
    """健康检查接口。"""
    return {
        "code": 0,
        "msg": "ok"
    }
