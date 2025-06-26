import json
import os
import subprocess

import tempfile
import threading
import numpy as np
from PyQt5 import QtWidgets, QtCore
import random
import serial.tools.list_ports

from PyQt5.QtWidgets import QWidget, QApplication, QListWidgetItem, QListView, QFileDialog, QComboBox, QProgressDialog, \
    QLabel, QProgressBar, QVBoxLayout
from PyQt5.QtCore import *
from PyQt5.QtCore import Qt
from config.config import *
from db_data import WgtData
import wave
import pyaudio
import pygame
import pandas as pd
from db_data_analyze import WgtData_Analyze
from db_left_egg import WgtLeft_eggItem, EEGDataThread
from db_report import Report
from db_right_egg import WgtRight
from db_school_login import School_Login
from db_set import Set_Info
import yaml

from gui.main import Ui_main_Form
# from new_db_data_analyze import New_WgtData_Analyze
from utils.logger import logger

from utils.data_sqlite import *

from utils.utils import *
from get_path import get_actual_path


class Wgt_Main(QWidget, Ui_main_Form):
    def __init__(self):
        super(Wgt_Main, self).__init__()
        self.setupUi(self)

        self.comboBox_COM.setView(QListView())

        # 添加设备号
        ports = list(serial.tools.list_ports.comports())
        # com_list = [port.device for port in ports]
        com_list = self.device_init(ports)

        self.comboBox_COM.addItems(com_list)
        self.comboBox_COM.setCurrentIndex(-1)
        self.comboBox_COM.currentIndexChanged.connect(self.receive_eeg_data)
        # 先配置基本界面
        self.__sub_init_basic_ui()

        self._init_listwidget_data()

        self.api = api()

        with open(set_file_path, 'r', encoding='utf-8') as file:
            self.settings = json.load(file)

        # #数据分析
        # self.bt_data_analyze_2.clicked.connect(self.data_analy)
        # 检测报告
        self.bt6_generateReport.clicked.connect(self.file_analy)
        # self.bt6_generateReport.setEnabled(False)

        # 信息录入
        self.bt3_infoRecord.clicked.connect(self.open_user_info)
        # #数据检索
        # self.bt7_dataRetrieval.clicked.connect(self.show_data_widget)
        # 采集数据一阶
        self.dataRecord_flag = False
        self.bt4_dataRecord.clicked.connect(self.Collect_data_1)
        self.bt4_dataRecord.setEnabled(True)
        # 采集数据二阶
        self.dataRecord2_flag = False
        self.bt5_dataRecod2.clicked.connect(self.Collect_data_2)
        self.bt5_dataRecod2.setEnabled(False)

        # 文件分析
        # self.bt1_openDevice_2.clicked.connect(self.csv_file_analy)

        # 充电
        # self.pb_set_2.clicked.connect(self.charging_status)  # 充电 停止充电
        # self.pb_set_2.setToolTip("充电")
        self.charging_name = ""

        self.collect_flag = False  # 是否正在采集
        # 初始化倒计时时间为 80,70 秒
        self.time_left = self.settings['data_I']
        self.lineEdit_timing.setText("0")

        self.lineEdit_time.setStyleSheet("color: blue; font-size: 24px;")
        self.lineEdit_timing.setStyleSheet("color: green; font-size: 24px;")

        self.lineEdit_timing.setReadOnly(True)
        self.lineEdit_time.setReadOnly(True)  # 设置为只读

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        self.playing = False
        self.thread_flag = False
        self.stop_event = threading.Event()

        self.thread = ""
        self.WgtData = None
        self.phone = ""  # 当前的学号
        self.name = ""  # 当前的名字
        self.count = ""  # 当前的检测次数
        self.com_name = "None"
        # 初次更新时间
        self.Enter_Info = None

        self.csv_file = ""
        self.csv_file_s = ""


    def charging_status(self):
        com_name = self.comboBox_COM.currentText()
        if com_name == "":
            definition_MessageBox("未选择设备号~")
            self.pb_set_2.setChecked(False)
            return

        if self.collect_flag:
            definition_MessageBox("正在采集中")
            return

        eeg_items = [self.left_widget_1, self.right_widget_1]
        if self.pb_set_2.isChecked():
            msg_box, yes_button, no_button = select_definition_MessageBox(f"是否为{com_name}设备号充电?")
            if msg_box.clickedButton() == no_button:
                self.pb_set_2.setChecked(False)
                return
            else:
                # 充电  停止线程
                if self.thread:
                    self.charging_name = com_name
                    self.thread.requestInterruption()
                    self.bt3_infoRecord.setEnabled(True)
                    self.bt4_dataRecord.setEnabled(True)
                    self.bt5_dataRecod2.setEnabled(False)
                    self.dataRecord_flag = False
                    self.dataRecord2_flag = False
                    self.lineEdit_timing.setText("0")
                    self.time_left = self.settings['data_I']
                    if self.com_name != com_name:
                        self.phone = ""
                        self.name = ""
                        self.count = ""
                    self.cleanup()  # 自动在退出时停止音乐

                    self.pb_set_2.setToolTip("停止充电")
                    self.pb_set_2.setIcon(QIcon(':/icon/res/充电.png'))
                    # self.charging_time_flag=True
                    # self.use_time_flag=False
                    wait_noblock(1)
                    self.thread = ""
                    for item in range(0, len(eeg_items)):
                        if item < 1:
                            eeg_items[item].canvas.all_data = []
                            eeg_items[item].canvas1.all_data = []
                            eeg_items[item].canvas2.all_data = []
                            eeg_items[item].canvas.line = ""
                            eeg_items[item].canvas1.line = ""
                            eeg_items[item].canvas2.line = ""
                            eeg_items[item].update_signal.emit([], [], [])
                        else:
                            eeg_items[item].WgtRight_1.canvas.line = ""
                            eeg_items[item].WgtRight_2.canvas.line = ""
                            eeg_items[item].WgtRight_3.canvas.line = ""
                            eeg_items[item].update_signal.emit(None, None, None, [], [], [])

        else:  # 停止充电
            msg_box, yes_button, no_button = select_definition_MessageBox(f"是否为{self.charging_name}设备号停止充电?")
            if msg_box.clickedButton() == no_button:
                self.pb_set_2.setChecked(True)
                return
            else:
                # 停止充电  如果和当前设备是同一个就启动线程
                if self.com_name == self.charging_name:
                    self.thread = EEGDataThread(eeg_items, com_name, self)
                    self.thread.start()

            self.charging_name = ""
            self.pb_set_2.setToolTip("充电")
            self.pb_set_2.setIcon(QIcon(':/icon/res/停止充电.png'))

    def device_init(self, port_lst=None):
        data_port = []
        for port_name in port_lst:
            if 'USB Serial Port' in port_name.description:
                data_port.append(port_name.device)
        return data_port

    def receive_eeg_data(self):
        com_name = self.comboBox_COM.currentText()
        eeg_items = [self.left_widget_1, self.right_widget_1]

        if self.thread:
            self.thread.requestInterruption()
            self.bt3_infoRecord.setEnabled(True)
            self.bt4_dataRecord.setEnabled(True)
            self.bt5_dataRecod2.setEnabled(False)
            self.dataRecord_flag = False
            self.dataRecord2_flag = False
            self.lineEdit_timing.setText("0")
            self.time_left = self.settings['data_I']
            if self.com_name != com_name:
                self.phone = ""
                self.name = ""
                self.count = ""

            self.cleanup()  # 自动在退出时停止音乐
            wait_noblock(1)

        self.thread = EEGDataThread(eeg_items, com_name, self)

        for item in range(0, len(eeg_items)):
            if item < 1:
                eeg_items[item].canvas.all_data = []
                eeg_items[item].canvas1.all_data = []
                eeg_items[item].canvas2.all_data = []
                eeg_items[item].canvas.line = ""
                eeg_items[item].canvas1.line = ""
                eeg_items[item].canvas2.line = ""
                eeg_items[item].update_signal.emit([], [], [])
            else:
                eeg_items[item].WgtRight_1.canvas.line = ""
                eeg_items[item].WgtRight_2.canvas.line = ""
                eeg_items[item].WgtRight_3.canvas.line = ""
                eeg_items[item].update_signal.emit(None, None, None, [], [], [])
        self.com_name = com_name

        # self.use_time_flag=True
        self.thread.start()

    def Collect_data_1(self):
        if self.charging_name == self.com_name:
            definition_MessageBox("当前选择设备号正在充电,请停止充电~")
            return
        if not self.phone:
            definition_MessageBox("请先录入信息~")
            return
        if self.thread:
            res, result = self.api.get_report_count(self.phone)
            if res:
                self.count = result
            self.collect_flag = True  # 是否正在采集
            self.left_widget_1.canvas2.toggle_red_dot(True)

            self.thread.collect_flag = True
            self.thread.count_flag = 1
            self.dataRecord_flag = True

    def _play_music(self, music_path):
        # 初始化音频流
        wf = wave.open(music_path, 'rb')
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        data = wf.readframes(1024)
        while data and not self.stop_event.is_set():  # 事件被设置就停止
            stream.write(data)
            data = wf.readframes(1024)

        # 停止音频流并关闭所有资源
        stream.stop_stream()
        stream.close()
        p.terminate()

    def play_music(self):
        music_path = os.path.join(os.path.dirname(__file__), 'Pictures', 'oldsound3.wav')
        self.playing = True
        self.stop_event.clear()  # 确保在开始播放前清除停止事件设置
        self.music_thread = threading.Thread(target=self._play_music, args=(music_path,))
        self.music_thread.start()

    def stop_music(self):
        if self.playing:
            self.stop_event.set()  # 事件设置
            self.music_thread.join()
            self.playing = False

    def cleanup(self):
        self.stop_music()

    def Collect_data_2(self):
        if self.thread:
            self.thread.collect_flag = True
            self.thread.count_flag = 2
            self.dataRecord2_flag = True
            # self.bt5_dataRecod2.setEnabled(False)
            if not self.playing:
                self.play_music()  # 切换设备号的时候在调用  退出软件的时候在调用

    def data_analy(self):
        self.Data_Analyze = WgtData_Analyze(self.api)
        self.Data_Analyze.showMaximized()

        # self.Data_Analyze=New_WgtData_Analyze(self.api)
        # self.Data_Analyze.showMaximized()

    def file_analy(self):
        if not hasattr(self, 'thread_analy'):
            definition_MessageBox("无采集信息")
        else:
            if self.thread_flag:
                self.progress_dialog = CustomProgressDialog("正在分析数据...", "取消", 0, 100, self)
                self.progress_dialog.show()
                self.thread_analy.progress_flag = True
            else:
                self.open_report()

    def open_report(self):
        if self.thread_analy.error_text != "":
            definition_MessageBox(self.thread_analy.error_text)
        else:

            self.report = Report(self.user_info_list[0], self.user_info_list[2], self.api, self.user_info_list[1])

    def show_data_widget(self):
        if self.WgtData:
            self.WgtData.close()
        self.WgtData = WgtData(self.api)

    def open_user_info(self):
        if self.collect_flag:
            definition_MessageBox(f"当前正在数据采集中~")
            return
        self.Enter_Info = School_Login(self)
        self.Enter_Info.show()

    def update_time(self):
        if self.dataRecord_flag:
            if self.time_left >= 0:
                self.lineEdit_timing.setText(str(self.time_left))
                # 增加剩余时间
                self.time_left -= 1
            else:
                self.dataRecord_flag = False
                self.time_left = 72
                self.bt4_dataRecord.setEnabled(False)
                self.bt5_dataRecod2.setEnabled(True)

                # self.thread.collect_flag = False
                # self.thread.save_flag = True
                self.thread.collect_flag = False
                self.thread.save_flag = True

                # 添加音乐
                try:
                    pygame.mixer.init()
                    mp3_path = get_actual_path("data_collection2.mp3")
                    pygame.mixer.music.load(mp3_path)
                    # 播放 MP3 文件
                    pygame.mixer.music.play()
                    wait_noblock(1)
                    self.Collect_data_2()
                    # definition_MessageBox("第一阶段采集完成")
                except Exception as e:
                    logger.error('db_main/null_music/%s', str(e))
                    definition_MessageBox("第一阶段采集完成，无法播放音频")

        elif self.dataRecord2_flag:
            if self.time_left >= 0:
                self.lineEdit_timing.setText(str(self.time_left))
                # 增加剩余时间
                self.time_left -= 1
            else:
                self.playing = False

                self.thread.collect_flag = False
                self.thread.save_flag = True
                try:
                    mp3_path = get_actual_path("endTip.mp3")
                    pygame.mixer.music.load(mp3_path)
                    # 播放 MP3 文件
                    pygame.mixer.music.play()
                    definition_MessageBox("第二阶段采集完成")
                except Exception as e:
                    logger.error('db_main/null_music/%s', str(e))
                    definition_MessageBox("第二阶段采集完成")

                self.thread_flag = True
                self.user_info_list = [self.phone, self.name, self.count]
                self.api.update_medical_records(self.phone, 1)
                self.left_widget_1.canvas2.toggle_red_dot(False)
                self.collect_flag = False

                com_name = self.comboBox_COM.currentText()
                self.thread_analy = analy_worker_Thread(self, com_name)
                self.thread_analy.progress_signal.connect(self.update_ui)  # 连接信号到槽
                # self.thread_analy.finished.connect(self.open_report)
                self.thread_analy.start()

                self.receive_eeg_data()

        # 获取当前时间
        currentDateTime = QDateTime.currentDateTime()

        formattedDateTime = currentDateTime.toString('yyyy-MM-dd HH:mm')

        self.lineEdit_time.setText(formattedDateTime)

    def update_ui(self, value):
        if value == 99:
            self.progress_dialog.close()
            self.open_report()
            return
        self.progress_dialog.setValue(value)

    def _init_listwidget_data(self):
        for i in range(0, 1):
            item = QListWidgetItem()  # 创建QListWidgetItem对象
            if i == 0:
                item.setSizeHint(QSize(30, int(self.listWidget.height())))
                self.left_widget_1 = WgtLeft_eggItem(self)
                self.listWidget.addItem(item)  # 添加item
                self.listWidget.setItemWidget(item, self.left_widget_1)

        for i in range(0, 1):
            item = QListWidgetItem()  # 创建QListWidgetItem对象
            if i == 0:
                item.setSizeHint(QSize(30, int(self.listWidget_2.height())))
                self.right_widget_1 = WgtRight()
                self.listWidget_2.addItem(item)
                self.listWidget_2.setItemWidget(item, self.right_widget_1)

    def __sub_init_basic_ui(self):
        """初始化基本UI
        """
        self.setWindowFlags(Qt.FramelessWindowHint)  # 无边框
        self.showMaximized()
        wait_noblock()

        self.m_flag = False
        self.setWindowIcon(QIcon(":/icon/res/logo.png"))
        self.setWindowTitle('首页')

        self.pbClose.setMouseTracking(True)
        self.pbClose.setToolTip("关闭程序")
        self.pbClose.clicked.connect(self.onMainWindowClose)
        self.pbhide.setMouseTracking(True)
        self.pbhide.setToolTip("窗口最小化")
        self.pbhide.clicked.connect(self.showMinimized)

        self.pb_set.clicked.connect(self.open_set_page)
        self.pb_set.setToolTip("设置")

    def open_set_page(self):
        self.set_info = Set_Info(self.api)
        self.set_info.show()

    def closeEvent(self, a0):
        self.onMainWindowClose(a0)

    def onMainWindowClose(self, event):
        """关闭按钮槽函数
        """
        wait_noblock(0.5)
        self.cleanup()  # 自动在退出时停止音乐
        # 强制退出
        os._exit(0)


