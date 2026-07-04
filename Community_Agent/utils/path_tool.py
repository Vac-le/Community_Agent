"""路径工具模块。

职责：
1. 获取项目根目录。
2. 将相对路径统一转换为项目内绝对路径。
"""

import os


def get_project_root():
    """获取当前工程根目录。"""
    current_file = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file)
    project_root = os.path.dirname(current_dir)
    return project_root


def get_abs_path(relative_path):
    """将项目内相对路径转换为绝对路径。"""
    project_root = get_project_root()
    return os.path.join(project_root, relative_path)


if __name__ == "__main__":
    print(get_abs_path("config\\config.txt"))
