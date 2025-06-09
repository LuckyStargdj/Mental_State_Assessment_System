import json
import os
import re
import sqlite3

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal, QEvent, QObject, QPoint
from PyQt5.QtGui import QCursor, QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QWidget, QListView, QMessageBox, QCompleter, QComboBox
from datetime import datetime

from config.config import set_file_path
from gui.main_school_login import Ui_school_login
from utils.utils import definition_MessageBox, wait_noblock
import pandas as pd

class School_Login(QWidget, Ui_school_login):
    def __init__(self,db_main):
        super(School_Login, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint) #无边框
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        screen_resolution = self.screen().geometry()
        screen_width = screen_resolution.width()
        screen_height = screen_resolution.height()
        # 设置宽度为屏幕宽度的10/7
        width = int(screen_width * 0.2)
        height = screen_height * 0.3
        self.setGeometry(0, 0, width, height)

        self.center(screen_resolution)

        self.db_main=db_main
        self.setWindowIcon(QIcon(":/icon/res/logo.png"))
        self.setWindowTitle('信息录入')



        self.comboBox_3.setView(QListView()) #性别
        self.comboBox_3.addItems(["男","女"])

        self.comboBox_8.setView(QListView()) #学校
        res,school_list=self.db_main.api.get_school_order_by()
        self.comboBox_8.addItems(school_list)

        school_text = self.comboBox_8.currentText()
        res, grade_list = self.db_main.api.get_grade_order_by(school_text)
        self.comboBox_9.addItems(grade_list)

        grade_text = self.comboBox_9.currentText()
        res, class_list = self.db_main.api.get_class_order_by(school_text,grade_text)
        self.comboBox_10.addItems(class_list)


        self.comboBox_9.setView(QListView())  #年级
        self.comboBox_10.setView(QListView()) #班级

        self.comboBox_8.currentIndexChanged.connect(self.on_combobox_index_changed)
        self.comboBox_9.currentIndexChanged.connect(self.on_combobox_index_changed)
        self.comboBox_10.currentIndexChanged.connect(self.on_combobox_index_changed)

        self.pbhide.setMouseTracking(True)
        self.pbhide.setToolTip("窗口最小化")
        self.pbhide.clicked.connect(self.showMinimized)

        self.pbClose.setMouseTracking(True)
        self.pbClose.setToolTip("关闭程序")
        self.pbClose.clicked.connect(self.close)

        # 将事件过滤器安装到整个窗口
        self.installEventFilter(self)
        self.pushButton_2.clicked.connect(self.confirm_infor) #确认信息
        self.pushButton.clicked.connect(self.Cancel_infor) #取消信息


        self.completer_phone = QCompleter(self)
        self.completer_phone.setCaseSensitivity(False)
        popup = self.completer_phone.popup()
        popup.setResizeMode(QListView.Adjust)
        popup.setFixedHeight(100)
        self.lineEdit.installEventFilter(self)
        self.lineEdit.textChanged.connect(self.showStretchOptions_phone)
        self.lineEdit.setCompleter(self.completer_phone)

        self.lineEdit_3.textChanged.connect(self.on_text_changed)

        self.m_Position = QPoint()
        # 初始化变量
        self.isDragging = False
        self.setupComboBoxEvents()

    def on_text_changed(self):
        """ 实时回删不符合要求的字符 """
        sender = self.sender()
        if sender == self.lineEdit_3:
            pattern = r'[1-9]\d{0,3}'
        else:
            return

        cleaned_text = self.remove_invalid_characters(sender.text(), pattern)
        if sender.text() != cleaned_text:
            sender.setText(cleaned_text)
            sender.setCursorPosition(len(cleaned_text))  # 将光标移动到文本末尾
            return

    def remove_invalid_characters(self, input_str, pattern):
        """ 移除输入字符串中不符合模式的字符 """
        return ''.join(re.findall(pattern, input_str))


    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:  # 捕捉键盘按键事件
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                # 回车键被按下时，触发按钮的点击事件
                self.pushButton_2.click()
                return True

        if obj == self.lineEdit:
            if event.type() == QEvent.FocusOut:
                # 检查焦点是否转移到其他控件
                if self.focusWidget() != self.lineEdit:  # 确认焦点转移到了其他控件
                    res = self.db_main.api.medical_records_phone_data_exists(self.lineEdit.text())
                    if res:
                        self.onCompleterActivated()

        return QObject.eventFilter(self, obj, event)  # 交由其他控件处理

    def onCompleterActivated(self):
        '''
        查询完后的处理
        '''
        input_text = self.lineEdit.text()
        res, data_dict = self.db_main.api.get_medical_records_phone_data(input_text)
        if res:

            self.comboBox_8.setCurrentText(data_dict['school'])
            self.comboBox_9.setCurrentText(data_dict['grade'])
            self.comboBox_10.setCurrentText(data_dict['class'])

            self.lineEdit_2.setText(data_dict['name'])
            self.lineEdit_3.setText(str(data_dict['age']))

            self.comboBox_3.setCurrentText(data_dict['sex'])

    def showStretchOptions_phone(self, text):
        """ 实时回删不符合要求的字符 """
        sender = self.sender()
        if sender == self.lineEdit:
            pattern = r'[0-9]\d{0,9}'
        else:
            return

        cleaned_text = self.remove_invalid_characters(sender.text(), pattern)
        if sender.text() != cleaned_text:
            sender.setText(cleaned_text)
            sender.setCursorPosition(len(cleaned_text))  # 将光标移动到文本末尾
            return

        completion_prefix = self.lineEdit.completer().completionPrefix()

        if len(completion_prefix) < len(text):
            return

        if text.strip() == "":
            pass
        else:
            model = QStandardItemModel()
            self.completer_phone.setModel(model)
            # 添加候选项和图标
            # 数据库
            res, items = self.db_main.api.fuzzy_query_phone_data(text)

            if res:
                for item_text in items:
                    item = QStandardItem(QIcon(":/icon/res/搜索.png"), item_text)
                    model.appendRow(item)


    def center(self,screen):
        # 获取窗口的尺寸
        size = self.geometry()

        # 计算窗口居中的位置
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2 - 40

        # 移动窗口到居中的位置
        self.move(x, y)

    def on_combobox_index_changed(self):
        sender = self.sender()

        if sender == self.comboBox_8:
            current_text = self.comboBox_8.currentText()
            res, grade_list = self.db_main.api.get_grade_order_by(current_text)
            self.comboBox_9.clear()
            self.comboBox_9.addItems(grade_list)

        elif sender == self.comboBox_9:
            comboBox_text = self.comboBox_8.currentText()
            comboBox_text_2 = self.comboBox_9.currentText()
            res, class_list = self.db_main.api.get_class_order_by(comboBox_text,comboBox_text_2)
            self.comboBox_10.clear()
            self.comboBox_10.addItems(class_list)


    def Cancel_infor(self):
        self.close()

    def confirm_infor(self):
        phone = self.lineEdit.text().strip() #学号
        pname = self.lineEdit_2.text().strip() #名字
        age = self.lineEdit_3.text().strip() #年龄
        sex = self.comboBox_3.currentText()
        school = self.comboBox_8.currentText() #学校
        grade = self.comboBox_9.currentText() #年级
        Class = self.comboBox_10.currentText()
        if phone=="" or pname == '' or age == '' or school=="" or  grade=="" or Class =="":
            definition_MessageBox("信息尚未录入完整！")
            return

        res,info=self.db_main.api.insert_medical_records(phone, pname, sex, age,school,grade,Class,0)  # 提交到编号表

        if not res:
            if info=="该学号已存在,请重新输入":
                definition_MessageBox(info)
                return

        res,result=self.db_main.api.get_report_count(phone)
        if res:
            count=result

        with open(set_file_path, 'r', encoding='utf-8') as file:
            settings = json.load(file)

        save_path = settings["save_path"]
        dir_path = os.path.join(save_path, phone)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        self.db_main.phone=phone
        self.db_main.name=pname
        self.db_main.count=count
        self.db_main.bt4_dataRecord.setEnabled(True)

        self.close()

    def setupComboBoxEvents(self):
        # 绑定每个 QComboBox 的 mousePressEvent 到自定义方法
        for comboBox in [self.comboBox_8, self.comboBox_9,self.comboBox_10,self.comboBox_3]:
            comboBox.mousePressEvent = self.createComboBoxMousePressEvent(comboBox)

    def createComboBoxMousePressEvent(self, comboBox):
        def comboBoxMousePressEvent(event):
            # 保持 QComboBox 的默认行为
            QComboBox.mousePressEvent(comboBox, event)
            # 处理窗口拖动的逻辑
            self.handleMousePress(event)

        return comboBoxMousePressEvent

    def mousePressEvent(self, event):
        # 处理窗口拖动的逻辑
        self.handleMousePress(event)

    def handleMousePress(self, event):
        # 鼠标键按下时调用
        if event.button() == Qt.LeftButton:
            if any(comboBox.underMouse() for comboBox in
                   [self.comboBox_8, self.comboBox_9,self.comboBox_10,self.comboBox_3]):
                return

            # 如果点击位置不在 comboBox_COM_3 上，允许拖动窗口
            self.m_Position = event.globalPos() - self.pos()  # 获取鼠标相对窗口的位置
            self.isDragging = True

            event.accept()

    def mouseMoveEvent(self, QMouseEvent):
        if Qt.LeftButton and self.isDragging:
            self.move(QMouseEvent.globalPos() - self.m_Position)  # 更改窗口位置
            QMouseEvent.accept()


    def mouseReleaseEvent(self, QMouseEvent):
        # 鼠标键公开时调用
        self.setCursor(QCursor(Qt.ArrowCursor))
        if QMouseEvent.button() == Qt.LeftButton:
            self.isDragging = False
            QMouseEvent.accept()