import os
import sys


def get_actual_path(relative_path):
    """动态获取路径"""
    if hasattr(sys, '_MEIPASS'):
        # 打包后（单文件模式）路径为临时目录
        actual_path = os.path.join(sys._MEIPASS, relative_path)
        actual_path = os.path.normpath(actual_path)
        return actual_path
    # 开发环境路径为当前脚本目录
    actual_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), relative_path)
    actual_path = os.path.normpath(actual_path)
    return actual_path
