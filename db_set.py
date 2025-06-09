import json
import os
import shutil
import sqlite3
from base64 import b64encode, b64decode

from utils.logger import logger


from PyQt5.QtCore import Qt, QEvent, QObject, QPoint
from PyQt5.QtGui import QMouseEvent, QIcon, QFont, QColor, QCursor
from PyQt5.QtWidgets import QWidget, QAbstractItemView, QHeaderView, QTableView, QTableWidgetItem, QLabel, QHBoxLayout, \
    QMessageBox, QFileDialog, QDesktopWidget, QVBoxLayout, QProgressBar, QPushButton, QProgressDialog, QDialog, \
    QTableWidget, QLineEdit
from PyQt5 import QtGui, QtCore

from config.config import set_file_path, paths
from gui.set import Ui_set_form
from gui.template import Ui_template_form
from utils.data_sqlite import api
from utils.utils import definition_MessageBox, select_definition_MessageBox, wait_noblock

from configobj import ConfigObj
import pandas as pd
class Set_Info(QWidget, Ui_set_form):
    def __init__(self,api):
        super(Set_Info, self).__init__()
        self.setupUi(self)

        screen_resolution = self.screen().geometry()
        screen_width = screen_resolution.width()
        screen_height = screen_resolution.height()

        width = int(screen_width * 0.4)
        height = screen_height * 0.7
        self.setGeometry(0, 0, width, height)

        self.center()
        self.setWindowFlags(Qt.FramelessWindowHint)  # 无边框
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowIcon(QIcon(":/icon/res/logo.png"))
        self.setWindowTitle('设置')

        self.pbhide_5.setMouseTracking(True)
        self.pbhide_5.setToolTip("窗口最小化")
        self.pbhide_5.clicked.connect(self.showMinimized)

        self.pbClose_5.setMouseTracking(True)
        self.pbClose_5.setToolTip("关闭程序")
        self.pbClose_5.clicked.connect(self.close)

        self.api=api
        self.Row = ""
        self.row = ""

        self.Row_csv = ""
        self.row_csv = ""

        with open(set_file_path, 'r', encoding='utf-8') as file:
            self.settings = json.load(file)

        self.user_label.setToolTip("用户名")
        self.password_label.setToolTip("密码")
        self.user_configger = ConfigObj(paths['userconfig_path'], encoding='utf-8')  # 读取config.ini
        self.manage_id = None  # 用户id
        self.init_account()  # 初始化获取账号
        self.show_user_edit.setFocusPolicy(QtCore.Qt.NoFocus)  # 不可编辑
        self.show_pw_edit.setFocusPolicy(QtCore.Qt.NoFocus)
        self.show_pw_edit.setEchoMode(QLineEdit.Password)  # 默认显示星号
        self.re_pw_edit.setEchoMode(QLineEdit.Password)
        self.new_pw_edit.setEchoMode(QLineEdit.Password)
        self.show_pw_icon_bl = True  # 是否显示密码icon参数
        self.pushButton.clicked.connect(self.show_password)  # 显示密码
        self.pushButton_2.clicked.connect(self.modify_password)  # 修改密码

        self.frame_10.hide()
        self.load_args()
        self.__init_table()  # 初始化表格
        self.update_template_table()  # 获取用户数据表信息
        self.listWidget_2.itemClicked.connect(self.change_page)
        self.pushButton_3.clicked.connect(self.add_template)
        self.path_button.clicked.connect(self.select_path)
        self.data_path.textChanged.connect(self.update_settings)

        #导入csv文件
        self.path_button_3.clicked.connect(self.export_csv_file)

        #导入csv文件夹
        self.path_button_4.clicked.connect(self.export_csv_dir)
        self.init_table()
        self.update_csv_table()  # 获取添加csv表的基本信息

        font = QFont("微软雅黑", 12)  # 设置字体为 Arial，字号为 12
        self.data_path.setFont(font)

        self.listWidget_2.setFocus()
        self.listWidget_2.setCurrentRow(0)


        self.m_Position = QPoint()

    def init_account(self):
        if self.user_configger['account set']['password']:
            self.show_user_edit.setText(self.user_configger['account set']['username'])
            self.show_pw_edit.setText(b64decode(self.user_configger['account set']['password']).decode('utf-8'))
        #获取用户类型和用户id  管理员用户id默认为0
            res,list_info=self.api.get_user_type_id(self.user_configger['account set']['username'])
            if res:
                self.manage_id=list_info[1]

    def modify_password(self):
        if not self.new_pw_edit.text() or not self.re_pw_edit.text():
            definition_MessageBox("密码还未完全输入")

            return

        if self.new_pw_edit.text() != self.re_pw_edit.text():
            definition_MessageBox("两次密码输入不一样")

            return

        user = self.show_user_edit.text()
        new_password = b64encode(self.new_pw_edit.text().encode('utf-8')).decode()
        #把修改的密码提交到数据库
        if self.api.update_user_password(user, new_password):
            self.show_pw_edit.setText(self.new_pw_edit.text()) #实时更新
            self.user_configger['account']['password'] = ""
            self.user_configger['account set']['password'] = new_password
            self.new_pw_edit.setText("")
            self.re_pw_edit.setText("")
            self.user_configger.write()
            definition_MessageBox("修改完成")


    def show_password(self):
        if self.show_pw_icon_bl:
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(r":/icon/res/眼睛显示保护图标.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.pushButton.setIcon(icon)
            self.show_pw_edit.setEchoMode(QLineEdit.Normal) #正常

            self.show_pw_icon_bl=False
        else:
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(r':/icon/res/闭眼.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.pushButton.setIcon(icon)
            self.show_pw_edit.setEchoMode(QLineEdit.Password)

            self.show_pw_icon_bl = True
        self.pushButton.setIconSize(QtCore.QSize(25, 25))
        self.pushButton.setAutoDefault(False)



    def init_table(self):
        '''
                初始化表格
                '''
        self.tableWidget.setStyleSheet("QWidget{font-size:9;}")
        self.tableWidget.clear()
        self.tableWidget.setShowGrid(False)
        self.tableWidget.setRowCount(0)

        self.tableWidget.verticalHeader().setHidden(True)  # 去掉序号列
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)  # 用户设置
        self.tableWidget.horizontalHeader().setStretchLastSection(True)  # 最后一列自适应
        self.tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)  # 设置只能选中一行
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)  # 设置只有行选中
        self.tableWidget.setEditTriggers(QTableView.NoEditTriggers)  # 不可编辑
        self.tableWidget.setFocusPolicy(Qt.NoFocus)

        head_list = ["序号", '文件名', '操作']
        head_list_cnt = len(head_list)
        self.tableWidget.setColumnCount(head_list_cnt)
        self.tableWidget.setHorizontalHeaderLabels(head_list)

        self.tableWidget.setMouseTracking(True)  # 启用鼠标追踪
        self.tableWidget.mouseMoveEvent = self.table_mouse_csv  # 绑定鼠标移动事件
        self.tableWidget.mousePressEvent = self.table_press_csv  # 绑定鼠标点击事件

        # 按比例设置宽度
        header = self.tableWidget.horizontalHeader()
        self.tableWidget.setColumnWidth(0, 60)
        header.setSectionResizeMode(0, QHeaderView.Fixed)

        for i in range(1, head_list_cnt):
            header.setSectionResizeMode(i, QHeaderView.Stretch)

    def table_press_csv(self, event):
        item = self.tableWidget.itemAt(event.pos())
        if item is not None:
            row = item.row()
            self.Row_csv = row
            self.tableWidget.clearSelection()  # 取消选中状态
            self.clearHoverEffects_csv()
            if item is not None:
                self.tableWidget.setCurrentCell(row, 0)
                self.tableWidget.itemClicked.emit(item)  # 手动触发itemClicked信号

        super().mousePressEvent(event)

    def table_mouse_csv(self, event):
        item = self.tableWidget.itemAt(event.pos())

        if item is not None:
            row = item.row()
            self.row_csv = row

            self.clearHoverEffects_csv()  # 清除之前的悬停效果

            for col in range(self.tableWidget.columnCount()):
                if col == 2:
                    self.tableWidget.cellWidget(row, col).setStyleSheet(
                        "background-color: rgb(217, 235, 249);color:rgb(0, 0, 255;)")
                    continue
                self.tableWidget.item(row, col).setBackground(QColor(217, 235, 249))  # 设置当前行的悬停效果

        super().mouseMoveEvent(event)

    def clearHoverEffects_csv(self):
        for row_index in range(self.tableWidget.rowCount()):
            if self.Row_csv == row_index:
                continue
            for col in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row_index, col)
                cell_widget = self.tableWidget.cellWidget(row_index, col)
                if item is None and cell_widget is None:
                    break

                if col == 2:
                    self.tableWidget.cellWidget(row_index, col).setStyleSheet(
                        "background-color: rgb(255,255,255);color:rgb(0, 0, 255);")
                    continue

                self.tableWidget.item(row_index, col).setBackground(QColor(255, 255, 255))  # 恢复原始背景色


    def export_csv_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_filter = "CSV 和 Excel 文件 (*.csv *.xls *.xlsx)"
        file_path, _ = QFileDialog.getOpenFileName(self, "选择 CSV 文件", "", file_filter, options=options)
        if file_path:
            destination_dir = os.path.join(os.getcwd(), "csv_file")
            if not os.path.exists(destination_dir):
                os.mkdir(destination_dir)

            file_name = os.path.basename(file_path)  # 获取目标文件路径
            destination_path = os.path.join(destination_dir, file_name)

            self.data_path_3.setText(file_path)
            res=self.api.insert_csv(file_name,destination_path)
            if not res:
                definition_MessageBox("此文件已上传过")
                return

            self.progress_dialog = CustomProgressDialog("传输数据中...", "取消", 0, 100, self)
            self.progress_dialog.show()
            wait_noblock(0.2)
            # 复制选中的文件到目标文件夹
            shutil.copy(file_path, destination_path)

            #把csv表里面的数据加到
            self.add_csv_or_exl_data(file_path,destination_path)

    def insert_medical_records_data(self,data_as_list):
        failed_data = []
        interval = 100 / len(data_as_list)
        count_step=0
        self.run = True
        count = 0
        with sqlite3.connect(paths["database_path"]) as conn:
            cursor = conn.cursor()
            for i, data in enumerate(data_as_list):

                if not self.run:
                    self.progress_dialog.close()
                    self.update_csv_table()
                    definition_MessageBox("上传中途结束")
                    return
                if data[2] == "性别":  # 跳过表头行
                    count += interval
                    count_step+=1
                    continue
                try:
                    if pd.isna(data[3]):  # 检查是否为空值
                        data[3]=""

                    sql_insert = '''INSERT INTO medical_records (phone, name, sex, age, school, grade, class, is_active) 
                                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
                    cursor.execute(sql_insert, (data[0], data[1], data[2], data[3], data[4], data[5], data[6], 0))

                    # 判断表里是否有重复
                    sql = 'SELECT * FROM template WHERE school = ? AND grade = ? AND class = ? AND is_delete = 1;'
                    cursor.execute(sql, (data[4], data[5], data[6]))
                    res = cursor.fetchone()

                    if not res:
                        sql = '''INSERT INTO template(school, grade, class, is_delete) VALUES (?, ?, ?, 1)'''
                        cursor.execute(sql, (data[4], data[5], data[6]))

                    if i % 100 == 0:  # 每100条记录提交一次事务
                        conn.commit()

                    count += interval
                    count_step+=1
                    if count_step==10:
                        self.progress_dialog.setValue(count)
                        count_step = 0

                except Exception as ex:
                    if ex!="UNIQUE constraint failed: medical_records.phone":

                        failed_data.append(data)
                    count += interval
                    count_step += 1
                    if count_step == 10:
                        self.progress_dialog.setValue(count)
                        count_step = 0

                if i == len(data_as_list) - 1:
                    self.progress_dialog.close()
                    if failed_data:
                        # 创建并显示保存失败数据的窗口
                        failed_data_window = FailedDataWindow(failed_data)
                        failed_data_window.exec_()
                        definition_MessageBox(f"保存成功，但有 {len(failed_data)} 条数据保存失败")
                    else:
                        definition_MessageBox("保存成功")

                    self.update_csv_table()

            conn.commit()

            return True


    def add_csv_or_exl_data(self,file_path,destination_path):
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, header=None)
        elif file_path.endswith('.xls') or file_path.endswith('.xlsx'):
            engine = 'xlrd' if file_path.endswith('.xls') else 'openpyxl'
            df = pd.read_excel(file_path, header=None, engine=engine)
        else:
            self.progress_dialog.close()
            definition_MessageBox("请选择.csv或.xls文件")
            return

        data_as_list = df.values.tolist()
        if len(data_as_list[0])<7:

            conn = sqlite3.connect(paths["database_path"])
            cursor = conn.cursor()
            cursor.execute('DELETE FROM add_csv_path WHERE save_path = ?', (destination_path,))
            conn.commit()
            conn.close()
            if os.path.exists(destination_path):
                os.remove(destination_path)
            self.progress_dialog.close()
            definition_MessageBox(f"文件格式错误，请检查文件格式")
            return

        self.insert_medical_records_data(data_as_list)


    def export_csv_dir(self):
        directory_dialog = QFileDialog(self)
        directory_path = directory_dialog.getExistingDirectory(self, '打开文件夹', self.data_path_4.text())
        if directory_path:
            self.data_path_4.setText(directory_path)



    def update_csv_table(self):
        '''
        更新数据库表
        '''
        self.tableWidget.clearContents()
        row = 0
        res,step_list=self.api.get_csv_data()
        if res:
            if len(step_list):
                self.tableWidget.setRowCount(len(step_list))
            else:
                self.tableWidget.setRowCount(0)
        for info in step_list:
            #序号
            col = 0
            item = QTableWidgetItem(str(row+1))
            self.tableWidget.setItem(row, col, item)
            item.setTextAlignment(Qt.AlignCenter)

            #csv文件名
            col += 1
            item = QTableWidgetItem(info['csv_name'])
            self.tableWidget.setItem(row, col, item)
            item.setTextAlignment(Qt.AlignCenter)

            #操作
            col += 1
            custwidget = CustomWidget_csv(self,info,row)
            self.tableWidget.setCellWidget(row, col, custwidget)

            row += 1

    def update_settings(self):
        self.settings["save_path"] = self.data_path.text()
        with open(set_file_path, 'w', encoding='utf-8') as file:
            json.dump(self.settings, file, indent=2, ensure_ascii=False)

    def center(self):
        # 获取主屏幕的尺寸
        screen = QDesktopWidget().screenGeometry()

        # 获取窗口的尺寸
        size = self.geometry()

        # 计算窗口居中的位置
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2 - 40

        # 移动窗口到居中的位置
        self.move(x, y)

    def load_args(self):
        self.data_path.setText(str(self.settings['save_path']))

    def select_path(self):
        directory_dialog = QFileDialog(self)
        directory_path = directory_dialog.getExistingDirectory(self, '打开文件夹', self.data_path.text())
        if directory_path:
            self.data_path.setText(directory_path)

            self.settings['save_path'] = directory_path

            with open(set_file_path, 'w', encoding='utf-8') as file:
                json.dump(self.settings, file, indent=2,ensure_ascii=False)

    def add_template(self):
        self.wgt_template = Wgt_Template(self, "", "", "", type="add")
        self.wgt_template.show()

    def __init_table(self):
        '''
        初始化表格
        '''
        self.tableWidget_2.setStyleSheet("QWidget{font-size:9;}")
        self.tableWidget_2.clear()
        self.tableWidget_2.setShowGrid(False)
        self.tableWidget_2.setRowCount(0)

        self.tableWidget_2.verticalHeader().setHidden(True)  # 去掉序号列
        self.tableWidget_2.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)  # 用户设置
        self.tableWidget_2.horizontalHeader().setStretchLastSection(True)  # 最后一列自适应
        self.tableWidget_2.setSelectionMode(QAbstractItemView.SingleSelection)  # 设置只能选中一行
        self.tableWidget_2.setSelectionBehavior(QAbstractItemView.SelectRows)  # 设置只有行选中
        self.tableWidget_2.setEditTriggers(QTableView.NoEditTriggers)  # 不可编辑
        self.tableWidget_2.setFocusPolicy(Qt.NoFocus)

        head_list = ["序号",'学校', "年级", '班级', '操作']
        self.head_list_cnt = len(head_list)
        self.tableWidget_2.setColumnCount(self.head_list_cnt)
        self.tableWidget_2.setHorizontalHeaderLabels(head_list)

        self.tableWidget_2.setMouseTracking(True)  # 启用鼠标追踪
        self.tableWidget_2.mouseMoveEvent = self.table_mouse  # 绑定鼠标移动事件
        self.tableWidget_2.mousePressEvent = self.table_press  # 绑定鼠标点击事件


        # 按比例设置宽度
        header = self.tableWidget_2.horizontalHeader()
        self.tableWidget_2.setColumnWidth(0,45)
        header.setSectionResizeMode(0, QHeaderView.Fixed)

        for i in range(1, self.head_list_cnt):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        # self.tableWidget_2.setColumnWidth(0, 50)
        # self.tableWidget_2.setColumnWidth(1, 110)
        # self.tableWidget_2.setColumnWidth(2, 110)
        # self.tableWidget_2.setColumnWidth(3, 110)

    def table_press(self, event):
        item = self.tableWidget_2.itemAt(event.pos())
        if item is not None:
            row = item.row()
            self.Row = row
            self.tableWidget_2.clearSelection()  # 取消选中状态
            self.clearHoverEffects()
            if item is not None:
                self.tableWidget_2.setCurrentCell(row, 0)
                self.tableWidget_2.itemClicked.emit(item)  # 手动触发itemClicked信号

        super().mousePressEvent(event)

    def table_mouse(self, event):
        item = self.tableWidget_2.itemAt(event.pos())

        if item is not None:
            row = item.row()
            self.row = row

            self.clearHoverEffects()  # 清除之前的悬停效果

            for col in range(self.tableWidget_2.columnCount()):
                if col == 4:
                    self.tableWidget_2.cellWidget(row, col).setStyleSheet(
                        "background-color: rgb(217, 235, 249);color:rgb(0, 0, 255;)")
                    continue
                self.tableWidget_2.item(row, col).setBackground(QColor(217, 235, 249))  # 设置当前行的悬停效果


        super().mouseMoveEvent(event)

    def clearHoverEffects(self):
        for row_index in range(self.tableWidget_2.rowCount()):
            if self.Row == row_index:
                continue
            for col in range(self.tableWidget_2.columnCount()):
                item = self.tableWidget_2.item(row_index, col)
                cell_widget = self.tableWidget_2.cellWidget(row_index, col)
                if item is None and cell_widget is None:
                    break

                if col == 4:
                    self.tableWidget_2.cellWidget(row_index, col).setStyleSheet(
                        "background-color: rgb(255,255,255);color:rgb(0, 0, 255);")
                    continue

                self.tableWidget_2.item(row_index, col).setBackground(QColor(255,255,255))  # 恢复原始背景色



    def change_page(self, item):
        # 获取点击的项的索引
        self.index = self.listWidget_2.row(item)
        if self.index==0:
            #更新图表
            self.update_template_table()
        # 切换 QStackedWidget 中的界面
        self.stackedWidget.setCurrentIndex(self.index)

    def update_template_table(self):
        '''
        更新数据库表
        '''
        self.tableWidget_2.clearContents()
        row = 0
        res,step_list=self.api.get_template_data()
        if res:
            if len(step_list):
                self.tableWidget_2.setRowCount(len(step_list))
            else:
                self.tableWidget_2.setRowCount(0)

        for info in step_list:
            #序号
            col = 0
            item = QTableWidgetItem(str(row+1))
            self.tableWidget_2.setItem(row, col, item)
            item.setTextAlignment(Qt.AlignCenter)

            #学校
            col += 1
            item = QTableWidgetItem(info["school"])
            self.tableWidget_2.setItem(row, col, item)
            item.setTextAlignment(Qt.AlignCenter)

            # 年级
            col += 1
            item = QTableWidgetItem(info["grade"])
            self.tableWidget_2.setItem(row, col, item)
            item.setTextAlignment(Qt.AlignCenter)

            #班级
            col += 1
            item = QTableWidgetItem(info["class"])
            self.tableWidget_2.setItem(row, col, item)
            item.setTextAlignment(Qt.AlignCenter)


            #操作
            col += 1
            custwidget = CustomWidget(self,info,row)
            self.tableWidget_2.setCellWidget(row, col, custwidget)

            row += 1

    def mousePressEvent(self, event):
        # 鼠标键按下时调用
        if event.button() == Qt.LeftButton:
            self.m_Position = event.globalPos() - self.pos()  # 获取鼠标相对窗口的位置
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))  # 更改鼠标图标

    def mouseMoveEvent(self, QMouseEvent):
        if Qt.LeftButton:
            self.move(QMouseEvent.globalPos() - self.m_Position)  # 更改窗口位置
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        # 鼠标键公开时调用
        self.setCursor(QCursor(Qt.ArrowCursor))

class FailedDataWindow(QDialog):
    def __init__(self, failed_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("保存失败的数据")
        self.setWindowIcon(QIcon(":/icon/res/logo.png"))
        self.setGeometry(300, 300, 970, 500)

        # 创建 QTableWidget
        self.tableWidget_2 = QTableWidget(self)

        self.tableWidget_2.setStyleSheet("QWidget{font-size:9;}")
        self.tableWidget_2.clear()
        self.tableWidget_2.setShowGrid(False)
        self.tableWidget_2.installEventFilter(self)

        self.tableWidget_2.verticalHeader().setHidden(True)  # 去掉序号列
        self.tableWidget_2.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)  # 用户设置
        self.tableWidget_2.horizontalHeader().setStretchLastSection(True)  # 最后一列自适应

        self.tableWidget_2.setSelectionMode(QAbstractItemView.SingleSelection)  # 设置只能选中一行
        self.tableWidget_2.setSelectionBehavior(QAbstractItemView.SelectRows)  # 设置只有行选中

        self.tableWidget_2.setEditTriggers(QTableView.NoEditTriggers)  # 不可编辑

        self.tableWidget_2.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)  # 隐藏滚动条
        self.tableWidget_2.setFocusPolicy(Qt.NoFocus)


        self.tableWidget_2.setColumnCount(8)
        self.tableWidget_2.setHorizontalHeaderLabels(["序号",'学号', '姓名', '性别', '年龄', '学校', '年级', '班级'])
        self.tableWidget_2.setColumnWidth(0, 60)
        # 设置数据

        self.tableWidget_2.setRowCount(len(failed_data))
        for row_idx, row_data in enumerate(failed_data):
            # 设置序号
            serial_item = QTableWidgetItem(str(row_idx + 1))
            serial_item.setTextAlignment(Qt.AlignCenter)  # 设置序号居中
            self.tableWidget_2.setItem(row_idx, 0, serial_item)

            # 设置其他数据
            for col_idx, item in enumerate(row_data):
                table_item = QTableWidgetItem(str(item))
                table_item.setTextAlignment(Qt.AlignCenter)  # 设置文字居中
                self.tableWidget_2.setItem(row_idx, col_idx + 1, table_item)  # 数据列从1开始

        # 布局
        layout = QVBoxLayout()
        layout.addWidget(self.tableWidget_2)

        # 添加关闭按钮
        close_button = QPushButton("关闭", self)
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)

class CustomWidget_csv(QWidget):
    def __init__(self,db_set,info,row):
        super().__init__()

        self.db_set=db_set
        self.row=row
        self.info=info
        self.initUI()

    def initUI(self):
        # 创建四个 QLabel
        self.label1 = QLabel('删除', self)
        self.label1.setAlignment(Qt.AlignCenter)
        font = QFont('Microsoft YaHei', 9)

        self.label1.setFont(font)
        self.label1.setStyleSheet("QLabel {color:rgb(0, 0, 255);}")
        self.label1.installEventFilter(self)

        # 创建一个 QHBoxLayout 布局
        layout = QHBoxLayout(self)
        layout.addWidget(self.label1)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

    def enterEvent(self, event):
        if self.db_set.row_csv:
            selected_row = ""
            selected_items = self.db_set.tableWidget.selectedItems()
            if selected_items:
                selected_row = selected_items[0].row()
            if selected_row == self.db_set.row_csv:
                pass
            else:
                for col in range(self.db_set.tableWidget.columnCount()):
                    item = self.db_set.tableWidget.item(self.db_set.row_csv, col)
                    cell_widget = self.db_set.tableWidget.cellWidget(self.db_set.row_csv, col)
                    if item is None and cell_widget is None:
                        break
                    if col == 2:
                        self.db_set.tableWidget.cellWidget(self.db_set.row_csv, col).setStyleSheet(
                            "background-color: rgb(255,255,255);color:rgb(0, 0, 255);")
                        continue

                    self.db_set.tableWidget.item(self.db_set.row_csv, col).setBackground(QColor(255,255,255))  # 恢复原始背景色

        for col in range(self.db_set.tableWidget.columnCount()):
            if col == 2:
                self.db_set.tableWidget.cellWidget(self.row, col).setStyleSheet(
                    "background-color: rgb(217, 235, 249);color:rgb(0, 0, 255;)")
                continue

            self.db_set.tableWidget.item(self.row, col).setBackground(QColor(217, 235, 249))  # 设置当前行的悬停效果

    def leaveEvent(self, event):
        self.clearHoverEffects()  # 清除之前的悬停效果

    def clearHoverEffects(self):
        selected_items = self.db_set.tableWidget.selectedItems()
        if selected_items:
            selected_row = selected_items[0].row()
            if selected_row == self.row:
                return

        for col in range(self.db_set.tableWidget.columnCount()):
            item = self.db_set.tableWidget.item(self.row, col)
            cell_widget = self.db_set.tableWidget.cellWidget(self.row, col)
            if item is None and cell_widget is None:
                break

            if col == 2:
                self.db_set.tableWidget.cellWidget(self.row, col).setStyleSheet(
                    "background-color: rgb(255,255,255);color:rgb(0, 0, 255);")
                continue

            self.db_set.tableWidget.item(self.row, col).setBackground(QColor(255,255,255))  # 恢复原始背景色


    def eventFilter(self, obj, event):
        '''事件过滤
        '''
        event_type = event.type()
        if isinstance(event, QMouseEvent) and event.buttons() == QtCore.Qt.LeftButton: #鼠标左键点击此控件时
            if obj==self.label1: #删除
                msg_box, yes_button, no_button = select_definition_MessageBox("该导入文件将被删除,请确认")
                if msg_box.clickedButton() == yes_button:
                    res=self.db_set.api.delete_csv(self.info["save_path"])
                    if os.path.exists(self.info["save_path"]):
                        os.remove(self.info["save_path"])
                    if res:
                        #更新table表
                        self.db_set.update_csv_table()


        return QObject.eventFilter(self, obj, event)  # 交由其他控件处理


class CustomWidget(QWidget):
    def __init__(self,db_set,info,row):
        super().__init__()

        self.db_set=db_set
        self.row=row
        self.info=info
        self.initUI()

    def initUI(self):
        # 创建四个 QLabel
        self.label1 = QLabel('编辑', self)
        self.label2 = QLabel('删除', self)

        font = QFont('Microsoft YaHei', 9)

        self.label1.setFont(font)
        self.label2.setFont(font)
        #self.label1.setStyleSheet("QLabel:hover{color:red;}")
        self.label1.setStyleSheet("QLabel {color:rgb(0, 0, 255);}")
        self.label2.setStyleSheet("QLabel {color:rgb(0, 0, 255);}")

        self.label1.installEventFilter(self)
        self.label2.installEventFilter(self)
        # 创建一个 QHBoxLayout 布局
        layout = QHBoxLayout(self)
        layout.addWidget(self.label1)
        layout.addWidget(self.label2)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

    def enterEvent(self, event):
        if self.db_set.row:
            selected_row = ""
            selected_items = self.db_set.tableWidget_2.selectedItems()
            if selected_items:
                selected_row = selected_items[0].row()
            if selected_row == self.db_set.row:
                pass
            else:
                for col in range(self.db_set.tableWidget_2.columnCount()):
                    item = self.db_set.tableWidget_2.item(self.db_set.row, col)
                    cell_widget = self.db_set.tableWidget_2.cellWidget(self.db_set.row, col)
                    if item is None and cell_widget is None:
                        break
                    if col == 4:
                        self.db_set.tableWidget_2.cellWidget(self.db_set.row, col).setStyleSheet(
                            "background-color: rgb(255,255,255);color:rgb(0, 0, 255);")
                        continue

                    self.db_set.tableWidget_2.item(self.db_set.row, col).setBackground(QColor(255,255,255))  # 恢复原始背景色

        for col in range(self.db_set.tableWidget_2.columnCount()):
            if col == 4:
                self.db_set.tableWidget_2.cellWidget(self.row, col).setStyleSheet(
                    "background-color: rgb(217, 235, 249);color:rgb(0, 0, 255;)")
                continue

            self.db_set.tableWidget_2.item(self.row, col).setBackground(QColor(217, 235, 249))  # 设置当前行的悬停效果

    def leaveEvent(self, event):
        self.clearHoverEffects()  # 清除之前的悬停效果

    def clearHoverEffects(self):
        selected_items = self.db_set.tableWidget_2.selectedItems()
        if selected_items:
            selected_row = selected_items[0].row()
            if selected_row == self.row:
                return

        for col in range(self.db_set.tableWidget_2.columnCount()):
            item = self.db_set.tableWidget_2.item(self.row, col)
            cell_widget = self.db_set.tableWidget_2.cellWidget(self.row, col)
            if item is None and cell_widget is None:
                break

            if col == 4:
                self.db_set.tableWidget_2.cellWidget(self.row, col).setStyleSheet(
                    "background-color: rgb(255,255,255);color:rgb(0, 0, 255);")
                continue

            self.db_set.tableWidget_2.item(self.row, col).setBackground(QColor(255,255,255))  # 恢复原始背景色


    def eventFilter(self, obj, event):
        '''事件过滤
        '''
        event_type = event.type()
        if isinstance(event, QMouseEvent) and event.buttons() == QtCore.Qt.LeftButton: #鼠标左键点击此控件时

            if obj==self.label1: #编辑
                self.template = Wgt_Template(self.db_set,self.info["school"], self.info["grade"], self.info["class"],type="update")
                self.template.show()

            elif obj==self.label2: #删除
                msg_box, yes_button, no_button = select_definition_MessageBox("该学校所有学生信息将被删除,请确认")
                if msg_box.clickedButton() == yes_button:
                    res=self.db_set.api.delete_template(self.info["school"],self.info["grade"],self.info["class"])
                    if res:
                        #更新table表
                        self.db_set.update_template_table()


        return QObject.eventFilter(self, obj, event)  # 交由其他控件处理

class Wgt_Template(QWidget,Ui_template_form):

    def __init__(self,db_set,school,grade,Class,type=None):
        super(Wgt_Template, self).__init__()

        self.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)  # 无边框
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowIcon(QIcon(":/icon/res/logo.png"))
        self.setWindowTitle('添加模板')

        self.pbhide.setMouseTracking(True)
        self.pbhide.setToolTip("窗口最小化")
        self.pbhide.clicked.connect(self.showMinimized)

        self.pbClose.setMouseTracking(True)
        self.pbClose.setToolTip("关闭程序")
        self.pbClose.clicked.connect(self.close)

        self.school=school
        self.grade=grade
        self.Class=Class
        self.type=type
        self.db_set=db_set
        if type=="add":

            self.setWindowTitle('添加')
        else:
            self.setWindowTitle('编辑')

        font = QFont("微软雅黑", 12)  # 设置字体为 Arial，字号为 12
        self.lineEdit.setFont(font)
        self.lineEdit_2.setFont(font)
        self.lineEdit_3.setFont(font)

        self.lineEdit.setText(self.school)
        self.lineEdit_2.setText(self.grade)
        self.lineEdit_3.setText(self.Class)
        # 将事件过滤器安装到整个窗口
        self.installEventFilter(self)

        self.pushButton.clicked.connect(self.submit_template)  # 提交模板
        self.pushButton_3.clicked.connect(self.Cancel_infor)  # 提交模板
        self.m_Position = QPoint()
    def mousePressEvent(self, event):
        # 鼠标键按下时调用
        if event.button() == Qt.LeftButton:
            self.m_Position = event.globalPos() - self.pos()  # 获取鼠标相对窗口的位置
            event.accept()

    def mouseMoveEvent(self, QMouseEvent):
        if Qt.LeftButton:
            self.move(QMouseEvent.globalPos() - self.m_Position)  # 更改窗口位置
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        # 鼠标键公开时调用
        self.setCursor(QCursor(Qt.ArrowCursor))

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:  # 捕捉键盘按键事件
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                # 回车键被按下时，触发按钮的点击事件
                self.pushButton.click()
                return True

        return QObject.eventFilter(self, obj, event)  # 交由其他控件处理

    def Cancel_infor(self):
        self.close()
    def submit_template(self):
        '''
        添加模板和编辑模板
        '''
        school_text = self.lineEdit.text().strip()
        grade_text = self.lineEdit_2.text().strip()
        class_text = self.lineEdit_3.text().strip()

        if school_text == "" or grade_text == "" or  class_text == "":
            definition_MessageBox("信息为空!")
            return

        if self.type=="add":
            #添加
            res,info=self.db_set.api.create_template(school_text,grade_text,class_text)
            if res:
                definition_MessageBox("添加成功")
                self.close()
                #更新table表
                self.db_set.update_template_table()
            else:
                definition_MessageBox(info)

        elif self.type=="update":
            #编辑
            res,info=self.db_set.api.update_template(self.school,school_text,self.grade,grade_text,self.Class,class_text)
            if res:
                definition_MessageBox("编辑成功")
                self.close()
                # 更新table表
                self.db_set.update_template_table()
            else:
                definition_MessageBox(info)



class CustomProgressDialog(QProgressDialog):
    def __init__(self, labelText, cancelText, min, max, parent=None):
        super().__init__(labelText, cancelText, min, max, parent)
        # 直接隐藏默认取消按钮
        self.setCancelButton(None)
        self.parent=parent
        self.setWindowModality(Qt.WindowModal)
        self.setWindowTitle("导入")
        self.resize(300, 150)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)

        # 创建自定义取消按钮和布局
        self.cancel_button = QPushButton(cancelText, self)
        self.cancel_button.clicked.connect(self.reject)  # 连接取消信号

        self.cancel_button.setStyleSheet("""
                    QPushButton {
                        background-color: #F2F2F2;
                        border: 1px solid #DDDDDD;
                        border-radius: 5px;
                        padding: 10px 20px;  # 增加按钮的内边距
                        font-size: 16px;     # 增大字体
                        min-width: 100px;    # 设置按钮的最小宽度
                    }
                """)

        # 获取 QProgressDialog 中的 QLabel 和 QProgressBar
        label = self.findChild(QLabel)
        progress_bar = self.findChild(QProgressBar)

        # 创建一个新的布局并添加控件
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(progress_bar)
        layout.addWidget(self.cancel_button, alignment=Qt.AlignCenter)

        # 应用自定义样式
        self.setStyleSheet("""
            QProgressDialog {
                background-color: #FFFFFF;
                color: #333333;
                border: 1px solid #DDDDDD;
                border-radius: 10px;
                padding: 15px;
            }
            QLabel {
                color: #333333;
            }
            QProgressBar {
                border: 1px solid #DDDDDD;
                border-radius: 5px;
                text-align: center;
                background-color: #F2F2F2;
            }   
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 20px;
                margin: 1px;
            }
        """)
        self.setLayout(layout)

    def reject(self):
        self.parent.run = False
