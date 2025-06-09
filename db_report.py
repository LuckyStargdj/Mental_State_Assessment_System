import ctypes
import json
import os
from datetime import datetime

import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QSizeF, QSize, pyqtSignal, QObject, QPoint
from PyQt5.QtGui import QIcon, QPainter, QCursor, QFont, QPixmap, QTextCharFormat, QFontMetrics, QMouseEvent, QColor
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QScrollArea, QListWidgetItem, QVBoxLayout, QHeaderView, \
    QAbstractItemView, QTableView, QTableWidgetItem, QLabel, QHBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.ticker import AutoMinorLocator
import pandas as pd
from config.config import set_file_path
import random
from gui.left_egg import Ui_left_eeg_form
from gui.main_report import Ui_report_Form
from gui.new_report import Ui_new_report
from gui.report import Ui_report_item
# from utils.utils import *
from utils.utils import wait_noblock, select_definition_MessageBox, definition_MessageBox
from matplotlib.figure import Figure
from utils.logger import logger
from get_path import get_actual_path

class Report(QWidget, Ui_report_Form):
    update_signal = pyqtSignal(str, int,str)  # 定义信号
    def __init__(self, phone, count, api, name, is_show=True):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)  # 无边框
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.frame.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowIcon(QIcon(":/icon/res/logo.png"))
        self.setWindowTitle('报告')

        screen_resolution = self.screen().geometry()
        screen_width = screen_resolution.width()
        screen_height = screen_resolution.height()
        width = int(screen_width * 0.8)
        height = screen_height * 0.9
        self.setGeometry(0, 0, width, height)

        with open(set_file_path, 'r', encoding='utf-8') as file:
            self.settings = json.load(file)

        self.pbhide_5.setMouseTracking(True)
        self.pbhide_5.setToolTip("窗口最小化")
        self.pbhide_5.clicked.connect(self.showMinimized)

        self.pbClose_5.setMouseTracking(True)
        self.pbClose_5.setToolTip("关闭程序")
        self.pbClose_5.clicked.connect(self.close)

        self.phone = phone
        self.count = count
        self.api = api
        self.name = name

        self.print_button_3.clicked.connect(self.check_report) #检测报告
        self.save_button_3.clicked.connect(self.historical_statistics) #历史统计
        #self.save_button_3.hide()
        self.is_show = is_show

        self.print_button_6.clicked.connect(self.printCurrentTabScreenshot)
        self.save_button_6.clicked.connect(lambda: self.export_pdf_file())
        self.update_signal.connect(self.update_ui)  # 连接信号到槽

        self.update_signal.emit(phone, count, name)
        self.Row = ""
        self.row = ""

        self.print_button_3.setChecked(True)
        self.label_7.setStyleSheet("background-color: #3498db;")
        self.m_Position = QPoint()
        if is_show:
            font = QFont("微软雅黑", 10)
            self.textEdit.setFont(font)
            self.textEdit.setReadOnly(True)
            self.__init_table()  # 初始化表格

            self.verticalLayout_20 = QVBoxLayout(self)
            self.canvas = PlotCanvas_2(self)
            self.verticalLayout_20.addWidget(self.canvas)
            self.canvas.plot()
            self.widget.setLayout(self.verticalLayout_20)

            self.center()
        self.show()

    def __init_table(self):
        '''
        初始化表格
        '''
        self.tableWidget.setStyleSheet("QWidget{font-size:9;}")
        self.tableWidget.clear()
        self.tableWidget.setShowGrid(False)
        self.tableWidget.setRowCount(0)

        self.tableWidget.verticalHeader().setHidden(True)  # 去掉序号列
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)  # 用户设置
        #self.tableWidget.horizontalHeader().setStretchLastSection(True)  # 最后一列自适应
        self.tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)  # 设置只能选中一行
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)  # 设置只有行选中
        self.tableWidget.setEditTriggers(QTableView.NoEditTriggers)  # 不可编辑
        self.tableWidget.setFocusPolicy(Qt.NoFocus)

        head_list = ["检测次数", '检测时间', "检测设备", '焦虑得分', '焦虑程度',"抑郁得分","抑郁程度"]
        self.head_list_cnt = len(head_list)
        self.tableWidget.setColumnCount(self.head_list_cnt)
        self.tableWidget.setHorizontalHeaderLabels(head_list)

        self.tableWidget.setMouseTracking(True)  # 启用鼠标追踪
        self.tableWidget.mouseMoveEvent = self.table_mouse  # 绑定鼠标移动事件
        self.tableWidget.mousePressEvent = self.table_press  # 绑定鼠标点击事件

        # 按比例设置宽度
        header = self.tableWidget.horizontalHeader()
        # 设置固定宽度的列
        fixed_columns = [1]
        for index in fixed_columns:
            self.tableWidget.setColumnWidth(index, 270)
            header.setSectionResizeMode(index, QHeaderView.Fixed)

        # 设置可按比例伸缩的列
        stretch_columns = [0, 2, 3, 4, 5, 6]  # '检测时间' 和 '操作' 列
        for index in stretch_columns:
            header.setSectionResizeMode(index, QHeaderView.Stretch)



    def table_press(self, event):
        item = self.tableWidget.itemAt(event.pos())
        if item is not None:
            row = item.row()
            self.Row = row
            self.tableWidget.clearSelection()  # 取消选中状态
            self.clearHoverEffects()
            if item is not None:
                self.tableWidget.itemClicked.emit(item)  # 手动触发itemClicked信号

        super().mousePressEvent(event)

    def table_mouse(self, event):
        item = self.tableWidget.itemAt(event.pos())

        if item is not None:
            row = item.row()
            self.row = row

            self.clearHoverEffects()  # 清除之前的悬停效果

            for col in range(self.tableWidget.columnCount()):
                self.tableWidget.item(row, col).setBackground(QColor(217, 235, 249))  # 设置当前行的悬停效果



        super().mouseMoveEvent(event)

    def clearHoverEffects(self):
        for row_index in range(self.tableWidget.rowCount()):
            if self.Row == row_index:
                continue
            for col in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row_index, col)
                cell_widget = self.tableWidget.cellWidget(row_index, col)
                if item is None and cell_widget is None:
                    break

                self.tableWidget.item(row_index, col).setBackground(QColor(255,255,255))  # 恢复原始背景色

    def update_template_table(self):
        '''
                更新数据库表
                '''
        self.tableWidget.clearContents()
        row = 0

        if len(self.step_list):
            self.tableWidget.setRowCount(len(self.step_list))
        else:
            self.tableWidget.setRowCount(0)

        for info in self.step_list:
            # 检测次数
            col = 0
            item = QTableWidgetItem("第"+str(info["count"])+"次")
            self.tableWidget.setItem(row, col, item)
            item.setTextAlignment(Qt.AlignCenter)

            # 检测时间
            col += 1
            item = QTableWidgetItem(info["createtime"])
            self.tableWidget.setItem(row, col, item)
            item.setTextAlignment(Qt.AlignCenter)

            # 检测设备
            col += 1
            item = QTableWidgetItem(info["com"])
            self.tableWidget.setItem(row, col, item)
            item.setTextAlignment(Qt.AlignCenter)

            # 焦虑得分
            col += 1
            item = QTableWidgetItem(str(info['anxiety_score']))
            self.tableWidget.setItem(row, col, item)
            item.setTextAlignment(Qt.AlignCenter)

            # 焦虑程度
            col += 1
            item = QTableWidgetItem(info['anxiety_result'])
            self.tableWidget.setItem(row, col, item)
            item.setTextAlignment(Qt.AlignCenter)

            #抑郁得分
            col += 1
            item = QTableWidgetItem(str(info['depressed_score']))
            self.tableWidget.setItem(row, col, item)
            item.setTextAlignment(Qt.AlignCenter)

            #抑郁程度
            col += 1
            item = QTableWidgetItem(info['depressed_result'])
            self.tableWidget.setItem(row, col, item)
            item.setTextAlignment(Qt.AlignCenter)

            row += 1

    def check_report(self):
        if self.print_button_3.isChecked():
            self.label_7.setStyleSheet("background-color: #3498db;")
            self.label_10.setStyleSheet("background-color: transparent;")
            self.stackedWidget.setCurrentIndex(0)
            self.save_button_3.setChecked(False)
        else:
            pass
            #self.label_7.setStyleSheet("background-color: transparent;")


    def historical_statistics(self):
        if self.save_button_3.isChecked():
            self.label_10.setStyleSheet("background-color: #3498db;")
            self.label_7.setStyleSheet("background-color: transparent;")
            self.stackedWidget.setCurrentIndex(1)
            self.print_button_3.setChecked(False)
            self.label_15.setText(f"检测报告(共{len(self.step_list)}次)")
            self.update_template_table()
            self.__init_text()
        else:
            pass
            #self.label_10.setStyleSheet("background-color: transparent;")


    def __init_text(self):
        '''
        初始化数据
        :return:
        '''
        depressed_zc = []
        depressed_qd = []
        depressed_zhongdu = []
        depressed_zd = []

        anxiety_zc = []
        anxiety_qd = []
        anxiety_zhongdu = []
        anxiety_zd = []

        anxiety_score=""
        depressed_score=""
        anxiety_previous_score = ""
        depressed_previous_score = ""
        for i in range(0,len(self.step_list)):
            if len(self.step_list)>=2:
                if i==len(self.step_list)-2:
                    depressed_previous_score = self.step_list[i]["depressed_score"]
                    anxiety_previous_score = self.step_list[i]["anxiety_score"]
            if i==len(self.step_list)-1:
                depressed_score=self.step_list[i]["depressed_score"]
                anxiety_score=self.step_list[i]["anxiety_score"]
            if self.step_list[i]["anxiety_result"]=="正常":
                anxiety_zc.append("正常")
            elif self.step_list[i]["anxiety_result"]=="轻度":
                anxiety_qd.append("轻度")
            elif self.step_list[i]["anxiety_result"]=="中度":
                anxiety_zhongdu.append("中度")
            elif self.step_list[i]["anxiety_result"]=="重度":
                anxiety_zd.append("重度")

            if self.step_list[i]["depressed_result"]=="正常":
                depressed_zc.append("正常")
            elif self.step_list[i]["depressed_result"]=="轻度":
                depressed_qd.append("轻度")
            elif self.step_list[i]["depressed_result"]=="中度":
                depressed_zhongdu.append("中度")
            elif self.step_list[i]["depressed_result"]=="重度":
                depressed_zd.append("重度")

        anxiety=""
        if len(anxiety_zc) == len(self.step_list):
            anxiety = "均为正常"
        elif len(anxiety_qd) == len(self.step_list):
            anxiety = "均为轻度抑郁"
        elif len(anxiety_zhongdu) == len(self.step_list):
            anxiety = "均为中度抑郁"
        elif len(anxiety_zd) ==len(self.step_list):
            anxiety = "均为重度抑郁"
        else:
            parts = []
            if len(anxiety_qd) != 0:
                parts.append(f"{len(anxiety_qd)}次轻度")
            if len(anxiety_zhongdu) != 0:
                parts.append(f"{len(anxiety_zhongdu)}次中度")
            if len(anxiety_zd) != 0:
                parts.append(f"{len(anxiety_zd)}次重度")

            anxiety = ",".join(parts)

        depressed=""
        if len(depressed_zc) == len(self.step_list):
            depressed = "均为正常"
        elif len(depressed_qd) == len(self.step_list):
            depressed = "均为轻度抑郁"
        elif len(depressed_zhongdu) == len(self.step_list):
            depressed = "均为中度抑郁"
        elif len(depressed_zd) == len(self.step_list):
            depressed = "均为重度抑郁"
        else:
            parts = []
            if len(depressed_qd) != 0:
                parts.append(f"{len(depressed_qd)}次轻度")
            if len(depressed_zhongdu) != 0:
                parts.append(f"{len(depressed_zhongdu)}次中度")
            if len(depressed_zd) != 0:
                parts.append(f"{len(depressed_zd)}次重度")

            depressed = ",".join(parts)

        if len(self.step_list) >= 10:
            h = 10
        else:
            h = len(self.step_list)

        if depressed=="均为正常":
            comment = f"根据分析显示 {self.step_list[0]['name']} 近{h}次的检测报告中\n抑郁结果均为正常，请根据测评建议调整当前状况。\n"
        elif len(self.step_list)>=2:
            score= round(depressed_score - depressed_previous_score, 2)
            count = len(self.step_list) - len(depressed_zc)
            if score<0:
                comment = f"根据分析显示 {self.step_list[0]['name']} 近{h}次的检测报告中\n抑郁结果有{count}次，{depressed}，其中最新一次的检测结果为{depressed_score}分，相较于上次检测减少{abs(score) } 分，请根据测评建议调整当前状况。\n"
            else:
                comment = f"根据分析显示 {self.step_list[0]['name']} 近{h}次的检测报告中\n抑郁结果有{count}次，{depressed}，其中最新一次的检测结果为{depressed_score}分，相较于上次检测高出{score}分，请根据测评建议调整当前状况。\n"
        else:
            count = len(self.step_list) - len(depressed_zc)
            comment = f"根据分析显示 {self.step_list[0]['name']} 近{h}次的检测报告中\n抑郁结果有{count}次，{depressed}，其中最新一次的检测结果为{depressed_score}分，请根据测评建议调整当前状况。\n"

        if anxiety == "均为正常":
            comment += f"焦虑结果均为正常，请根据测评建议调整当前状况。"
        elif len(self.step_list) >= 2:
            score =  round(anxiety_score - anxiety_previous_score, 2)
            count = len(self.step_list) - len(anxiety_zc)
            if score < 0:
                comment += f"焦虑结果有{count}次，{anxiety}，其中最新一次的检测结果为{anxiety_score}分，相较于上次检测减少{abs(score)} 分，请根据测评建议调整当前状况。\n"
            else:
                comment += f"焦虑结果有{count}次，{anxiety}，其中最新一次的检测结果为{anxiety_score}分，相较于上次检测高出{score}分，请根据测评建议调整当前状况。\n"
        else:
            count = len(self.step_list) - len(anxiety_zc)
            comment += f"焦虑结果有{count}次，{anxiety}，其中最新一次的检测结果为{anxiety_score}分，请根据测评建议调整当前状况。\n"

        self.textEdit.setText(comment)

    def update_ui(self,phone, count, name):
        self.phone = phone
        self.count = count
        self.name = name
        # 清除旧的标签页
        self.tabWidget.clear()

        if self.is_show:
            # 获取新的数据并更新标签页
            res, self.step_list = self.api.get_report_tab_data(self.phone)

        else:
            if self.isHidden():
                self.show()
            res, self.step_list = self.api.get_report_tab_data(self.phone, self.count)

        count_list = []
        for i in self.step_list:
            tab_item = Report_Item(i)
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(tab_item)
            self.tabWidget.addTab(scroll_area, f"第{i['count']}次")
            # if not self.is_show:
            #     self.hide()
            count_list.append(i['count'])

        if not self.is_show:
            if not self.isHidden():
                self.hide()

        if self.count in count_list:
            index = count_list.index(self.count)

        self.tabWidget.currentChanged.connect(self.on_tab_changed)

        if self.tabWidget.count() > 0:
            if index == 0:
                current_widget = self.tabWidget.currentWidget()
                report_item = current_widget.widget()
                report_item.init_listwidget_data()
            else:
                self.tabWidget.setCurrentIndex(index)

    def on_tab_changed(self, index):
        current_widget = self.tabWidget.currentWidget()
        # 获取 QScrollArea 中的内部小部件
        if current_widget:
            report_item = current_widget.widget()
            report_item.init_listwidget_data()


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

    def export_pdf_file(self,directory_path=None):

        currentIndex = self.tabWidget.currentIndex()
        if currentIndex == -1:
            logger.error("No current tab selected in tabWidget.")
            return

        currentTabWidget = self.tabWidget.widget(currentIndex)
        if currentTabWidget is None:
            logger.error("currentTabWidget is None.")
            return

        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)

        # 设置分辨率
        printer.setResolution(500)

        if directory_path is None:
            save_path = self.settings["save_path"]
        else:
            save_path = directory_path
        dir_path = os.path.join(save_path, self.phone)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        output_file = os.path.join(dir_path,
                                   f"{self.name}_{self.count}.pdf")
        printer.setOutputFileName(output_file)

        # 获取内容大小
        if isinstance(currentTabWidget, QScrollArea):
            content_widget = currentTabWidget.widget()
        else:
            content_widget = currentTabWidget

        # 获取内容的完整大小
        content_size = content_widget.sizeHint()

        # 设置页面大小
        page_size = printer.pageRect(QPrinter.DevicePixel).size()
        printer.setPaperSize(page_size, QPrinter.DevicePixel)  # 使用设备像素单位

        # 创建 QPainter 对象
        painter = QPainter(printer)

        # 计算缩放因子
        x_scale = page_size.width() / content_size.width()
        y_scale = page_size.height() / content_size.height()
        scale_factor = min(x_scale, y_scale) * 0.95  # 将缩放因子调整为0.85

        # 计算偏移量以居中内容，并设置边距
        offset_x = (page_size.width() - content_size.width() * scale_factor) / 2
        offset_y = (page_size.height() - content_size.height() * scale_factor) / 2-10

        # 应用缩放因子和偏移量
        painter.translate(offset_x, offset_y)
        painter.scale(scale_factor, scale_factor)

        # # 应用缩放因子
        # painter.scale(scale_factor, scale_factor)

        # 渲染内容到 PDF
        content_widget.render(painter)

        # 结束绘制
        painter.end()
        if not directory_path:
            definition_MessageBox("保存成功!")

    def printCurrentTabScreenshot(self):
        currentIndex = self.tabWidget.currentIndex()

        self.frame_2.hide()
        wait_noblock()
        currentTabWidget = self.tabWidget.widget(currentIndex)

        # 获取滚动区域的大小
        scroll_area_size = currentTabWidget.widget().size()

        # 创建一个与滚动区域大小相同的 QPixmap 对象
        screenshot = QPixmap(scroll_area_size)
        screenshot.fill(Qt.white)  # 填充白色背景

        # 创建一个 QPainter 对象，将滚动区域内容绘制到 QPixmap 对象中
        painter = QPainter(screenshot)
        currentTabWidget.widget().render(painter)
        painter.end()

        printer = QPrinter()  # 打印机对象
        printer.setPageMargins(0, 0, 0, 0, QPrinter.Millimeter)  # 设置打印页边距为0
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() == QPrintDialog.Accepted:
            painter = QPainter(printer)  # 在打印机上创建绘制对象
            paperRect = printer.pageRect()  # 获取打印页面的尺寸

            # 计算每一页的高度
            pixmap_height = screenshot.height()
            page_height = paperRect.height()

            # 如果内容超过一页，进行分割打印
            for offset in range(0, pixmap_height, page_height):
                # 计算要打印的部分
                part = screenshot.copy(0, offset, screenshot.width(), min(page_height, pixmap_height - offset))

                # 计算宽度缩放因子
                scale_factor = paperRect.width() / part.width()
                scaled_width = part.width() * scale_factor

                # 绘制时保持高度不变，但缩放宽度
                scaled_part = part.scaled(scaled_width, part.height(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
                painter.drawPixmap(0, 0, scaled_part)

                if offset + page_height < pixmap_height:
                    printer.newPage()  # 开始新的一页

            painter.end()
            definition_MessageBox("打印结束")
        self.frame_2.show()

    def onTabChanged(self,index):
        self.current_tab = self.tabWidget.widget(index)

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

class Report_Item(QWidget, Ui_new_report):
    def __init__(self, data):

        super().__init__()
        self.setupUi(self)
        self.data=data

        # self.label_14.setText(f"第{self.data['count']}次检测") #检测记录
        self.label_2.setText(f"{self.data['class']}抑郁焦虑心理健康评测报告")
        label_data_pairs = [
            (self.label_3, 'depressed_score'),
            (self.label_35, 'anxiety_score'),
            (self.label_5, 'school'),  #学校
            (self.label_9, 'grade'),  #年级
            (self.label_12, 'class'),  #班级
            (self.label_13, 'phone'),  #学号
            (self.label_14, 'name'),  #姓名
            (self.label_15, 'sex'),  #性别
            (self.label_16, 'age'),  #年龄
        ]
        # 循环设置标签文本
        for label, key in label_data_pairs:
            if self.data[key] is not None:
                label.setText(str(self.data[key]))
            else:
                label.setText("")
        self.init_text_data()

        self.adjust_size()
        #self.init_listwidget_data()

    def adjust_size(self):
        self.text_list=[]
        if  self.stackedWidget_3.currentIndex()==0:
            self.text_list.append(self.textEdit_5)

        elif self.stackedWidget_3.currentIndex()==1:
            self.text_list.append(self.textEdit_12)

        elif self.stackedWidget_3.currentIndex()==2:
            self.text_list.append(self.textEdit_6)
        elif self.stackedWidget_3.currentIndex()==3:
            self.text_list.append(self.textEdit_7)

        if self.stackedWidget_2.currentIndex() == 0:
            self.text_list.append(self.textEdit_8)
        elif self.stackedWidget_2.currentIndex() == 1:
            self.text_list.append(self.textEdit_9)
        elif self.stackedWidget_2.currentIndex() == 2:
            self.text_list.append(self.textEdit_10)
        elif self.stackedWidget_2.currentIndex() == 3:
            self.text_list.append(self.textEdit_11)


        for i in range(0,len(self.text_list)):

            document = self.text_list[i].document()
            font_metrics = QFontMetrics(self.text_list[i].font())
            document_height = font_metrics.height() * document.blockCount()

            if i == 0:
                if self.stackedWidget_3.currentIndex() == 0:
                    self.text_list[i].setFixedHeight(document_height + 180)

                elif self.stackedWidget_3.currentIndex() == 1:
                    self.text_list[i].setFixedHeight(document_height + 770)

                elif self.stackedWidget_3.currentIndex() == 2:
                    self.text_list[i].setFixedHeight(document_height + 660)

                elif self.stackedWidget_3.currentIndex() == 3:
                    self.text_list[i].setFixedHeight(document_height + 745)

            else:
                if self.stackedWidget_2.currentIndex() == 0:
                    self.text_list[i].setFixedHeight(document_height + 180)

                elif self.stackedWidget_2.currentIndex() == 1:
                    self.text_list[i].setFixedHeight(document_height + 440)

                elif self.stackedWidget_2.currentIndex() == 2:
                    self.text_list[i].setFixedHeight(document_height + 430)

                elif self.stackedWidget_2.currentIndex() == 3:
                    self.text_list[i].setFixedHeight(document_height + 380)

    def init_text_data(self):
        # 抑郁正常
        if -1 <= float(self.label_3.text()) <50:
            self.label_74.setText("正常")
            current_style = self.styleSheet()
            new_style = """
                #frame_8 {
                     border-image:url(:/icon/res/抑郁正常.png);
                }
                 #label_3 {
                        color: rgb(28, 187, 0);
                        font: 75 18pt "微软雅黑";
                        font-weight: bold;
                        }
            """
            self.setStyleSheet(current_style + new_style)

            self.stackedWidget_3.setCurrentIndex(0)
        elif 50 <= float(self.label_3.text()) <65:
            self.label_84.setText("轻度抑郁")
            current_style = self.styleSheet()
            new_style = """
                                                    #frame_8 {
                                                        border-image:url(:/icon/res/抑郁轻度.png);
                                                    }
                                                     #label_3 {
                                                        color: rgb(164, 208, 6);
                                                        font: 75 18pt "微软雅黑";
                                                        font-weight: bold;
                                                        }
                                                """
            self.setStyleSheet(current_style + new_style)

            self.stackedWidget_3.setCurrentIndex(1)
        elif 65 <= float(self.label_3.text()) <75:
            self.label_67.setText("中度抑郁")
            current_style = self.styleSheet()
            new_style = """
                                                    #frame_8 {
                                                        border-image:url(:/icon/res/抑郁中度.png);
                                                    }
                                                    #label_3 {
                                                        color: rgb(255, 180, 5);
                                                        font: 75 18pt "微软雅黑";
                                                        font-weight: bold;
                                                        }
                                                """
            self.setStyleSheet(current_style + new_style)

            self.stackedWidget_3.setCurrentIndex(2)
        elif 75 <= float(self.label_3.text()) <= 100:
            self.label_69.setText("重度抑郁")
            current_style = self.styleSheet()
            new_style = """
                                                    #frame_8 {
                                                        border-image:url(:/icon/res/抑郁重度.png);
                                                    }
                                                    #label_3 {
                                                        color: rgb(255, 0, 0);
                                                        font: 75 18pt "微软雅黑";
                                                        font-weight: bold;
                                                        }
                                                """
            self.setStyleSheet(current_style + new_style)

            self.stackedWidget_3.setCurrentIndex(3)
        #焦虑
        if -1 <= float(self.label_35.text()) <50:
            self.label_60.setText("正常")
            current_style = self.styleSheet()
            new_style = """
                            #frame_9 {
                                border-image:url(:/icon/res/焦虑正常.png);
                            }
                            #label_35 {
                                color: rgb(28, 187, 0);
                                font: 75 18pt "微软雅黑";
                                font-weight: bold;
                            }
                        """
            self.setStyleSheet(current_style + new_style)

            self.stackedWidget_2.setCurrentIndex(0)
        elif 50 <= float(self.label_35.text()) <65:
            self.label_63.setText("轻度焦虑")
            current_style = self.styleSheet()
            new_style = """
                                        #frame_9 {
                                            border-image:url(:/icon/res/焦虑轻度.png);
                                        }
                                         #label_35 {
                                                color: rgb(164, 208, 6);
                                                font: 75 18pt "微软雅黑";
                                                font-weight: bold;
                                            }
                                    """
            self.setStyleSheet(current_style + new_style)

            self.stackedWidget_2.setCurrentIndex(1)
        elif 65 <= float(self.label_35.text()) <75:
            self.label_78.setText("中度焦虑")
            current_style = self.styleSheet()
            new_style = """
                                        #frame_9 {
                                            border-image:url(:/icon/res/焦虑中度.png);
                                        }
                                        #label_35 {
                                                color: rgb(255, 180, 5);
                                                font: 75 18pt "微软雅黑";
                                                font-weight: bold;
                                            }
                                    """
            self.setStyleSheet(current_style + new_style)

            self.stackedWidget_2.setCurrentIndex(2)
        elif 75 <= float(self.label_35.text()) <= 100:
            self.label_81.setText("重度焦虑")
            current_style = self.styleSheet()
            new_style = """
                                        #frame_9 {
                                            border-image:url(:/icon/res/焦虑重度.png);
                                        }
                                        #label_35 {
                                            color: rgb(255, 0, 0);
                                            font: 75 18pt "微软雅黑";
                                            font-weight: bold;
                                        }
                                    """
            self.setStyleSheet(current_style + new_style)

            self.stackedWidget_2.setCurrentIndex(3)


    def init_listwidget_data(self):
        print("-------")
        if self.data["save_path_s"] is None:
            subset_list = []
            subset_list_1 = []
            subset_list_2 = []
        elif os.path.exists(self.data["save_path_s"]):
            print("------------")
            dll_path=get_actual_path('./ForPy/EEGSENSOR.dll')
            eegs_dll = ctypes.CDLL(dll_path)
            # 用于去除EEG数据中的噪声
            eegs_dll.ThreeLead_EEGSensor_DataDSP.argtypes = [ctypes.POINTER(ctypes.c_double),
                                                             ctypes.POINTER(ctypes.c_double)]
            eegs_dll.ThreeLead_EEGSensor_DataDSP.restype = ctypes.POINTER(ctypes.c_double)

            eegs_dll.EEGQuality.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_int)]
            eegs_dll.EEGQuality.restype = ctypes.POINTER(ctypes.c_int)

            df = pd.read_csv(self.data["save_path_s"])
            # 获取数据行数
            num_rows = len(df)
            # 如果行数超过18000行
            mid = num_rows // 2
            subset_list = []
            subset_list_1 = []
            subset_list_2 = []
            if num_rows > 0:
                # 提取第9001行到第10000行之间的数据（注意Python的索引是从0开始的）
                slist = df.iloc[mid:mid + 5000, 0].tolist()
                slist_1 = df.iloc[mid:mid + 5000, 1].tolist()
                slist_2 = df.iloc[mid:mid + 5000, 2].tolist()
                dsp_eeg_initData_fp1_fp2_fpz = [0] * 804
                for i in range(len(slist) // 250):
                    fp1fpzfp2 = slist[i * 250:(i + 1) * 250] + slist_1[i * 250:(i + 1) * 250] + slist_2[
                                                                                                i * 250:(i + 1) * 250]
                    raw_eeg_data_fp1_fp2 = (ctypes.c_double * (250 * 3))(*fp1fpzfp2)
                    dsp_eeg_data_fp1_fp2_fpz = (ctypes.c_double * (250 * 3 + 54))(*dsp_eeg_initData_fp1_fp2_fpz)
                    eeg_data_without_noise = eegs_dll.ThreeLead_EEGSensor_DataDSP(raw_eeg_data_fp1_fp2,
                                                                                  dsp_eeg_data_fp1_fp2_fpz)
                    # 将去噪后的数据转换为 NumPy 数组
                    eeg_data_without_noise_array_withargs = np.ctypeslib.as_array(
                        ctypes.cast(eeg_data_without_noise,
                                    ctypes.POINTER(ctypes.c_double * (250 * 3 + 54))).contents)
                    dsp_eeg_initData_fp1_fp2_fpz[:] = eeg_data_without_noise_array_withargs[:]

                    fp1fpzfp2_baseline = eeg_data_without_noise_array_withargs.tolist()
                    subset_list.extend(fp1fpzfp2_baseline[:250])
                    subset_list_1.extend(fp1fpzfp2_baseline[250:500])
                    subset_list_2.extend(fp1fpzfp2_baseline[500:750])

            else:
                subset_list = []
                subset_list_1 = []
                subset_list_2 = []

        else:

            subset_list = []
            subset_list_1 = []
            subset_list_2 = []


        for i in range(0, 1):
            item = QListWidgetItem()  # 创建QListWidgetItem对象
            item.setSizeHint(QSize(30, int(self.listWidget.height())-30))
            if len(subset_list) > 0:
                self.widget_ = WgtLeft_eggItem(subset_list[-2000:], subset_list_1[-2000:], subset_list_2[-2000:])
            else:
                self.widget_ = WgtLeft_eggItem(subset_list, subset_list_1, subset_list_2)
            self.listWidget.addItem(item)  # 添加item
            self.listWidget.setItemWidget(item, self.widget_)


class PlotCanvas_2(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure() # 创建一个新的图形对象
        self.ax = fig.add_subplot(111) #添加子图
        super().__init__(fig)
        self.setParent(parent)
        self.parent=parent

        fig.subplots_adjust(left=0.15, bottom=0.2, top=0.9)  # 调整图形在窗口中的位置
        # # 设置背景颜色
        fig.patch.set_facecolor('#1E2222')  # 图形背景颜色
        self.ax.set_facecolor('#1E2222')  # 坐标轴区域背景颜色


    def initialize_plot(self):
        self.formatted_start_date=""
        self.formatted_end_date=""
        self.depressed_list = []
        self.anxiety_list = []
        # 获取最近最多 6 个数据点
        self.step_list = self.parent.step_list[-10:] if len(self.parent.step_list) > 10 else self.parent.step_list
        # 生成格式化的日期标签
        self.date_labels = []
        for i in range(0,len(self.step_list)):
            datetime_obj = datetime.strptime(self.step_list[i]["createtime"], "%Y-%m-%d %H:%M:%S")
            if i==0:
                # 格式化为 "2024年7月12日"
                self.formatted_start_date = datetime_obj.strftime("%Y-%m-%d")
            if i==len(self.step_list)-1 and i!=0:
                self.formatted_end_date = datetime_obj.strftime("%Y-%m-%d")

            formatted_date = datetime_obj.strftime("%m-%d  %H")
            formatted_date=formatted_date+"h"
            self.depressed_list.append(self.step_list[i]["depressed_score"])
            self.anxiety_list.append(self.step_list[i]["anxiety_score"])

            self.date_labels.append(formatted_date)

        major_ticks = np.arange(0, len(self.step_list), 1)  # 设置x轴刻度
        self.ax.set_xticks(major_ticks)

        # 生成刻度标签，隐藏多余的刻度标签
        if len(self.date_labels) < len(self.step_list):
            while True:
                self.date_labels.append("")
                if len(self.date_labels) == len(self.step_list):
                    break

        # 设置斜着显示的刻度标签
        self.ax.set_xticklabels(self.date_labels, rotation=20, ha='right')

        # 设置 x 轴范围
        if len(self.step_list) > 1:
            self.ax.set_xlim(0, len(self.step_list) - 1)
        else:
            self.ax.set_xlim(-0.5, 0.5)  # 或者设置一个合理的范围以避免警告

        # 设置刻度标签往下移动
        self.ax.tick_params(axis='x', labelsize=10, pad=15)
        # 设置轴标签和刻度线的颜色
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('white')
        self.ax.spines['left'].set_color('white')
        self.ax.spines['right'].set_color('white')

        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')

        self.ax.xaxis.set_tick_params(which='major', direction='in', length=6, width=1)
        self.ax.xaxis.set_tick_params(top=True, which='major', direction='in', length=6, width=1)

        self.ax.yaxis.set_tick_params(which='major', direction='in', length=6, width=1)
        self.ax.yaxis.set_tick_params(right=True, which='major', direction='in', length=6, width=1)

        self.ax.grid(True, which='major', linestyle='--', linewidth=0.5, color='gray')
        self.ax.axhline(0, color='white', linewidth=1)

        y_ticks = [0, 20, 40, 60, 80, 100]
        self.ax.set_yticks(y_ticks)
        self.ax.set_ylim(min(y_ticks), max(y_ticks))  # 确保 y 轴范围覆盖所有刻度


    def plot(self):
        try:

            self.ax.clear()
            self.initialize_plot()
            sampling_interval = 1  # 调整此值以控制采样率

            depressed_data = self.depressed_list[::sampling_interval]
            anxiety_data = self.anxiety_list[::sampling_interval]

            sampled_indices = list(range(0, len(self.depressed_list), sampling_interval))

            self.ax.plot(sampled_indices, anxiety_data, label='焦虑分数', color='red', marker='o')
            self.ax.plot(sampled_indices, depressed_data, label='抑郁分数', color='orange', marker='o')

            if len(self.step_list) >= 5:
                count = 0.1
            elif len(self.step_list) <= 2:
                count = 0.025
            elif 3 <= len(self.step_list) <= 4:
                count = 0.07
            # 在每个数据点上添加分数注释
            for i in sampled_indices:
                # 添加焦虑分数注释
                if abs(anxiety_data[i] - depressed_data[i]) <= 5:
                    if anxiety_data[i]>depressed_data[i]:
                        self.ax.text(i-count, anxiety_data[i]+7, f'{anxiety_data[i]}', color='red', fontsize=12, ha='center',
                                     va='bottom')

                        self.ax.text(i-count, depressed_data[i], f'{depressed_data[i]}', color='orange', fontsize=12,
                                     ha='center', va='bottom')
                    else:
                        self.ax.text(i-count, anxiety_data[i], f'{anxiety_data[i]}', color='red', fontsize=12, ha='center',
                                     va='bottom')
                        self.ax.text(i-count, depressed_data[i] + 7, f'{depressed_data[i]}', color='orange', fontsize=12,
                                     ha='center', va='bottom')

                else:
                    self.ax.text(i-count, anxiety_data[i], f'{anxiety_data[i]}', color='red', fontsize=12, ha='center',
                                 va='bottom')
                    # 添加抑郁分数注释
                    self.ax.text(i-count, depressed_data[i], f'{depressed_data[i]}', color='orange', fontsize=12, ha='center',
                                 va='bottom')

            legend = self.ax.legend(loc='upper right')
            legend.get_frame().set_alpha(0.0)
            for text in legend.get_texts():
                text.set_color('white')
            for line in legend.get_lines():
                line.set_linewidth(5)

            if self.formatted_end_date:
                self.text = self.ax.text(-0.18, 1.06, f'近期检测结果折线报告({self.formatted_start_date}-{self.formatted_end_date})', transform=self.ax.transAxes, ha='left',
                                         color='white', fontsize=12)
            else:
                self.text = self.ax.text(-0.18, 1.06, f'近期检测结果折线报告({self.formatted_start_date})',
                                         transform=self.ax.transAxes, ha='left',
                                         color='white', fontsize=12)
            self.draw()
            return
        except Exception as ex:
            logger.error('%s', str(ex))


class WgtLeft_eggItem(QWidget, Ui_left_eeg_form):
    def __init__(self,data_list,data_list_1,data_list_2):
        super(WgtLeft_eggItem, self).__init__()

        self.setupUi(self)

        self.all_data = [data_list, data_list_1, data_list_2]

        self.canvas = PlotCanvas_1(self, 0)
        self.verticalLayout.addWidget(self.canvas, stretch=1)  # 设置拉伸因子

        self.canvas1 = PlotCanvas_1(self, 1)
        self.verticalLayout.addWidget(self.canvas1, stretch=1)

        self.canvas2 = PlotCanvas_1(self, 2)
        self.verticalLayout.addWidget(self.canvas2, stretch=1)

        self.canvas.plot()
        self.canvas1.plot()
        self.canvas2.plot()

class PlotCanvas_1(FigureCanvas):
    def __init__(self, parent=None,count=None):
        fig = Figure() # 创建一个新的图形对象
        self.ax = fig.add_subplot(111) #添加子图
        super().__init__(fig)
        self.setParent(parent)
        self.parent = parent

        self.count = count

        self.all_data = self.parent.all_data[count]
        self.line=""
        self.initialize_plot()
        fig.subplots_adjust(left=0.15)  # 调整图形在窗口中的位置
        #fig.subplots_adjust(left=-0.01,right=1)  # 调整图形在窗口中的位置

    def initialize_plot(self):
        major_ticks = np.arange(0, 2400, 400)  # 设置x轴刻度为0, 400, 800, 1200, 1600, 2000
        self.ax.set_xticks(major_ticks)
        self.ax.set_xlim(0, 2000)
        self.ax.xaxis.set_tick_params(which='major', direction='in', length=6, width=1)
        self.ax.yaxis.set_tick_params(which='major', direction='in', length=6, width=1)

        if self.count==0 or self.count==1:
            self.ax.xaxis.set_visible(False)  # 隐藏X轴




        self.ax.axhline(0, color='white', linewidth=1)

    def plot(self):
        try:
            if not self.all_data:
                self.ax.set_ylim(-1, 1)
                self.ax.set_yticks(np.linspace(-1, 1, 6))
                self.ax.set_yticklabels([f'{tick:.2f}' for tick in np.linspace(-1, 1, 6)])
                self.draw()
                return

            sampling_interval = 5

            sampled_data = self.all_data[::sampling_interval]
            sampled_indices = list(range(0, len(self.all_data), sampling_interval))

            # 计算当前批次数据的最大值和最小值
            max_val = max(sampled_data)
            min_val = min(sampled_data)

            mid_val = (max_val + min_val) / 2

            # 设置动态的y轴范围，以当前数据的中间值为中心
            tick_spacing = (max_val - min_val) / 5
            if tick_spacing == 0:
                tick_spacing = 1  # 防止tick_spacing为0的情况
            ticks = np.linspace(mid_val - 2.5 * tick_spacing, mid_val + 2.5 * tick_spacing, 6)

            self.ax.set_ylim(min(ticks), max(ticks))
            self.ax.set_yticks(ticks)
            self.ax.set_yticklabels([f'{tick:.2f}' for tick in ticks])

            if not self.line:
                if self.count==0:
                    self.line, = self.ax.plot(sampled_indices, sampled_data, color='red', label=f'FP1(uV)')

                elif self.count==1:
                    self.line, = self.ax.plot(sampled_indices, sampled_data, color='green', label=f'FPz(uV)')
                elif self.count==2:
                    self.line, = self.ax.plot(sampled_indices, sampled_data, color='blue', label=f'FP2(uV)')

                legend = self.ax.legend(loc='upper right', bbox_to_anchor=(1.14, 1.2))  # 将图例上移
                legend.get_frame().set_alpha(0.0)
                for text in legend.get_texts():
                    text.set_color('black')
                for line in legend.get_lines():
                    line.set_linewidth(5)


            self.draw()

        except Exception as ex:
            logger.error('%s', str(ex))