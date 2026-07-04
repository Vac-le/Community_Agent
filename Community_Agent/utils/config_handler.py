"""配置加载模块。

职责：
1. 统一加载项目中的 YAML 配置文件。
2. 暴露各类配置对象，供其他模块直接使用。
"""

import yaml

from utils.path_tool import get_abs_path


def load_rag_config(config_path: str = get_abs_path("config/rag.yml"), encoding="utf-8"):
    """加载 RAG 相关配置。"""
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def load_vector_store_config(config_path: str = get_abs_path("config/vector_store.yml"), encoding="utf-8"):
    """加载向量库配置。"""
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def load_prompt_config(config_path: str = get_abs_path("config/prompt.yml"), encoding="utf-8"):
    """加载提示词配置。"""
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def load_agent_config(config_path: str = get_abs_path("config/agent.yml"), encoding="utf-8"):
    """加载 Agent 配置。"""
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def load_java_config(config_path: str = get_abs_path("config/java_config.yml"), encoding="utf-8"):
    """加载 Java 后端配置。"""
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


rag_config = load_rag_config()
vector_store_config = load_vector_store_config()
prompt_config = load_prompt_config()
agent_config = load_agent_config()
java_config = load_java_config()


if __name__ == "__main__":
    print(agent_config["chat_model_name"])