class analy_worker_Thread(QThread):
    # 定义一个信号，当需要打开新窗口时发出
    progress_signal = pyqtSignal(int)

    def __init__(self, db_main, com_name):
        super().__init__()
        self.phone = db_main.phone
        self.name = db_main.name
        self.api = db_main.api
        self.count = db_main.count

        self.db_main = db_main
        self.com_name = com_name

        with open(set_file_path, 'r', encoding='utf-8') as file:
            self.settings = json.load(file)
        self.dir_path = os.path.join(self.settings["save_path"], self.phone)
        self.dir_path = get_actual_path(self.dir_path)
        self.csv_file1 = os.path.join(self.dir_path,
                                      f"{self.phone}_{self.name}_{self.count}_FP1.csv")
        self.csv_file2 = os.path.join(self.dir_path,
                                      f"{self.phone}_{self.name}_{self.count}_FPz.csv")
        self.csv_file3 = os.path.join(self.dir_path,
                                      f"{self.phone}_{self.name}_{self.count}_FP2.csv")
        self.error_text = ""

        self.progress_flag = False
        if not os.path.exists(self.csv_file1):
            self.error_text = "不存在数据文件"
        else:
            df = pd.read_csv(self.csv_file1, header=None)
            # 获取行数
            num_rows = df.size  # df.size 获取 Series 的元素数量，即行数
            # 判断行数是否达到 18000 行
            if num_rows != 18000:
                self.error_text = "数据格式不正确"

    def run(self):
        try:
            if self.error_text:
                self.db_main.thread_flag = False
                if self.progress_flag:
                    self.progress_signal.emit(99)
                return

            # result = subprocess.run([paths["exe_path"], self.csv_file1, self.csv_file2, self.csv_file3],
            #                         capture_output=True, text=True,
            #                         check=True)

            # 打开检测报告
            if self.phone:
                # 读取txt文件内容
                with open(paths["DrugProbability_path"], 'r') as file:
                    content = float(file.read()) + self.settings['depressed_check_score']  # 抑郁

                with open(paths["AnxietyProbability_path"], 'r') as file:
                    content1 = float(file.read()) + self.settings['anxiety_check_score']  # 焦虑

                print(content, "content", content1, "content1")

                if content <= 10:
                    content = round(random.uniform(20, 35), 2)
                if content1 <= 10:
                    content1 = round(random.uniform(20, 35), 2)

                if self.progress_flag:
                    self.progress_signal.emit(90)

                self.api.insert_localAnaly_records(float(content), float(content1), self.phone, self.name, self.count,
                                                   self.db_main.csv_file, self.db_main.csv_file_s,
                                                   com_name=self.com_name)

        except Exception as ex:
            self.error_text = "未读取到报告。"
            logger.error('db_main/Detection_report_error/%s', str(ex))
            logger.error(paths["exe_path"], paths["DrugProbability_path"],
                         paths["AnxietyProbability_path"])

        self.db_main.thread_flag = False

        wait_noblock(0.2)
        if self.progress_flag:
            self.progress_signal.emit(99)


