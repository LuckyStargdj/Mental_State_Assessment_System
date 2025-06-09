# @Time    : 2025/5/28
# @Author  : 王睿
# @FUnc    : 主界面
import os
import sys
from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon, QPixmap, QBrush, QMovie, QCursor
from db_login import WgtLogin
from utils.logger import handle_exception
from get_path import get_actual_path


class WinMain(QMainWindow):

    def __init__(self):
        super(WinMain, self).__init__()

        self.setWindowOpacity(1)  # 设置窗口透明度
        self.setAttribute(Qt.WA_TranslucentBackground)  # 设置窗口背景透明
        self.setWindowFlag(Qt.FramelessWindowHint)  # 隐藏边框
        icon_path = get_actual_path(":/icon/res/logo.png")
        self.setWindowIcon(QIcon(icon_path))  # 设置任务栏图标为软件图标
        self.setWindowTitle('登录')
        self.resize(800, 800)
        self.setFixedSize(800, 800)
        self.m_flag = None
        # 创建基础透明窗口
        self.base_widget = QtWidgets.QWidget()
        self.base_widget.setObjectName('base_widget')
        self.base_layout = QGridLayout()  # 创建布局

        self.base_widget.setLayout(self.base_layout)
        self.base_widget.setAttribute(Qt.WA_TranslucentBackground)  # 设置窗口背景透明
        self.base_widget.setWindowFlag(Qt.FramelessWindowHint)  # 启动界面无边框

        self.page_main = WgtLogin(self)
        self.base_layout.addWidget(self.page_main)
        self.setCentralWidget(self.base_widget)  # 设置主窗口主部件

    def mousePressEvent(self, event):
        # 鼠标键按下时调用
        if event.button() == Qt.LeftButton:
            self.m_flag = True
            self.m_Position = event.globalPos() - self.pos()  # 获取鼠标相对窗口的位置
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))  # 更改鼠标图标

    def mouseMoveEvent(self, QMouseEvent):
        if Qt.LeftButton and self.m_flag:
            self.move(QMouseEvent.globalPos() - self.m_Position)  # 更改窗口位置
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        # 鼠标键公开时调用

        self.m_flag = False
        self.setCursor(QCursor(Qt.ArrowCursor))


if __name__ == "__main__":
    sys.excepthook = handle_exception
    app = QApplication(sys.argv)
    winMain = WinMain()
    qss_filepath = get_actual_path("db_master_style.qss")
    app.setStyleSheet(open(qss_filepath, "r", encoding='utf-8').read())
    winMain.show()
    sys.exit(app.exec_())
