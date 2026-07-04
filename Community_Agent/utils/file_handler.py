"""文件与知识源处理模块。

职责：
1. 计算知识文件 MD5，用于去重。
2. 按后缀筛选可加载的知识文件。
3. 提供 TXT / PDF 文档加载能力。
"""

import hashlib
import os

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document

from utils.logger_handler import logger


def get_file_md5_hex(file_path: str) -> str:
    """计算文件 MD5，用于判断知识文件是否重复入库。"""
    if not os.path.exists(file_path):
        logger.error("[md5计算] 文件不存在")
        return ""

    if not os.path.isfile(file_path):
        logger.error(f"[md5计算] 路径不是文件: {file_path}")
        return ""

    md5_obj = hashlib.md5()
    chunk_size = 4096
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                md5_obj.update(chunk)
        return md5_obj.hexdigest()
    except Exception as e:
        logger.error(f"计算文件 {file_path} md5 失败: {str(e)}")
        return ""


def listdir_with_allowed_type(path: str, allowed_types: tuple[str]):
    """返回指定目录下符合后缀条件的文件列表。"""
    files = []

    if not os.path.isdir(path):
        logger.error(f"[listdir_with_allowed_type] {path} 不是文件夹")
        return tuple(files)

    for file_name in os.listdir(path):
        if file_name.endswith(allowed_types):
            files.append(os.path.join(path, file_name))

    return tuple(files)


def pdf_loader(file_path: str, password=None) -> list[Document]:
    """加载 PDF 文档。"""
    return PyPDFLoader(file_path, password).load()


def txt_loader(file_path: str) -> list[Document]:
    """加载 TXT 文档。"""
    return TextLoader(file_path, encoding="utf-8").load()
