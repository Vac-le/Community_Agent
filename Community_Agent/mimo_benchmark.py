"""MIMO 模型最小测速脚本。

用途：
1. 使用官方 OpenAI SDK 直连 MIMO 做最小耗时测试。
2. 使用 LangChain ChatOpenAI 走同一 base_url 做最小耗时测试。
3. 打印 usage / metadata，帮助判断 token 为 0 是 provider 未返回还是链路未透传。

运行前环境变量：
- 必填：MIMO_API_KEY
- 选填：OPENAI_BASE_URL_MIMO，默认 https://api.xiaomimimo.com/v1
"""

from __future__ import annotations

import json
import os
import time
from typing import Any

from langchain_openai import ChatOpenAI
from openai import OpenAI

DEFAULT_BASE_URL = "https://api.xiaomimimo.com/v1"
DEFAULT_MODEL = "mimo-v2.5-pro"
DEFAULT_QUESTION = "你是谁？请用一句话介绍自己。"


def _env_api_key() -> str:
    api_key = os.getenv("MIMO_API_KEY") or os.getenv("OPENAI_API_KEY_MIMO")
    if not api_key:
        raise RuntimeError("缺少环境变量 MIMO_API_KEY 或 OPENAI_API_KEY_MIMO")
    return api_key


def _base_url() -> str:
    return os.getenv("OPENAI_BASE_URL_MIMO") or os.getenv("OPENAI_BASE_URL") or DEFAULT_BASE_URL


def _pretty(obj: Any) -> str:
    try:
        return json.dumps(obj, ensure_ascii=False, indent=2, default=str)
    except Exception:
        return str(obj)


def official_sdk_test(question: str):
    print("=" * 80)
    print("[1] 官方 OpenAI SDK 直连 MIMO")
    client = OpenAI(api_key=_env_api_key(), base_url=_base_url())

    start = time.perf_counter()
    completion = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": "You are MiMo, an AI assistant developed by Xiaomi."},
            {"role": "user", "content": question},
        ],
        max_completion_tokens=128,
        temperature=0.0,
        top_p=1.0,
        stream=False,
    )
    elapsed = time.perf_counter() - start

    content = ""
    if completion.choices:
        content = completion.choices[0].message.content or ""

    print(f"耗时: {elapsed:.3f}s")
    print(f"模型: {getattr(completion, 'model', None)}")
    print(f"回答: {content}")
    print("usage:")
    print(_pretty(getattr(completion, "usage", None)))
    print("完整响应预览:")
    print(_pretty(completion.model_dump()))



def langchain_test(question: str):
    print("=" * 80)
    print("[2] LangChain ChatOpenAI 直连 MIMO")
    model = ChatOpenAI(
        model=DEFAULT_MODEL,
        api_key=_env_api_key(),
        base_url=_base_url(),
        temperature=0.0,
        max_tokens=128,
    )

    messages = [
        ("system", "You are MiMo, an AI assistant developed by Xiaomi."),
        ("human", question),
    ]

    start = time.perf_counter()
    response = model.invoke(messages)
    elapsed = time.perf_counter() - start

    print(f"耗时: {elapsed:.3f}s")
    print(f"回答: {getattr(response, 'content', '')}")
    print("usage_metadata:")
    print(_pretty(getattr(response, "usage_metadata", None)))
    print("response_metadata:")
    print(_pretty(getattr(response, "response_metadata", None)))
    print("完整 AIMessage 预览:")
    print(_pretty({
        "content": getattr(response, "content", None),
        "usage_metadata": getattr(response, "usage_metadata", None),
        "response_metadata": getattr(response, "response_metadata", None),
        "id": getattr(response, "id", None),
    }))


if __name__ == "__main__":
    question = os.getenv("MIMO_BENCH_QUESTION", DEFAULT_QUESTION)
    print(f"base_url={_base_url()}")
    print(f"question={question}")
    official_sdk_test(question)
    langchain_test(question)