class CustomProgressDialog(QProgressDialog):
    def __init__(self, labelText, cancelText, min, max, parent=None):
        super().__init__(labelText, cancelText, min, max, parent)
        self.setCancelButton(None)
        self.parent = parent
        self.setWindowModality(Qt.WindowModal)
        self.setWindowTitle("分析")
        self.resize(300, 150)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)

        # 获取 QLabel 和 QProgressBar
        label = self.findChild(QLabel)
        progress_bar = self.findChild(QProgressBar)

        # 创建新的布局并添加控件
        layout = QVBoxLayout()
        layout.addWidget(label, alignment=Qt.AlignCenter)
        layout.addWidget(progress_bar, alignment=Qt.AlignCenter)

        # 应用自定义样式
        self.setStyleSheet("""
            QProgressDialog {
                background-color: #F0F0F0; /* 更柔和的背景 */
                color: #333333;
                border: 1px solid #DDDDDD;
                border-radius: 10px;
                padding: 15px;
            }
            QLabel {
                font-size: 16px; /* 增加字体大小 */
                font-weight: bold; /* 加粗标签 */
                color: #444444; /* 更深的颜色 */
                margin-bottom: 10px; /* 标签下方的间距 */
            }
            QProgressBar {
                border: 1px solid #DDDDDD;
                border-radius: 5px;
                background-color: #EAEAEA; /* 进度条背景色更浅 */
                height: 20px; /* 增加高度 */
            }   
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 20px;
                margin: 1px;
            }
        """)
        self.setLayout(layout)
