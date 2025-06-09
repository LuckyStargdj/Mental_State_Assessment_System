# @Time    : 2024/1/3 13:54
# @File    : db_login.py
# @FUnc    : 登录界面
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QEvent, QObject
from PyQt5.QtWidgets import QWidget, QLineEdit, QMessageBox
from PyQt5.QtGui import QIcon


from base64 import b64encode,b64decode
from config.config import paths
from db_main import Wgt_Main
from gui.login import Ui_login_form
from utils.data_sqlite import api
import pandas as pd
from configobj import ConfigObj

from utils.utils import definition_MessageBox


class WgtLogin(QWidget,Ui_login_form):

    def __init__(self,parent=None):
        super(WgtLogin, self).__init__(parent)
        self.setupUi(self)

        self.db_main=parent
        self.close_bool=True

        self.setWindowFlags(Qt.FramelessWindowHint) #无边框

        self.show()

        self.user_edit.setPlaceholderText("用户名")
        self.password_edit.setPlaceholderText("密码")
        self.password_edit.setEchoMode(QLineEdit.Password)  # 密码隐藏
        self.checkBox.setChecked(False)

        self.user_configger = ConfigObj(paths['userconfig_path'], encoding='utf-8') #读取config.ini
        #记住密码的判断
        self.data_init()
        self.pb_succeed.clicked.connect(self.login_button) #登录


        self.curr_api = api() #数据库接口函数

        self.pbhide.setMouseTracking(True)
        self.pbhide.setToolTip("窗口最小化")
        self.pbhide.clicked.connect(self.db_main.showMinimized)

        self.pbClose.setMouseTracking(True)
        self.pbClose.setToolTip("关闭程序")
        self.pbClose.clicked.connect(self.close)
        # 将事件过滤器安装到整个窗口
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:  # 捕捉键盘按键事件
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                # 回车键被按下时，触发按钮的点击事件
                self.pb_succeed.click()
                return True

        return QObject.eventFilter(self, obj, event)  # 交由其他控件处理


    def closeEvent(self, event):
        if not self.checkBox.isChecked():
            self.user_configger['account']['username'] = ""
            self.user_configger['account']['password'] = ""
            self.user_configger.write()
        if self.close_bool:
            self.db_main.close()  # 主程序退出


    def data_init(self):
        '''
        从配置文件判断用户之前是否勾选过记住密码
        '''
        if self.user_configger['account']['flag']:
            self.checkBox.setChecked(True)
            self.user_edit.setText(self.user_configger['account']['username'])
            #self.password_edit.setText(b64decode(self.user_configger['account']['password']).decode('utf-8'))

    def login_button(self):
        #判断用户账号密码是否输入正确：
        if not self.user_edit.text() or not self.password_edit.text():
            definition_MessageBox("用户名或者密码还未完全输入")

            return

        base_password = b64encode(self.password_edit.text().encode('utf-8')).decode()

        res,type=self.curr_api.get_users(self.user_edit.text(),base_password)

        if res:
            #判断用户是否勾选记住密码,没有则清除数据
            if self.checkBox.isChecked():
                self.user_configger['account']['flag']="True"
                self.user_configger['account']['username'] = self.user_edit.text()
                self.user_configger['account']['password'] = base_password
            else:
                self.user_configger['account']['username'] = ""
                self.user_configger['account']['password'] = ""
                self.user_configger['account']['flag'] = ""
            self.user_configger['account set']['username'] = self.user_edit.text()
            self.user_configger['account set']['password'] = base_password

            self.user_configger.write()
            #JMsgBox.info('登录成功', close_sec=3)

            #跳转到软件首页
            self.close_bool=False
            self.close()
            self.db_main.hide()

            self.myWin = Wgt_Main()

        else:
            definition_MessageBox("用户名或密码错误")






