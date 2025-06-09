import threading
from functools import partial

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QObject, QEvent, pyqtSignal, QThread, QPoint
from PyQt5.QtGui import QCursor, QMouseEvent, QColor, QIcon, QFont
from PyQt5.QtWidgets import QWidget, QHeaderView, QAbstractItemView, QTableView, QTableWidgetItem, QLabel, QHBoxLayout, \
    QMessageBox, QCalendarWidget, QFileDialog, QListView, QDesktopWidget, QProgressDialog, QCheckBox, QVBoxLayout, \
    QProgressBar, QPushButton, QApplication, QComboBox

from xlutils.copy import copy
import xlrd
import xlwt
from db_report import Report
from gui.main_data import Ui_data_frame
from utils.logger import logger
from utils.utils import wait_noblock, select_definition_MessageBox, definition_MessageBox
from datetime import datetime
import pandas as pd

class WgtData(QWidget, Ui_data_frame):
    control_signal = pyqtSignal(list)
    def __init__(self,api):
        super(WgtData, self).__init__()
        self.setupUi(self)
        screen_resolution = QApplication.primaryScreen().size()
        screen_width = screen_resolution.width()
        screen_height = screen_resolution.height()

        width = int(screen_width * 0.96)
        height = screen_height * 0.9
        self.setGeometry(0, 0, width, height)

        self.center(screen_resolution)

        self.setWindowFlags(Qt.FramelessWindowHint) #无边框
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowIcon(QIcon(":/icon/res/logo.png"))
        self.setWindowTitle('数据检索')

        #初始化表格
        self.show()

        self.api = api
        self.page_count = 0  # 当前页面默认 table行数
        self.Row = ""
        self.row = ""
        self.calendar = None
        self.calendar_2 = None
        self.export_flag=False
        self.label_10.setText("1")

        self.pbhide.setMouseTracking(True)
        self.pbhide.setToolTip("窗口最小化")
        self.pbhide.clicked.connect(self.showMinimized)

        self.pbClose.setMouseTracking(True)
        self.pbClose.setToolTip("关闭程序")
        self.pbClose.clicked.connect(self.close)

        self.pushButton_3.clicked.connect(partial(self.export_list, 'list')) #导出列表
        self.pushButton_4.clicked.connect(partial(self.export_list, 'page')) #导出本页

        self.lineEdit_2.textChanged.connect(self.showStretchOptions) #手机号
        self.lineEdit_3.textChanged.connect(self.showStretchOptions) #姓名

        self.lineEdit_time_3.setReadOnly(True)  # 设置为只读
        self.lineEdit_time_3.installEventFilter(self)

        self.lineEdit_time_4.setReadOnly(True)  # 设置为只读
        self.lineEdit_time_4.installEventFilter(self)

        self.abnormal_flag = False

        self.label_32.installEventFilter(self)

        self.pushButton_12.clicked.connect(self.__pre_page)  # 上一页
        self.pushButton_13.clicked.connect(self.__next_page)  # 下一页
        self.pushButton_14.clicked.connect(self.__final_page)  # 尾页
        self.pushButton_15.clicked.connect(self.__confirm_skip)  # 确认
        self.control_signal.connect(self.page_controller)

        self.comboBox_9.setView(QListView())
        res, grade_list = self.api.get_grade_order_by("")
        self.comboBox_9.addItem("请选择")
        self.comboBox_9.addItems(grade_list)
        self.comboBox_9.setCurrentIndex(0)
        self.__init_table()
        self.__init_user_table()
        self.comboBox_10.setView(QListView())  # 学校

        self.comboBox_9.currentIndexChanged.connect(self.on_combobox_index_changed)
        self.comboBox_10.currentIndexChanged.connect(self.on_combobox_index_changed)

        self.comboBox_11.setView(QListView())

        self.comboBox_11.addItem("请选择")
        self.comboBox_11.addItems(["正常", "轻度", "中度", "重度"])
        self.comboBox_11.setCurrentIndex(0)
        self.comboBox_11.currentIndexChanged.connect(self.on_combobox_index_changed)

        self.pushButton_5.clicked.connect(self.expoer_all_pdf)

        self.comboBox_12.setView(QListView())
        res, school_list = self.api.get_school_order_by()
        self.comboBox_12.addItem("请选择")
        self.comboBox_12.addItems(school_list)
        self.comboBox_12.setCurrentIndex(0)

        self.comboBox_12.currentIndexChanged.connect(self.on_combobox_school_changed)

        self.comboBox_13.setView(QListView())

        self.comboBox_13.addItem("请选择")
        self.comboBox_13.addItems(["已检查", "未检查"])
        self.comboBox_13.setCurrentIndex(0)
        self.comboBox_13.currentIndexChanged.connect(self.on_combobox_index_changed)
        self.frame_23.hide()
        self.comboBox_12.hide()
        self.label_23.hide()

        self.print_button_3.clicked.connect(self.report_list)  # 检测列表
        self.save_button_3.clicked.connect(self.historical_school)  # 预约学校
        self.save_button_4.clicked.connect(self.historical_abnormal)  # 心理异常

        self.label_7.setStyleSheet("background-color: #3498db;")
        self.label_14.setStyleSheet("background-color: transparent;")
        self.label_16.setStyleSheet("background-color: transparent;")
        self.save_button_4.setChecked(False)
        self.save_button_3.setChecked(False)


        self.m_Position = QPoint()
        self.isDragging = False
        self.setupComboBoxEvents()

    def historical_abnormal(self):
        if self.save_button_4.isChecked():
            self.label_16.setStyleSheet("background-color: #3498db;")
            self.label_7.setStyleSheet("background-color: transparent;")
            self.label_14.setStyleSheet("background-color: transparent;")
            self.save_button_3.setChecked(False)
            self.print_button_3.setChecked(False)

        self.abnormal_flag=True
        self.frame_2.show()
        self.frame_21.show()
        self.frame_22.show()
        self.frame_23.hide()
        self.pushButton_5.show()

        self.comboBox_12.hide()
        self.label_23.hide()

        self.stackedWidget.setCurrentIndex(0)
        #判断哪些人做了最少三次 每次都是异常

        grade, Class, level = self.back_comboBox_result()
        res, cnt, total_cnt = self.api.get_abnormal_count_page(self.lineEdit_2.text().strip(), self.lineEdit_3.text().strip(),
                                                      self.lineEdit_time_3.text().strip(), self.lineEdit_time_4.text().strip(),grade, Class, level,
                                                      self.page_count)
        if res:
            self.cnt = cnt
            self.label_13.setText(f"{cnt}页,共{total_cnt}条记录")
        self.label_10.setText("1")

        res, step_list = self.api.get_abnormal_data(self.page_count, int(self.label_10.text()),
                                                      time=self.lineEdit_time_3.text().strip(),
                                                      name=self.lineEdit_3.text().strip(),
                                                      phone=self.lineEdit_2.text().strip(),
                                                      grade=grade,
                                                      Class=Class,
                                                      level=level,
                                                      time_suffix=self.lineEdit_time_4.text().strip(),
                                                      )
        self.for_tabel_data(int(self.label_10.text()), step_list)


    def historical_school(self):
        if self.save_button_3.isChecked():
            self.label_14.setStyleSheet("background-color: #3498db;")
            self.label_7.setStyleSheet("background-color: transparent;")
            self.label_16.setStyleSheet("background-color: transparent;")
            self.save_button_4.setChecked(False)
            self.print_button_3.setChecked(False)

        self.abnormal_flag=False
        self.frame_2.hide()
        self.frame_21.hide()
        self.frame_22.hide()
        self.frame_23.show()
        self.pushButton_5.hide()

        self.page_user_count = int(20)
        self.tableWidget_3.setRowCount(self.page_user_count)

        self.comboBox_12.show()
        self.label_23.show()

        self.stackedWidget.setCurrentIndex(1)
        self.show_UserStretchOptions(self.comboBox_12.currentText())

    def report_list(self):
        if self.print_button_3.isChecked():
            self.label_7.setStyleSheet("background-color: #3498db;")
            self.label_14.setStyleSheet("background-color: transparent;")
            self.label_16.setStyleSheet("background-color: transparent;")
            self.save_button_4.setChecked(False)
            self.save_button_3.setChecked(False)

        self.abnormal_flag=False
        self.frame_2.show()
        self.frame_21.show()
        self.frame_22.show()
        self.frame_23.hide()
        self.pushButton_5.show()

        self.comboBox_12.hide()
        self.label_23.hide()

        self.stackedWidget.setCurrentIndex(0)
        self.showStretchOptions()


    def setupComboBoxEvents(self):
        # 绑定每个 QComboBox 的 mousePressEvent 到自定义方法
        for comboBox in [self.comboBox_11, self.comboBox_10, self.comboBox_9,self.comboBox_13,self.comboBox_12]:
            comboBox.mousePressEvent = self.createComboBoxMousePressEvent(comboBox)

    def show_UserStretchOptions(self,school_text):
        check_state = self.comboBox_13.currentText()
        if check_state == "请选择":
            check_text = ""
        elif check_state == "已检查":
            check_text = 1
        else:
            check_text = 0
        grade, Class, level = self.back_comboBox_result()
        self.init_user_total_count(school_text,check_text)
        self.label_10.setText("1")
        res, step_list = self.api.get_page_user_count_data(self.page_user_count, int(self.label_10.text()),
                                                           school_text,
                                                           name=self.lineEdit_3.text().strip(),
                                                           phone=self.lineEdit_2.text().strip(),
                                                           grade=grade,
                                                           Class=Class,
                                                            check=check_text,
                                                           )
        self.update_user_table(int(self.label_10.text()), step_list)

    def on_combobox_school_changed(self):
        self.comboBox_9.blockSignals(True)
        self.comboBox_10.blockSignals(True)

        school_text = self.comboBox_12.currentText()

        self.comboBox_10.clear()
        self.comboBox_9.clear()

        if self.comboBox_12.currentText() == "请选择":
            res, grade_list = self.api.get_grade_order_by("")
            self.comboBox_9.addItem("请选择")
            self.comboBox_9.addItems(grade_list)
            self.comboBox_9.setCurrentIndex(0)
        else:
            res, grade_list = self.api.get_grade_order_by(school_text)
            self.comboBox_9.addItem("请选择")
            self.comboBox_9.addItems(grade_list)
            self.comboBox_9.setCurrentIndex(0)

        school_text = self.comboBox_12.currentText()
        self.show_UserStretchOptions(school_text)

        self.comboBox_9.blockSignals(False)
        self.comboBox_10.blockSignals(False)



    def update_user_table(self,current_page, step_list):
        '''
        更新数据库表
        '''
        self.tableWidget_3.clearContents()
        row = 0
        id = current_page * self.page_user_count - self.page_user_count + 1

        for data in step_list:
            col =0
            item = QTableWidgetItem(str(id))
            self.tableWidget_3.setItem(row, col, item)
            item.setTextAlignment(Qt.AlignCenter)
            id += 1

            #学号
            col += 1
            item = QTableWidgetItem(data["phone"])
            self.tableWidget_3.setItem(row, col, item)
            item.setTextAlignment(Qt.AlignCenter)

            # 姓名
            col += 1
            item = QTableWidgetItem(data["name"])
            self.tableWidget_3.setItem(row, col, item)
            item.setTextAlignment(Qt.AlignCenter)


            # 性别
            col += 1
            item = QTableWidgetItem(data["sex"])
            self.tableWidget_3.setItem(row, col, item)
            item.setTextAlignment(Qt.AlignCenter)


            # 年龄
            col += 1
            if data["age"] is None:
                item = QTableWidgetItem(data["age"])
            else:
                item = QTableWidgetItem(str(data["age"]))
            self.tableWidget_3.setItem(row, col, item)
            item.setTextAlignment(Qt.AlignCenter)


            # 学校
            col += 1
            item = QTableWidgetItem(data["school"])
            self.tableWidget_3.setItem(row, col, item)
            item.setTextAlignment(Qt.AlignCenter)

            # 年级
            col += 1
            item = QTableWidgetItem(data["grade"])
            self.tableWidget_3.setItem(row, col, item)
            item.setTextAlignment(Qt.AlignCenter)


            # 班级
            col += 1
            item = QTableWidgetItem(data["class"])
            self.tableWidget_3.setItem(row, col, item)
            item.setTextAlignment(Qt.AlignCenter)

            col += 1
            if data["is_active"]==0:
                check_state="未检查"
            else:
                check_state = "已检查"

            item = QTableWidgetItem(check_state)
            self.tableWidget_3.setItem(row, col, item)
            item.setTextAlignment(Qt.AlignCenter)
            if data["is_active"]==1:
                item.setForeground(QColor(146,195,255))

            row += 1

            if row == self.page_user_count:
                return


    def expoer_all_pdf(self):
        '''导出全部pdf'''
        step_list = []
        for row in range(self.tableWidget_2.rowCount()):
            CheckBox = self.tableWidget_2.cellWidget(row, 0)
            if CheckBox:
                if CheckBox.isChecked():
                    phone = self.tableWidget_2.item(row, 2).text()
                    name = self.tableWidget_2.item(row, 3).text()
                    count = self.tableWidget_2.item(row, 12).text()
                    # 获取文本内容并处理可能的 None 值
                    phone_text = phone if phone else ""
                    name_text = name if name else ""
                    count_text = int(count) if count else 0

                    checkbox_dict = {"phone": phone_text, "name": name_text, "count": count_text}
                    step_list.append(checkbox_dict)

        if not step_list:
            grade, Class, level = self.back_comboBox_result()
            res, step_list = self.api.get_page_count_data(self.page_count, int(self.label_10.text()),
                                                          time=self.lineEdit_time_3.text().strip(),
                                                          name=self.lineEdit_3.text().strip(),
                                                          phone=self.lineEdit_2.text().strip(),
                                                          grade=grade,
                                                          Class=Class,
                                                          level=level,
                                                          time_suffix=self.lineEdit_time_4.text().strip(),

                                                            )
        # 获取选中得路径
        directory_dialog = QFileDialog(self)
        directory_path = directory_dialog.getExistingDirectory(self, '打开文件夹')
        if directory_path:
        #起线程保存
            self.progress_dialog = CustomProgressDialog("生成PDF中...", "取消", 0, 100, self)

            self.progress_dialog.show()

            wait_noblock(0.2)
            self.report = Report("", 0, self.api, "", is_show=False)
            self.update_pdf(step_list, directory_path)

    def update_pdf(self, step_list, directory_path):
        interval = 100 / len(step_list)
        self.run = True
        count = 0
        frema_count=0

        for i, data in enumerate(step_list):
            if not self.run:
                self.progress_dialog.close()
                definition_MessageBox("保存中途结束")
                return
            try:
                frema_count+=1
                if frema_count==5:
                    self.report.close()
                    self.report = Report("", 0, self.api, "", is_show=False)
                    frema_count=0

                self.report.update_signal.emit(data["phone"], data["count"], data["name"])
                wait_noblock(0.2)
                self.report.export_pdf_file(directory_path=directory_path)
                self.progress_dialog.setValue(count + interval)
                count += interval
                if i == len(step_list) - 1:
                    self.progress_dialog.close()
                    definition_MessageBox("保存成功")
            except Exception as e:
                logger.error('db_data/report_pdf_Thread/导出pdf报告/%s', str(e))
                break
        self.report.close()




    def center(self,screen):
        # 获取窗口的尺寸
        size = self.geometry()

        # 计算窗口居中的位置
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2 - 40

        # 移动窗口到居中的位置
        self.move(x, y)

    def on_combobox_index_changed(self):
        #防止递归调用
        self.comboBox_9.blockSignals(True)
        self.comboBox_10.blockSignals(True)

        sender = self.sender()
        if self.comboBox_9.currentText()=="请选择":
            self.comboBox_10.clear()

        if sender == self.comboBox_9:
            self.comboBox_10.clear()
            grade_text = self.comboBox_9.currentText()
            if grade_text=="请选择":
                grade_text=""
            res, class_list = self.api.get_class_order_by("", grade_text)
            self.comboBox_10.addItem("请选择")
            self.comboBox_10.addItems(class_list)
            self.comboBox_10.setCurrentIndex(0)

        self.label_10.setText("1")

        # 处理完毕后重新连接信号
        self.comboBox_9.blockSignals(False)
        self.comboBox_10.blockSignals(False)

        current_index = self.stackedWidget.currentIndex()
        grade, Class, level = self.back_comboBox_result()
        if current_index == 0:
            if self.abnormal_flag:
                res, step_list = self.api.get_abnormal_data(self.page_count, int(self.label_10.text()),
                                                        time=self.lineEdit_time_3.text().strip(),
                                                        name=self.lineEdit_3.text().strip(),
                                                        phone=self.lineEdit_2.text().strip(),
                                                        grade=grade,
                                                        Class=Class,
                                                        level=level,
                                                        time_suffix=self.lineEdit_time_4.text().strip(),

                                                        )
            else:
                res, step_list = self.api.get_page_count_data(self.page_count, int(self.label_10.text()),
                                                              time=self.lineEdit_time_3.text().strip(),
                                                              name=self.lineEdit_3.text().strip(),
                                                              phone=self.lineEdit_2.text().strip(),
                                                              grade=grade,
                                                              Class=Class,
                                                              level=level,
                                                              time_suffix=self.lineEdit_time_4.text().strip(),
                                                              )
            self.init_total_count()
            self.for_tabel_data(int(self.label_10.text()), step_list)
        else:
            check_state=self.comboBox_13.currentText()
            if check_state=="请选择":
                check_text=""
            elif check_state=="已检查":
                check_text=1
            else:
                check_text = 0
            school_text = self.comboBox_12.currentText()
            self.init_user_total_count(school_text,check_text)
            res, step_list = self.api.get_page_user_count_data(self.page_user_count, int(self.label_10.text()),
                                                               school_text,
                                                               name=self.lineEdit_3.text().strip(),
                                                               phone=self.lineEdit_2.text().strip(),
                                                               grade=grade,
                                                               Class=Class,
                                                                check=check_text,
                                                               )
            self.update_user_table(int(self.label_10.text()), step_list)

    def back_comboBox_result(self):
        grade = self.comboBox_9.currentText()
        Class = self.comboBox_10.currentText()
        level = self.comboBox_11.currentText()
        if grade=="请选择":
            grade=""
        if Class=="请选择":
            Class=""
        if level=="请选择":
            level=""

        return grade,Class,level
    def export_list(self,text):
        '''
        导出列表按钮
        '''
        self.export_flag = False
        selected_file, ftype = QFileDialog.getSaveFileName(self, 'save file', './', "All files (*.xls)")
        thread = threading.Thread(target=self.export_tabel_info, args=(selected_file,text))
        thread.start()
        while (thread.is_alive()):
            wait_noblock()
        thread.join()
        if self.export_flag:
            definition_MessageBox("导出完成")

    def export_tabel_info(self,selected_file,text1):
        new_file_path=""
        if selected_file:
            new_file_path = selected_file.strip()
            # 如果用户没有输入 .xml 扩展名，自动添加
            if not new_file_path.endswith('.xls'):
                new_file_path += '.xls'

        if new_file_path:
            self.export_flag=True
            new_file_list = new_file_path.split("/")

            text=new_file_list[-1][:-4]
            head_list = ["学号","姓名", "班级","年级","性别","年龄","焦虑得分","焦虑程度","抑郁得分","抑郁程度","检测次数","检测时间"]

            grade, Class, level = self.back_comboBox_result()
            if text1=="page":
                res, all_data = self.api.export_Current_page_tables(self.page_count, int(self.label_10.text()),
                                                      time=self.lineEdit_time_3.text().strip(),
                                                      name=self.lineEdit_3.text().strip(),
                                                      phone=self.lineEdit_2.text().strip(),
                                                      grade=grade,
                                                      Class= Class,
                                                      level= level,
                                                    time_suffix=self.lineEdit_time_4.text().strip(),

                                                                    )
            else:
                res, all_data = self.api.export_total_tables()
            # 导出excel文件
            self.excel_export_file(text, new_file_path, head_list, all_data)

        else:
            return

    def excel_export_file(self,export_file_name,excel_path,head_list,all_data): #excel文件表导出
        '''
        curr_table_name:要导出的文件名
        excel_path:导出路径
        head_list:表标签
        all_data:表数据
        '''
        new_workbook = xlwt.Workbook() #创建一个新的 Excel 工作簿（Workbook）

        if len(export_file_name)>20:
            new_workbook.add_sheet(export_file_name[:20])
        else:
            new_workbook.add_sheet(export_file_name)  # 创建一个新的工作表（Sheet）

        new_workbook.save(excel_path)  # 保存新的 Excel工作簿到 excel_path 文件路径

        oldWb = xlrd.open_workbook(excel_path, formatting_info=True)  # 使用 xlrd打开旧的 Excel 文件
        # 设置excel的边框
        borders = xlwt.Borders()
        styletest(borders, 1, 1, 1, 1)
        style = xlwt.XFStyle()
        style.borders = borders

        newWb = copy(oldWb)  # 复制旧的 Excel 工作簿，获得一个新的工作簿对象（newWb）
        # 获取新的工作簿的第一个工作表（newWs）
        newWs = newWb.get_sheet(0)

        # 得出tableWidget2有多少行数据
        colunm_list = len(head_list)
        colunm_filter = []
        for i in head_list:
            colunm_filter.append(i)
        count = 0

        for j in range(colunm_list):
            tag_list = []
            data = colunm_filter[count]  # 得出tablewidget每行每列的数据
            count += 1
            tag_list.append(data)  # 添加到数组
            # 把mainlist中的数据写入表格

            newWs.write(0, j, tag_list[0], style)

        count = 0

        for i in all_data:
            # 因为是边读边写，所以每次写完后，要把上次存储的数据清空，存储下一行读取的数据
            mainList = []
            # tablewidget一共有10列
            col = 0
            for j in range(colunm_list):
                try:
                    value = i[j]  # 得出tablewidget每行每列的数据
                    mainList.append(str(value))  # 添加到数组
                except:
                    # 如果tablewidget没有对象，则data = ‘’
                    data = ''
                    mainList.append(data)
                # 把mainlist中的数据写入表格
                newWs.write(count + 1, col, mainList[j], style)
                col += 1
            count += 1
        # 保存新的 Excel 工作簿到 excel_path 文件路径
        newWb.save(excel_path)

    def showTotalPage(self):
        """返回当前总页数"""
        return self.cnt

    def __pre_page(self):
        """点击上一页信号"""
        self.control_signal.emit(["pre", self.label_10.text()])

    def __next_page(self):
        """点击下一页信号"""
        self.control_signal.emit(["next", self.label_10.text()])

    def __final_page(self):
        """尾页点击信号"""
        self.control_signal.emit(["final", self.label_10.text()])

    def __confirm_skip(self):
        """跳转页码确定"""
        self.control_signal.emit(["confirm", self.lineEdit.text()])

    def page_controller(self, signal):
        total_page = self.showTotalPage()
        if "pre" == signal[0]:
            if 1 == int(signal[1]):
                definition_MessageBox("已经是第一页了")

                return
            self.label_10.setText(str(int(signal[1]) - 1))
        elif "next" == signal[0]:
            if total_page == int(signal[1]):
                definition_MessageBox("已经是最后一页了")

                return
            self.label_10.setText(str(int(signal[1]) + 1))
        elif "final" == signal[0]:

            self.label_10.setText(str(total_page))
        elif "confirm" == signal[0]:
            if not signal[1]:
                definition_MessageBox("请输入页数")

                return
            if total_page < int(signal[1]) or int(signal[1]) <= 0:
                definition_MessageBox("跳转页码超出范围")

                return
            self.label_10.setText(signal[1])

        self.changeTableContent()  # 改变表格内容

    def changeTableContent(self):
        current_index = self.stackedWidget.currentIndex()
        grade, Class, level = self.back_comboBox_result()
        if current_index == 0:
            if self.abnormal_flag:
                res, step_list = self.api.get_abnormal_data(self.page_count, int(self.label_10.text()),
                                                        time=self.lineEdit_time_3.text().strip(),
                                                        name=self.lineEdit_3.text().strip(),
                                                        phone=self.lineEdit_2.text().strip(),
                                                        grade=grade,
                                                        Class=Class,
                                                        level=level,
                                                        time_suffix=self.lineEdit_time_4.text().strip(),
                                                        )
            else:
                res, step_list = self.api.get_page_count_data(self.page_count, int(self.label_10.text()),
                                                              time=self.lineEdit_time_3.text().strip(),
                                                              name=self.lineEdit_3.text().strip(),
                                                              phone=self.lineEdit_2.text().strip(),
                                                              grade=grade,
                                                              Class=Class,
                                                              level=level,
                                                              time_suffix=self.lineEdit_time_4.text().strip(),
                                                              )
            self.isAllSelected = True
            self.tableWidget_2.horizontalHeaderItem(0).setText('全选')
            self.for_tabel_data(int(self.label_10.text()), step_list)
        else:
            check_state = self.comboBox_13.currentText()
            if check_state == "请选择":
                check_text = ""
            elif check_state == "已检查":
                check_text = 1
            else:
                check_text = 0

            school_text=self.comboBox_12.currentText()
            self.init_user_total_count(school_text,check_text)
            res, step_list = self.api.get_page_user_count_data(self.page_user_count, int(self.label_10.text()),
                                                               school_text,
                                                               name=self.lineEdit_3.text().strip(),
                                                               phone=self.lineEdit_2.text().strip(),
                                                               grade=grade,
                                                               Class=Class,
                                                                check=check_text,
                                                               )
            self.update_user_table(int(self.label_10.text()), step_list)


    def __init_user_table(self):
        '''
                初始化表格
                '''
        self.tableWidget_3.setStyleSheet("QWidget{font-size:9;}")
        self.tableWidget_3.clear()
        self.tableWidget_3.setShowGrid(False)
        self.tableWidget_3.installEventFilter(self)

        self.tableWidget_3.verticalHeader().setHidden(True)  # 去掉序号列
        self.tableWidget_3.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)  # 用户设置
        self.tableWidget_3.horizontalHeader().setStretchLastSection(True)  # 最后一列自适应

        self.tableWidget_3.setSelectionMode(QAbstractItemView.SingleSelection)  # 设置只能选中一行
        self.tableWidget_3.setSelectionBehavior(QAbstractItemView.SelectRows)  # 设置只有行选中

        self.tableWidget_3.setEditTriggers(QTableView.NoEditTriggers)  # 不可编辑

        self.tableWidget_3.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)  # 隐藏滚动条
        self.tableWidget_3.setFocusPolicy(Qt.NoFocus)

        self.tableWidget_3.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 设置表头点击事件
        header = self.tableWidget_3.horizontalHeader()
        header.sectionClicked.connect(self.handleHeaderClick)

        self.tableWidget_3.setMouseTracking(True)  # 启用鼠标追踪
        self.tableWidget_3.mouseMoveEvent = self.table_mouse  # 绑定鼠标移动事件
        self.tableWidget_3.mousePressEvent = self.table_press  # 绑定鼠标点击事件

        head_list = ["序号", "学号", "姓名", "性别", "年龄", "学校", "年级", "班级",
                     "检查状态"]
        head_list_cnt = len(head_list)
        self.tableWidget_3.setColumnCount(head_list_cnt)
        self.tableWidget_3.setHorizontalHeaderLabels(head_list)

        # 按比例设置宽度
        header = self.tableWidget_3.horizontalHeader()
        self.tableWidget_3.setColumnWidth(0, 60)
        header.setSectionResizeMode(0, QHeaderView.Fixed)

        for i in range(1, head_list_cnt):
            header.setSectionResizeMode(i, QHeaderView.Stretch)


    def __init_table(self):
        '''
        初始化表格
        '''
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

        self.tableWidget_2.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff) #隐藏滚动条
        self.tableWidget_2.setFocusPolicy(Qt.NoFocus)

        self.tableWidget_2.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 初始化全选标志
        self.isAllSelected = True
        # 设置表头点击事件
        header = self.tableWidget_2.horizontalHeader()
        header.sectionClicked.connect(self.handleHeaderClick)

        self.tableWidget_2.setMouseTracking(True)  # 启用鼠标追踪
        self.tableWidget_2.mouseMoveEvent = self.table_mouse  # 绑定鼠标移动事件
        self.tableWidget_2.mousePressEvent = self.table_press  # 绑定鼠标点击事件

        head_list = ["全选","序号","学号","姓名", "年级","班级","性别","年龄","焦虑得分","焦虑程度","抑郁得分","抑郁程度","检测次数","检测时间","操作"]

        self.head_list_cnt = len(head_list)
        self.tableWidget_2.setColumnCount(self.head_list_cnt),
        self.tableWidget_2.setHorizontalHeaderLabels(head_list)

        self.tableWidget2_width=self.tableWidget_2.width()
        self.tableWidget2_height = self.tableWidget_2.height()

        self.tableWidget_2.setColumnWidth(0, self.tableWidget2_width // 20)
        self.tableWidget_2.setColumnWidth(1, self.tableWidget2_width // 20)
        self.tableWidget_2.setColumnWidth(2, self.tableWidget2_width // 14)
        self.tableWidget_2.setColumnWidth(3, self.tableWidget2_width // 15)

        self.tableWidget_2.setColumnWidth(4, self.tableWidget2_width // 16)
        self.tableWidget_2.setColumnWidth(5, self.tableWidget2_width // 16)

        self.tableWidget_2.setColumnWidth(6, self.tableWidget2_width // 17)
        self.tableWidget_2.setColumnWidth(7, self.tableWidget2_width // 20)

        self.tableWidget_2.setColumnWidth(8, self.tableWidget2_width // 15)
        self.tableWidget_2.setColumnWidth(9, self.tableWidget2_width // 15)

        self.tableWidget_2.setColumnWidth(10, self.tableWidget2_width // 15)
        self.tableWidget_2.setColumnWidth(11, self.tableWidget2_width // 15)
        self.tableWidget_2.setColumnWidth(12, self.tableWidget2_width // 21)
        self.tableWidget_2.setColumnWidth(13, self.tableWidget2_width // 8)

        #self.tableWidget2_height // 31
        self.page_count = int(20)

        self.tableWidget_2.setRowCount(self.page_count)

        # for row in range(21):
        #     self.tableWidget_2.setRowHeight(row, self.tableWidget2_height/21 + 100)

        self.init_total_count()
        grade, Class, level = self.back_comboBox_result()
        if self.abnormal_flag:
            res, step_list = self.api.get_abnormal_data(self.page_count, int(self.label_10.text()),
                                                        time=self.lineEdit_time_3.text().strip(),
                                                        name=self.lineEdit_3.text().strip(),
                                                        phone=self.lineEdit_2.text().strip(),
                                                        grade=grade,
                                                        Class=Class,
                                                        level=level,
                                                        time_suffix=self.lineEdit_time_4.text().strip(),
                                                        )
        else:
            res,step_list=self.api.get_page_count_data(self.page_count, int(self.label_10.text()),time=self.lineEdit_time_3.text().strip(),name=self.lineEdit_3.text().strip(),phone=self.lineEdit_2.text().strip(),grade=grade,
                                                          Class=Class,
                                                          level=level,
                                                       time_suffix=self.lineEdit_time_4.text().strip(),
                                                       )

        self.for_tabel_data(int(self.label_10.text()),step_list)




    def showStretchOptions(self):
        current_index = self.stackedWidget.currentIndex()
        grade, Class, level = self.back_comboBox_result()
        if current_index == 0:
            self.init_total_count()
            self.label_10.setText("1")
            if self.abnormal_flag:
                res, step_list = self.api.get_abnormal_data(self.page_count, int(self.label_10.text()),
                                                        time=self.lineEdit_time_3.text().strip(),
                                                        name=self.lineEdit_3.text().strip(),
                                                        phone=self.lineEdit_2.text().strip(),
                                                        grade=grade,
                                                        Class=Class,
                                                        level=level,
                                                        time_suffix=self.lineEdit_time_4.text().strip(),
                                                        )
            else:
                res, step_list = self.api.get_page_count_data(self.page_count, int(self.label_10.text()),
                                                              time=self.lineEdit_time_3.text().strip(),
                                                              name=self.lineEdit_3.text().strip(),
                                                              phone=self.lineEdit_2.text().strip(),
                                                              grade=grade,
                                                              Class=Class,
                                                              level=level,
                                                              time_suffix=self.lineEdit_time_4.text().strip(),
                                                              )
            self.for_tabel_data(int(self.label_10.text()), step_list)
        else:

            check_state = self.comboBox_13.currentText()
            if check_state == "请选择":
                check_text = ""
            elif check_state == "已检查":
                check_text = 1
            else:
                check_text = 0

            school_text=self.comboBox_12.currentText()
            self.init_user_total_count(school_text,check_text)
            self.label_10.setText("1")

            res, step_list = self.api.get_page_user_count_data(self.page_user_count,                                                                         int(self.label_10.text()),
                                                                school_text,
                                                                name=self.lineEdit_3.text().strip(),
                                                                phone=self.lineEdit_2.text().strip(),
                                                                grade=grade,
                                                                Class=Class,
                                                                check=check_text,
                                                               )

            self.update_user_table(int(self.label_10.text()), step_list)

    def handleHeaderClick(self, logicalIndex):
        if logicalIndex == 0:  # 检查是否点击了第一个表头
            if self.isAllSelected:
                row = 0
                for i in range(0, self.page_count):
                    CheckBox = self.tableWidget_2.cellWidget(row, 0)
                    if CheckBox:
                        if not CheckBox.isChecked():
                            CheckBox.setChecked(True)
                    row += 1
                self.tableWidget_2.horizontalHeaderItem(0).setText('取消')
                self.isAllSelected =False
            else:
                row = 0
                for i in range(0, self.page_count):
                    CheckBox = self.tableWidget_2.cellWidget(row, 0)
                    if CheckBox:
                        if CheckBox.isChecked():
                            CheckBox.setChecked(False)
                    row += 1
                self.tableWidget_2.horizontalHeaderItem(0).setText('全选')
                self.isAllSelected=True


    def get_larger_number(self,a, b):
        """
        """
        if a > b:
            return a
        elif b > a:
            return b
        else:
            return a

    def for_tabel_data(self, current_page, step_list):
        self.tableWidget_2.clearContents()
        row = 0
        id = current_page * self.page_count - self.page_count + 1

        for data in step_list:
            if data["anxiety_score"] is None and data["depressed_score"] is None:
                color = QColor(255, 255, 255)
            else:
                if data["anxiety_score"] is None and data["depressed_score"] is not None:
                    number = data["depressed_score"]
                elif data["anxiety_score"] is not None and data["depressed_score"] is None:
                    number = data["anxiety_score"]
                else:
                    number=self.get_larger_number(data["anxiety_score"],data["depressed_score"])
                if 0 < number <50:
                    color = QColor(255, 255, 255)
                elif 50 <= number <65:
                    color = QColor(128, 128, 128)
                elif 65 <= number <75:
                    color = QColor(255, 165, 0)
                elif 75 <= number <= 100:
                    color = QColor(255, 0, 0)
                else:
                    color=QColor(255, 255, 255)

            col = 0
            checkBox = CheckBox(row, self, data, color)
            self.tableWidget_2.setCellWidget(row, col, checkBox)
            col += 1

            item = QTableWidgetItem(str(id))
            self.tableWidget_2.setItem(row, col, item)
            item.setTextAlignment(Qt.AlignCenter)
            item.setBackground(color)
            id+=1

            col += 1
            item = QTableWidgetItem(data["phone"])
            self.tableWidget_2.setItem(row, col, item)
            item.setTextAlignment(Qt.AlignCenter)
            item.setBackground(color)
            # 用户名
            col += 1
            item = QTableWidgetItem(data["name"])
            self.tableWidget_2.setItem(row, col, item)
            item.setTextAlignment(Qt.AlignCenter)
            item.setBackground(color)

            #年级
            col += 1
            item = QTableWidgetItem(data["grade"])
            self.tableWidget_2.setItem(row, col, item)
            item.setTextAlignment(Qt.AlignCenter)
            item.setBackground(color)

            #班级
            col += 1
            item = QTableWidgetItem(data["class"])
            self.tableWidget_2.setItem(row, col, item)
            item.setTextAlignment(Qt.AlignCenter)
            item.setBackground(color)

            # 用户类型
            col += 1
            item = QTableWidgetItem(data["sex"])
            self.tableWidget_2.setItem(row, col, item)
            item.setTextAlignment(Qt.AlignCenter)
            item.setBackground(color)
            # 备注信息
            col += 1


            item = QTableWidgetItem(str(data["age"]))
            self.tableWidget_2.setItem(row, col, item)
            item.setTextAlignment(Qt.AlignCenter)
            item.setBackground(color)

            # 操作
            col += 1
            if data["anxiety_score"] is None:
                item = QTableWidgetItem("")
            else:
                item = QTableWidgetItem(str(data["anxiety_score"]))
            self.tableWidget_2.setItem(row, col, item)
            item.setTextAlignment(Qt.AlignCenter)
            item.setBackground(color)

            col += 1
            item = QTableWidgetItem(data["anxiety_result"])
            self.tableWidget_2.setItem(row, col, item)
            item.setTextAlignment(Qt.AlignCenter)
            item.setBackground(color)

            col += 1
            if data["depressed_score"] is None:
                item = QTableWidgetItem("")
            else:
                item = QTableWidgetItem(str(data["depressed_score"]))
            self.tableWidget_2.setItem(row, col, item)
            item.setTextAlignment(Qt.AlignCenter)
            item.setBackground(color)

            col += 1
            item = QTableWidgetItem(data["depressed_result"])
            self.tableWidget_2.setItem(row, col, item)
            item.setTextAlignment(Qt.AlignCenter)
            item.setBackground(color)

            col += 1
            if data["count"] is None:
                item = QTableWidgetItem(data["count"])
            else:
                item = QTableWidgetItem(str(data["count"]))
            self.tableWidget_2.setItem(row, col, item)
            item.setTextAlignment(Qt.AlignCenter)
            item.setBackground(color)

            col += 1
            item = QTableWidgetItem(data["createtime"])
            self.tableWidget_2.setItem(row, col, item)
            item.setTextAlignment(Qt.AlignCenter)
            item.setBackground(color)

            col += 1
            custwidget = CustomWidget(row, self,data,color)
            self.tableWidget_2.setCellWidget(row, col, custwidget)

            row += 1

            if row == self.page_count:

                return
    def init_total_count(self):
        '''
        计算总页数
        '''
        grade, Class, level = self.back_comboBox_result()
        if self.abnormal_flag:
            res, cnt,total_cnt = self.api.get_abnormal_count_page(self.lineEdit_2.text().strip(),self.lineEdit_3.text().strip(),self.lineEdit_time_3.text().strip(),self.lineEdit_time_4.text().strip(),grade,Class,level,self.page_count)
        else:
            res, cnt,total_cnt = self.api.get_count_page(self.lineEdit_2.text().strip(),self.lineEdit_3.text().strip(),self.lineEdit_time_3.text().strip(),self.lineEdit_time_4.text().strip(),grade,Class,level,self.page_count)

        if res:
            self.cnt=cnt
            self.label_13.setText(f"{cnt}页,共{total_cnt}条记录")

    def init_user_total_count(self,school_text,check_text):
        '''
        计算总页数
        '''
        grade, Class, level = self.back_comboBox_result()
        res, cnt,total_cnt = self.api.get_user_count_page(self.page_user_count,
                                                           school_text,
                                                           self.lineEdit_3.text().strip(),
                                                           self.lineEdit_2.text().strip(),
                                                           grade,
                                                           Class,
                                                          check_text
                                                           )
        if res:
            self.cnt=cnt
            self.label_13.setText(f"{cnt}页,共{total_cnt}条记录")

    def table_press(self, event):
        current_index = self.stackedWidget.currentIndex()

        if current_index == 0:
            item = self.tableWidget_2.itemAt(event.pos())
            if item is not None:
                row = item.row()
                self.Row = row
                self.tableWidget_2.clearSelection()  # 取消选中状态
                self.clearHoverEffects()
                if item is not None:
                    self.tableWidget_2.setCurrentCell(row, 0)
                    self.tableWidget_2.itemClicked.emit(item)  # 手动触发itemClicked信号
        else:
            item = self.tableWidget_3.itemAt(event.pos())
            if item is not None:
                row = item.row()
                self.Row = row
                self.tableWidget_3.clearSelection()  # 取消选中状态
                self.clearHoverEffects()
                if item is not None:
                    self.tableWidget_3.itemClicked.emit(item)  # 手动触发itemClicked信号

        super().mousePressEvent(event)

    def table_mouse(self, event):
        current_index = self.stackedWidget.currentIndex()

        if current_index == 0:
            item = (self.tableWidget_2.
                    itemAt(event.pos()))

            if item is not None:
                row = item.row()
                self.row=row

                self.clearHoverEffects()  # 清除之前的悬停效果

                for col in range(self.tableWidget_2.columnCount()):
                    if col == 0:
                        self.tableWidget_2.cellWidget(row, col).setStyleSheet(
                            "background-color: rgb(217, 235, 249);color:rgb(0, 0, 255);padding-left: 30px;")
                        continue
                    if col == 14:
                        self.tableWidget_2.cellWidget(row, col).setStyleSheet(
                            "background-color: rgb(217, 235, 249);color:rgb(0, 0, 255;)")
                        continue

                    self.tableWidget_2.item(row, col).setBackground(QColor(217, 235, 249))  # 设置当前行的悬停效果
        else:
            item = (self.tableWidget_3.
                    itemAt(event.pos()))
            if item is not None:
                row = item.row()
                self.row = row
                self.clearHoverEffects()  # 清除之前的悬停效果
                for col in range(self.tableWidget_3.columnCount()):
                    self.tableWidget_3.item(row, col).setBackground(QColor(217, 235, 249))  # 设置当前行的悬停效果

        super().mouseMoveEvent(event)

    def clearHoverEffects(self):
        current_index = self.stackedWidget.currentIndex()

        if current_index == 0:
            for row_index in range(self.tableWidget_2.rowCount()):
                if self.Row == row_index:
                    continue


                item_2 = self.tableWidget_2.item(row_index, 10)
                item_3 = self.tableWidget_2.item(row_index, 8)

                if item_2 is not None and item_3 is not None:
                    if item_3.text()=="" and item_2.text()=="":
                        for col in range(self.tableWidget_2.columnCount()):
                            item = self.tableWidget_2.item(row_index, col)
                            cell_widget = self.tableWidget_2.cellWidget(row_index, col)
                            if item is None and cell_widget is None:
                                break
                            if col == 0:
                                self.tableWidget_2.cellWidget(row_index, col).setStyleSheet(
                                    "background-color: rgb(255,255,255);color:rgb(0, 0, 255);padding-left: 30px;")
                                continue
                            if col == 14:
                                self.tableWidget_2.cellWidget(row_index, col).setStyleSheet(
                                    "background-color: rgb(255,255,255);color:rgb(0, 0, 255);")
                                continue
                            self.tableWidget_2.item(row_index, col).setBackground(QColor(255, 255, 255))  # 恢复原始背景色
                    else:
                        if item_3.text()=="" and item_2.text()!="":
                            number=float(item_2.text())
                        elif item_3.text()!="" and item_2.text()=="":
                            number = float(item_3.text())
                        else:
                            value_1 = float(item_3.text())
                            value_2 = float(item_2.text())
                            number = self.get_larger_number(value_1, value_2)
                        if 0 < number <50:
                            color = QColor(255, 255, 255)
                        elif 50 <= number <65:
                            color = QColor(128, 128, 128)
                        elif 65 <= number <75:
                            color = QColor(255, 165, 0)
                        elif 75 <= number <= 100:
                            color = QColor(255, 0, 0)
                        else:
                            color = QColor(255, 255, 255)

                        for col in range(self.tableWidget_2.columnCount()):
                            item = self.tableWidget_2.item(row_index, col)
                            cell_widget = self.tableWidget_2.cellWidget(row_index, col)
                            if item is None and cell_widget is None:
                                break
                            if col == 0:
                                rgb_value = 'rgb({}, {}, {})'.format(color.red(), color.green(), color.blue())
                                self.tableWidget_2.cellWidget(row_index, col).setStyleSheet(
                                    "background-color: {};padding-left: 30px;".format(rgb_value))
                                continue
                            if col==14:
                                rgb_value = 'rgb({}, {}, {})'.format(color.red(), color.green(), color.blue())
                                self.tableWidget_2.cellWidget(row_index, col).setStyleSheet(
                                    "background-color: {};".format(rgb_value))
                                continue
                            self.tableWidget_2.item(row_index, col).setBackground(color)  # 设置当前行的悬停效果
        else:
            for row_index in range(self.tableWidget_3.rowCount()):
                if self.Row == row_index:
                    continue

                for col in range(self.tableWidget_3.columnCount()):
                    item = self.tableWidget_3.item(row_index, col)
                    if item is not None:  # 检查 item 是否为 None
                        item.setBackground(QColor(255,255,255))  # 设置当前行的悬停效果

    def eventFilter(self, obj, event):
        '''事件过滤
        '''
        event_type = event.type()


        if event_type == QtCore.QEvent.MouseButtonPress and event.buttons() == QtCore.Qt.LeftButton:
            if obj==self.lineEdit_time_3:
                if self.calendar is None:
                    self.calendar = QCalendarWidget(self)
                    self.calendar.setWindowFlags(self.calendar.windowFlags() | QtCore.Qt.Popup)
                    self.calendar.clicked.connect(self.selectDate)
                    self.calendar.setMinimumDate(QtCore.QDate(1900, 1, 1))  # 设置日期范围
                    self.calendar.setMaximumDate(QtCore.QDate(2100, 12, 31))
                    self.calendar.setSelectedDate(QtCore.QDate.currentDate())  # 设置默认选择当前日期
                    # 将日历选择器显示在 QLineEdit 下方
                    pos = self.lineEdit_time_3.mapToGlobal(self.lineEdit_time_3.rect().bottomLeft())
                    self.calendar.move(pos)
                self.calendar.show()

            elif obj == self.lineEdit_time_4:
                if self.calendar_2 is None:
                    self.calendar_2 = QCalendarWidget(self)
                    self.calendar_2.setWindowFlags(self.calendar_2.windowFlags() | QtCore.Qt.Popup)
                    self.calendar_2.clicked.connect(self.selectDate_2)
                    self.calendar_2.setMinimumDate(QtCore.QDate(1900, 1, 1))  # 设置日期范围
                    self.calendar_2.setMaximumDate(QtCore.QDate(2100, 12, 31))
                    self.calendar_2.setSelectedDate(QtCore.QDate.currentDate())  # 设置默认选择当前日期
                    # 将日历选择器显示在 QLineEdit 下方
                    pos = self.lineEdit_time_4.mapToGlobal(self.lineEdit_time_4.rect().bottomLeft())
                    self.calendar_2.move(pos)
                self.calendar_2.show()

            elif obj==self.label_32:
                self.lineEdit_time_3.setText("")
                self.lineEdit_time_4.setText("")
                self.init_total_count()
                self.label_10.setText("1")
                grade, Class, level = self.back_comboBox_result()
                if self.abnormal_flag:
                    res, step_list = self.api.get_abnormal_data(self.page_count, int(self.label_10.text()),
                                                            time=self.lineEdit_time_3.text().strip(),
                                                            name=self.lineEdit_3.text().strip(),
                                                            phone=self.lineEdit_2.text().strip(),
                                                            grade=grade,
                                                            Class=Class,
                                                            level=level,
                                                            time_suffix=self.lineEdit_time_4.text().strip(),

                                                            )
                else:
                    res, step_list = self.api.get_page_count_data(self.page_count, int(self.label_10.text()),
                                                                  time=self.lineEdit_time_3.text().strip(),
                                                                  name=self.lineEdit_3.text().strip(),
                                                                  phone=self.lineEdit_2.text().strip(),
                                                                  grade=grade,
                                                                  Class=Class,
                                                                  level=level,
                                                                time_suffix=self.lineEdit_time_4.text().strip(),)
                self.for_tabel_data(int(self.label_10.text()), step_list)


        return QObject.eventFilter(self, obj, event)  # 交由其他控件处理

    def selectDate_2(self, date):
        # 选择日期后将日期填充到 QLineEdit 中
        selected_date = date.toString("yyyy-MM-dd")
        self.lineEdit_time_4.setText(selected_date)
        self.calendar_2.hide()

        time_prefix = self.lineEdit_time_3.text().strip()
        time_suffix = self.lineEdit_time_4.text().strip()
        if (time_prefix != "" and time_suffix == "") or (time_prefix == "" and time_suffix != ""):
            return
        if time_prefix != "" and time_suffix != "":
            prefix = datetime.strptime(time_prefix, '%Y-%m-%d')
            suffix = datetime.strptime(time_suffix, '%Y-%m-%d')
            # 比较日期
            if prefix > suffix:
                definition_MessageBox("时间校准有误")
                self.lineEdit_time_4.setText("")
                return

        self.init_total_count()
        self.label_10.setText("1")
        grade, Class, level = self.back_comboBox_result()
        if self.abnormal_flag:
            res, step_list = self.api.get_abnormal_data(self.page_count, int(self.label_10.text()),
                                                    time=time_prefix,
                                                    name=self.lineEdit_3.text().strip(),
                                                    phone=self.lineEdit_2.text().strip(),
                                                    grade=grade,
                                                    Class=Class,
                                                    level=level,
                                                    time_suffix=time_suffix
                                                    )
        else:
            res, step_list = self.api.get_page_count_data(self.page_count, int(self.label_10.text()),
                                                          time= time_prefix,
                                                          name=self.lineEdit_3.text().strip(),
                                                          phone=self.lineEdit_2.text().strip(),
                                                          grade=grade,
                                                          Class=Class,
                                                          level=level,
                                                          time_suffix=time_suffix
                                                          )
        self.for_tabel_data(int(self.label_10.text()), step_list)

    def selectDate(self, date):
        # 选择日期后将日期填充到 QLineEdit 中
        selected_date = date.toString("yyyy-MM-dd")
        self.lineEdit_time_3.setText(selected_date)
        self.calendar.hide()

        time_prefix = self.lineEdit_time_3.text().strip()
        time_suffix = self.lineEdit_time_4.text().strip()
        if (time_prefix != "" and time_suffix == "") or (time_prefix == "" and time_suffix != ""):
            return
        if time_prefix != "" and time_suffix != "":
            prefix = datetime.strptime(time_prefix, '%Y-%m-%d')
            suffix = datetime.strptime(time_suffix, '%Y-%m-%d')
            # 比较日期
            if prefix > suffix:
                definition_MessageBox("时间校准有误")
                self.lineEdit_time_4.setText("")
                return

        self.init_total_count()
        self.label_10.setText("1")
        grade, Class, level = self.back_comboBox_result()
        if self.abnormal_flag:
            res, step_list = self.api.get_abnormal_data(self.page_count, int(self.label_10.text()),
                                                    time=time_prefix,
                                                    name=self.lineEdit_3.text().strip(),
                                                    phone=self.lineEdit_2.text().strip(),
                                                    grade=grade,
                                                    Class=Class,
                                                    level=level,
                                                    time_suffix=time_suffix,
                                                    )
        else:
            res, step_list = self.api.get_page_count_data(self.page_count, int(self.label_10.text()),
                                                          time=self.lineEdit_time_3.text().strip(),
                                                          name=self.lineEdit_3.text().strip(),
                                                          phone=self.lineEdit_2.text().strip(),
                                                          grade=grade,
                                                          Class=Class,
                                                          level=level,
                                                          time_suffix=self.lineEdit_time_4.text().strip(),
                                                          )
        self.for_tabel_data(int(self.label_10.text()), step_list)

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
                   [self.comboBox_11, self.comboBox_10, self.comboBox_9,self.comboBox_13,self.comboBox_12]):
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
class CheckBox(QCheckBox):
    def __init__(self, row, data, data_dict, color, parent=None):
        super().__init__(parent)

        self.data = data
        self.row = row
        self.data_dict = data_dict
        color_str = color.name()  # 将 QColor 转换为字符串
        self.setStyleSheet(f"""
                        background-color: {color_str};
                        padding-left: 30px;
                    """)
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        '''事件过滤
        '''
        if isinstance(event, QMouseEvent) and event.buttons() == QtCore.Qt.LeftButton:  # 鼠标左键点击此控件时

            item = self.data.tableWidget_2.item(self.row, 13)
            self.data.Row = self.row
            self.data.tableWidget_2.clearSelection()  # 取消选中状态
            self.data.clearHoverEffects()
            self.data.tableWidget_2.setCurrentCell(self.row, 1)
            self.data.tableWidget_2.itemClicked.emit(item)  # 手动触发itemClicked信号

        return QObject.eventFilter(self, obj, event)  # 交由其他控件处理


class CustomWidget(QWidget):
    def __init__(self,row,data,data_dict,color):
        super().__init__()

        self.initUI()
        self.data=data
        self.row=row
        self.data_dict=data_dict
        self.color=color
        rgb_value = 'rgb({}, {}, {})'.format(self.color.red(), self.color.green(), self.color.blue())
        self.setStyleSheet(
            "background-color: {};".format(rgb_value))

    def initUI(self):
        # 创建四个 QLabel
        self.label1 = QLabel('查看报告', self)
        self.label2 = QLabel('删除报告', self)

        font = QFont('Microsoft YaHei', 9)

        self.label1.setFont(font)
        self.label2.setFont(font)

        self.label2.setStyleSheet("QLabel {color:#92c3ff;}")
        self.label1.setStyleSheet("QLabel {color:#92c3ff;}")

        self.label1.installEventFilter(self)
        self.label2.installEventFilter(self)

        # 创建一个 QHBoxLayout 布局
        layout = QHBoxLayout(self)
        layout.addWidget(self.label1)
        layout.addWidget(self.label2)
        layout.setContentsMargins(0, 0, 0,0)
        layout.setSpacing(0)

        self.setLayout(layout)


    def eventFilter(self, obj, event):
        '''事件过滤
        '''
        event_type = event.type()

        if isinstance(event, QMouseEvent) and event.buttons() == QtCore.Qt.LeftButton: #鼠标左键点击此控件时

            item = self.data.tableWidget_2.item(self.row, 11)
            self.data.Row = self.row
            self.data.tableWidget_2.clearSelection()  # 取消选中状态
            self.data.clearHoverEffects()
            self.data.tableWidget_2.setCurrentCell(self.row, 0)
            self.data.tableWidget_2.itemClicked.emit(item)  # 手动触发itemClicked信号

            if obj == self.label1: #查看
                self.report=Report(self.data_dict["phone"],self.data_dict["count"],self.data.api,self.data_dict["name"])

            elif obj==self.label2: #删除
                msg_box,yes_button,no_button=select_definition_MessageBox("是否要删除此信息？")
                # 检查哪个按钮被点击
                if msg_box.clickedButton() == yes_button:
                    res=self.data.api.delete_medical_data(self.data_dict["phone"],self.data_dict["count"],self.data_dict["createtime"])
                    if res:
                        self.data.init_total_count()
                        grade, Class, level = self.data.back_comboBox_result()
                        if self.data.abnormal_flag:
                            res, step_list = self.data.api.get_abnormal_data(self.data.page_count, int(self.data.label_10.text()),
                                                                        time=self.data.lineEdit_time_3.text().strip(),
                                                                        name=self.data.lineEdit_3.text().strip(),
                                                                        phone=self.data.lineEdit_2.text().strip(),
                                                                        grade=grade,
                                                                        Class=Class,
                                                                        level=level,
                                                                        time_suffix=self.data.lineEdit_time_4.text().strip(),)
                        else:
                            res, step_list = self.data.api.get_page_count_data(self.data.page_count, int(self.data.label_10.text()),
                                                                          time=self.data.lineEdit_time_3.text().strip(),
                                                                          name=self.data.lineEdit_3.text().strip(),
                                                                          phone=self.data.lineEdit_2.text().strip(),grade=grade,
                                                          Class=Class,
                                                          level=level,
                                                        time_suffix=self.data.lineEdit_time_4.text().strip(),)
                        self.data.for_tabel_data(int(self.data.label_10.text()), step_list)

                elif msg_box.clickedButton() == no_button:
                    pass
                    #if res:
                        #更新table表
                        #pass

        return QObject.eventFilter(self, obj, event)  # 交由其他控件处理

    def enterEvent(self, event):
        if self.data.row:
            selected_row = ""
            selected_items = self.data.tableWidget_2.selectedItems()
            if selected_items:
                selected_row = selected_items[0].row()
            if selected_row == self.data.row:
                pass
            else:
                for col in range(self.data.tableWidget_2.columnCount()):
                    item = self.data.tableWidget_2.item(self.data.row, col)
                    cell_widget = self.data.tableWidget_2.cellWidget(self.data.row, col)
                    if item is None and cell_widget is None:
                        break
                    if col == 0:
                        self.data.tableWidget_2.cellWidget(self.row, col).setStyleSheet(
                            "background-color: rgb(255,255,255);color:rgb(0, 0, 255);padding-left: 30px;")
                        continue
                    if col == 14:
                        self.data.tableWidget_2.cellWidget(self.data.row, col).setStyleSheet(
                            "background-color: rgb(255,255,255);color:rgb(0, 0, 255);")
                        continue
                    self.data.tableWidget_2.item(self.data.row, col).setBackground(QColor(255,255,255))  # 恢复原始背景色

        for col in range(self.data.tableWidget_2.columnCount()):
            if col == 0:
                self.data.tableWidget_2.cellWidget(self.row, col).setStyleSheet(
                    "background-color: rgb(217, 235, 249);color:rgb(0, 0, 255);padding-left: 30px;")
                continue
            if col == 14:
                self.data.tableWidget_2.cellWidget(self.row, col).setStyleSheet(
                    "background-color: rgb(217, 235, 249);color:rgb(0, 0, 255;)")
                continue

            self.data.tableWidget_2.item(self.row, col).setBackground(QColor(217, 235, 249))  # 设置当前行的悬停效果

    def leaveEvent(self, event):
        self.clearHoverEffects()  # 清除之前的悬停效果

    def clearHoverEffects(self):
        selected_items = self.data.tableWidget_2.selectedItems()
        if selected_items:
            selected_row = selected_items[0].row()
            if selected_row == self.row:
                return

        item_2 = self.data.tableWidget_2.item(self.row, 10)
        item_3 = self.data.tableWidget_2.item(self.row, 8)

        if item_2 is not None and item_3 is not None:
            if item_3.text() == "" and item_2.text() == "":
                for col in range(self.data.tableWidget_2.columnCount()):
                    item = self.data.tableWidget_2.item(self.row, col)
                    cell_widget = self.data.tableWidget_2.cellWidget(self.row, col)
                    if item is None and cell_widget is None:
                        break
                    if col==0:
                        self.data.tableWidget_2.cellWidget(self.row, col).setStyleSheet(
                            "background-color: rgb(255,255,255);color:rgb(0, 0, 255);padding-left: 30px;")
                        continue
                    if col == 14:
                        self.data.tableWidget_2.cellWidget(self.row, col).setStyleSheet(
                            "background-color: rgb(255,255,255);color:rgb(0, 0, 255);")
                        continue
                    self.data.tableWidget_2.item(self.row, col).setBackground(QColor(255, 255, 255))  # 恢复原始背景色
            else:

                if item_3.text() == "" and item_2.text() != "":
                    number = float(item_2.text())
                elif item_3.text() != "" and item_2.text() == "":
                    number = float(item_3.text())
                else:
                    value_1 = float(item_3.text())
                    value_2 = float(item_2.text())
                    number = self.data.get_larger_number(value_1, value_2)
                if 0 < number <50:
                    color = QColor(255, 255, 255)
                elif 50 <= number <65:
                    color = QColor(128, 128, 128)
                elif 65 <= number <75:
                    color = QColor(255, 165, 0)
                elif 75 <= number <= 100:
                    color = QColor(255, 0, 0)
                else:
                    color = QColor(255, 255, 255)
                for col in range(self.data.tableWidget_2.columnCount()):
                    item = self.data.tableWidget_2.item(self.row, col)
                    cell_widget = self.data.tableWidget_2.cellWidget(self.row, col)
                    if item is None and cell_widget is None:
                        break
                    if col==0:
                        rgb_value = 'rgb({}, {}, {})'.format(color.red(), color.green(), color.blue())
                        self.data.tableWidget_2.cellWidget(self.row, col).setStyleSheet(
                            "background-color: {};padding-left: 30px;".format(rgb_value))
                        continue
                    if col == 14:
                        rgb_value = 'rgb({}, {}, {})'.format(color.red(), color.green(), color.blue())
                        self.data.tableWidget_2.cellWidget(self.row, col).setStyleSheet(
                            "background-color: {};".format(rgb_value))
                        continue
                    self.data.tableWidget_2.item(self.row, col).setBackground(color)  # 设置当前行的悬停效果


        # for col in range(self.data.tableWidget_2.columnCount()):
        #     item = self.data.tableWidget_2.item(self.row, col)
        #     cell_widget = self.data.tableWidget_2.cellWidget(self.row, col)
        #     if item is None and cell_widget is None:
        #         break
        #
        #     if col == 11:
        #         self.data.tableWidget_2.cellWidget(self.row, col).setStyleSheet(
        #             "background-color: rgb(255,255,255);color:rgb(0, 0, 255);")
        #         continue
        #     self.data.tableWidget_2.item(self.row, col).setBackground(QColor(255,255,255))  # 恢复原始背景色

def styletest(borders, left, right, top, bottom):
    borders.left = left
    borders.right = right
    borders.top = top
    borders.bottom = bottom
    borders.bottom_colour = 0x3A

class CustomProgressDialog(QProgressDialog):
    def __init__(self, labelText, cancelText, min, max, parent=None):
        super().__init__(labelText, cancelText, min, max, parent)
        # 直接隐藏默认取消按钮
        self.setCancelButton(None)
        self.parent=parent
        self.setWindowModality(Qt.WindowModal)
        self.setWindowTitle("导出")
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

