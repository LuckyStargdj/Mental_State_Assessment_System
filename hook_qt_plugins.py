import os
import sys

# 设置 QT_PLUGIN_PATH 确保 Qt 能找到 platforms 目录
plugin_path = os.path.join(sys._MEIPASS, 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path
