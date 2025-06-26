import csv
import ctypes
import json
import os
import sys
import queue
import threading
from collections import deque
from get_path import get_actual_path
from utils.logger import logger
import numpy as np
import serial
from matplotlib.ticker import MaxNLocator, AutoLocator
from PyQt5.QtCore import QThread, pyqtSignal, QRunnable, QObject, pyqtSlot, QTimer, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from matplotlib.colors import to_rgba
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.ticker import AutoMinorLocator
import time

from config.config import set_file_path
from gui.left_egg import Ui_left_eeg_form
from utils.utils import wait_noblock, wait_noblock_, select_definition_MessageBox
import concurrent.futures
from matplotlib.patches import Circle
import matplotlib.animation as animation
import pandas as pd
import matplotlib

matplotlib.rcParams['font.family'] = 'SimHei'


class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, count=None):
        fig = Figure()  # 创建一个新的图形对象
        self.ax = fig.add_subplot(111)  # 添加子图
        super().__init__(fig)
        self.setParent(parent)
        self.parent = parent
        self.setAttribute(Qt.WA_OpaquePaintEvent, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_PaintOnScreen, False)

        self.count = count
        # self.all_data = []
        self.all_data = []  # 初始化为 NumPy 数组
        self.line = ""
        fig.subplots_adjust(left=0.15)  # 调整图形在窗口中的位置

        self.initialize_plot()
        # # 设置背景颜色
        fig.patch.set_facecolor('#000814')  # 图形背景颜色
        # #FFFFFF
        self.ax.set_facecolor('#000814')  # 坐标轴区域背景颜色
        # #FFFFFF

        if self.count == 2:
            # 添加一个专门的Axes用于放置红点
            self.dot_ax = fig.add_axes([0.92, 0.05, 0.1, 0.1], aspect='equal')  # [左, 底, 宽, 高]
            self.dot_ax.set_xlim(0, 1)
            self.dot_ax.set_ylim(0, 1)
            self.dot_ax.axis('off')  # 隐藏轴

            # 添加红点到dot_ax中
            self.red_dot = Circle((0.5, 0.5), 0.3, color='red')
            self.dot_ax.add_patch(self.red_dot)

            # Initialize blink animation
            self.anim = animation.FuncAnimation(fig, self.blink_red_dot, frames=10, interval=500, repeat=True)

            # Connect events
            self.mpl_connect('button_press_event', self.on_click)
            self.mpl_connect('motion_notify_event', self.on_hover)

            self.red_dot_visible = False  # Flag for red dot visibility

    def blink_red_dot(self, i):
        # 使红点闪烁
        if self.red_dot_visible:  # 只有在红点应可见时才闪烁
            self.red_dot.set_visible(i % 2 == 0)
            self.draw_idle()
        else:
            self.red_dot.set_visible(False)
            self.draw_idle()

    def on_click(self, event):
        # 检查点击是否在红点区域
        if self.red_dot_visible and event.inaxes == self.dot_ax:
            msg_box, yes_button, no_button = select_definition_MessageBox(f"是否要中断采集?")
            if msg_box.clickedButton() == yes_button:
                self.toggle_red_dot(False)
                self.parent.db_main.cleanup()  # 自动在退出时停止音乐
                self.parent.db_main.collect_flag = False  # 是否正在采集
                self.parent.db_main.receive_eeg_data()
            else:
                pass

    def toggle_red_dot(self, visible):
        # 控制红点的显示和隐藏
        self.red_dot_visible = visible
        if self.red_dot:
            self.red_dot.set_visible(visible)
            self.draw_idle()

    def on_hover(self, event):
        # Handle mouse hover to show or hide tooltip
        if event.inaxes == self.dot_ax:
            x, y = event.xdata, event.ydata
            # Red dot center and radius
            dot_center = (0.5, 0.5)
            dot_radius = 0.3
            # Calculate distance from cursor to the center of the red dot
            distance = np.sqrt((x - dot_center[0]) ** 2 + (y - dot_center[1]) ** 2)

            if distance <= dot_radius:  # Check if mouse is within the red dot
                self.setToolTip("取消采集")
            else:
                self.setToolTip("")  # Hide tooltip if not over the red dot
        else:
            self.setToolTip("")  # Hide tooltip if not over the dot_ax

    def initialize_plot(self):
        major_ticks = np.arange(0, 1200, 200)  # 设置x轴刻度为0, 200, 400, 600, 800, 1000
        self.ax.set_xticks(major_ticks)
        self.ax.set_xlim(0, 1000)

        # 设置轴标签和刻度线的颜色
        self.ax.spines['bottom'].set_color('#1E3A5F')
        self.ax.spines['top'].set_color('#1E3A5F')
        self.ax.spines['left'].set_color('#1E3A5F')
        self.ax.spines['right'].set_color('#1E3A5F')

        self.ax.xaxis.label.set_color('#A3B3C3')
        self.ax.yaxis.label.set_color('#A3B3C3')
        self.ax.tick_params(axis='x', colors='#A3B3C3')
        self.ax.tick_params(axis='y', colors='#A3B3C3')

        # 增大轴标签字体大小
        self.ax.xaxis.label.set_fontsize(20)  # X轴标签
        self.ax.yaxis.label.set_fontsize(20)  # Y轴标签

        # 增大刻度标签字体大小
        self.ax.tick_params(axis='both', which='major', labelsize=20)

        # 设置小刻度
        minor_locator_x = AutoMinorLocator(5)  # 每个主刻度之间增加1个小刻度
        minor_locator_y = AutoMinorLocator(5)
        self.ax.xaxis.set_minor_locator(minor_locator_x)
        self.ax.yaxis.set_minor_locator(minor_locator_y)

        self.ax.xaxis.set_tick_params(which='major', direction='in', length=6, width=1)
        self.ax.xaxis.set_tick_params(top=True, which='major', direction='in', length=6, width=1)

        self.ax.xaxis.set_tick_params(which='minor', direction='in', length=4, width=1, colors='white')
        self.ax.xaxis.set_tick_params(top=True, which='minor', direction='in', length=4, width=1, colors='white')

        self.ax.yaxis.set_tick_params(which='major', direction='in', length=6, width=1)
        self.ax.yaxis.set_tick_params(right=True, which='major', direction='in', length=6, width=1)

        self.ax.yaxis.set_tick_params(which='minor', direction='in', length=4, width=1, colors='white')
        self.ax.yaxis.set_tick_params(right=True, which='minor', direction='in', length=4, width=1, colors='white')

        self.ax.grid(True, which='major', linestyle='--', linewidth=0.5, color='gray')
        self.ax.minorticks_on()  # 开启次级刻度
        self.ax.grid(True, which='minor', linestyle='--', linewidth=0.2, color='white')  # 设置次级网格
        self.ax.axhline(0, color='white', linewidth=1)

    def plot(self, data):
        try:
            if not data:
                self.ax.clear()
                self.ax.set_ylim(-1, 1)
                self.ax.set_yticks(np.linspace(-1, 1, 6))
                self.ax.set_yticklabels([f'{tick:.2f}' for tick in np.linspace(-1, 1, 6)])

                self.initialize_plot()

                if self.count == 0:
                    self.ax.set_ylabel('FP1(uV)', rotation=90, labelpad=10)
                    self.text = self.ax.text(-0.18, 1, '', transform=self.ax.transAxes, ha='left',
                                             color='white', fontsize=16)

                elif self.count == 1:
                    self.ax.set_ylabel('FPz(uV)', rotation=90, labelpad=10)
                else:
                    self.ax.set_ylabel('FP2(uV)', rotation=90, labelpad=10)
                self.draw()
                return

            # 更新当前所有数据
            self.all_data.extend(data)

            # 如果数据超过1000个，则删除前250个数据点
            if len(self.all_data) > 1000:
                self.all_data = self.all_data[-1000:]

            # 对数据进行采样以减少密度
            sampling_interval = 1  # 调整此值以控制采样率
            sampled_data = self.all_data[::sampling_interval]
            sampled_indices = list(range(0, len(self.all_data), sampling_interval))

            # 计算当前批次数据的最大值和最小值
            max_val = max(sampled_data)
            min_val = min(sampled_data)

            if abs(max_val) < 1e-10 and abs(min_val) < 1e-10:
                # 当 min_val 和 max_val 都为 0 时
                if max_val == 0 and min_val == 0:
                    max_val, min_val = 0, 0
                elif min_val == 0:
                    if max_val > 0:
                        max_val, min_val = 1, 0
                elif max_val == 0:
                    if min_val < 0:
                        max_val, min_val = 0, -1
                # 其他正常情况处理
                else:
                    if min_val < 0 and max_val > 0:
                        max_val, min_val = 1, -1
                    elif min_val < 0 and max_val < 0:
                        max_val, min_val = 0, -1
                    elif min_val > 0:
                        max_val, min_val = 1, 0

            elif abs(max_val) < 1e-10:
                if max_val < 0:
                    max_val = 0
                else:
                    max_val = 1

            elif abs(min_val) < 1e-10:
                if min_val < 0:
                    min_val = -1
                else:
                    min_val = 0

            # 如果最大值和最小值相等，手动调整一个微小的差值，避免除以零
            if max_val == min_val:
                if min_val != 0:
                    max_val += 1e-5
                    min_val -= 1e-5

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
                if self.count == 0:
                    self.line, = self.ax.plot(sampled_indices, sampled_data, color='#00F5D4', linewidth=0.8)
                elif self.count == 1:
                    self.line, = self.ax.plot(sampled_indices, sampled_data, color='#00F5D4', linewidth=0.8)
                else:
                    self.line, = self.ax.plot(sampled_indices, sampled_data, color='#00F5D4', linewidth=0.8)
            else:
                # 更新数据，只删除前250个点并添加新的250个点
                self.line.set_data(sampled_indices, sampled_data)

            if self.count == 0:
                # 添加竖直标签
                self.ax.set_ylabel('FP1(uV)', rotation=90, labelpad=10)
                if self.parent.db_main.name:
                    self.text.set_text("姓名:" + self.parent.db_main.name)

            elif self.count == 1:
                self.ax.set_ylabel('FPz(uV)', rotation=90, labelpad=10)
            else:
                self.ax.set_ylabel('FP2(uV)', rotation=90, labelpad=10)

            self.draw()


        except Exception as ex:

            logger.error('=========%s', str(ex))


# class PlotThread(threading.Thread):
#     def __init__(self,canvas,canvas1, canvas2):
#         threading.Thread.__init__(self)
#         self.canvas = canvas
#         self.canvas1 = canvas1
#         self.canvas2 = canvas2
#
#         self.data_queue = queue.Queue() #队列
#         self.condition = threading.Condition() #锁
#
#         self.running = True
#
#     def run(self):
#         while self.running:
#             with self.condition:
#                 self.condition.wait()  # 等待条件变量被触发
#                 if not self.running:
#                     break
#                 while not self.data_queue.empty(): #实时更新
#                     data_buffer,data_buffer1, data_buffer2 = self.data_queue.get()
#                     self.canvas.plot(data_buffer)
#                     self.canvas1.plot(data_buffer1)
#                     self.canvas2.plot(data_buffer2)
#
#     def trigger_update(self,data_buffer,data_buffer1, data_buffer2):
#         with self.condition:
#             self.data_queue.put((data_buffer,data_buffer1, data_buffer2))
#             self.condition.notify()  # 触发条件变量，唤醒线程

class WgtLeft_eggItem(QWidget, Ui_left_eeg_form):
    update_signal = pyqtSignal(list, list, list)  # 定义信号

    def __init__(self, db_main):
        super(WgtLeft_eggItem, self).__init__()

        self.setupUi(self)
        self.db_main = db_main
        self.canvas = PlotCanvas(self, 0)
        self.verticalLayout.addWidget(self.canvas, stretch=1)  # 设置拉伸因子

        self.canvas1 = PlotCanvas(self, 1)
        self.verticalLayout.addWidget(self.canvas1, stretch=1)

        self.canvas2 = PlotCanvas(self, 2)
        self.verticalLayout.addWidget(self.canvas2, stretch=1)

        self.update_signal.connect(self.update_ui)  # 连接信号到槽

        self.data_queue = queue.Queue()  # 添加数据队列
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plots)
        self.timer.start(100)  # 每50毫秒更新一次图表

        self.canvas.plot([])
        self.canvas1.plot([])
        self.canvas2.plot([])

        # self.plot_thread = PlotThread(self.canvas,self.canvas1, self.canvas2)
        # self.plot_thread.start()

    @pyqtSlot(list, list, list)
    def update_ui(self, batch, batch1, batch2):
        self.data_queue.put((batch, batch1, batch2))

    def update_plots(self):
        while not self.data_queue.empty():
            data = self.data_queue.get()
            self.canvas.plot(data[0])
            self.canvas1.plot(data[1])
            self.canvas2.plot(data[2])
        # self.plot_thread.trigger_update(batch, batch1, batch2)


class EEGDataThread(QThread):
    def __init__(self, eeg_items, com_name, db_main):
        super().__init__()
        self.eeg_items = eeg_items
        self.accumulated_voltage = []

        self.db_main = db_main

        self.collect_flag = False
        self.save_flag = False
        self.count_flag = ""

        with open(set_file_path, 'r', encoding='utf-8') as file:
            self.settings = json.load(file)
        dll_path = get_actual_path('./ForPy/EEGSENSOR.dll')
        self.eegs_dll = ctypes.CDLL(dll_path)  # Replace with the actual path to
        # 这两个函数在代码的前半部分只是进行了定义，还没有实际调用

        # 用于解析EEG数据帧
        self.eegs_dll.ThreeLead_EEGSensor_DataFrameParse.argtypes = [ctypes.POINTER(ctypes.c_ubyte),
                                                                     ctypes.POINTER(ctypes.c_double)]
        self.eegs_dll.ThreeLead_EEGSensor_DataFrameParse.restype = ctypes.POINTER(ctypes.c_double)

        # 用于去除EEG数据中的噪声
        self.eegs_dll.ThreeLead_EEGSensor_DataDSP.argtypes = [ctypes.POINTER(ctypes.c_double),
                                                              ctypes.POINTER(ctypes.c_double)]
        self.eegs_dll.ThreeLead_EEGSensor_DataDSP.restype = ctypes.POINTER(ctypes.c_double)

        # 原18000行去噪函数
        # self.eegs_dll_18000 = ctypes.CDLL('./ForPy_18000/EEGSENSOR.dll')  # Replace with the actual path to
        # self.eegs_dll_18000.ThreeLead_EEGSensor_DataDSP.argtypes = [ctypes.POINTER(ctypes.c_double),
        #                                                             ctypes.POINTER(ctypes.c_double)]
        # self.eegs_dll_18000.ThreeLead_EEGSensor_DataDSP.restype = ctypes.POINTER(ctypes.c_double)

        # 用于判断EEG数据的质量
        self.eegs_dll.EEGQuality.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_int)]
        self.eegs_dll.EEGQuality.restype = ctypes.POINTER(ctypes.c_int)
        self.dsp_eeg_initData_fp1_fp2_fpz = [0] * 804

        # 存储原始字节数据
        self.rawbyte = (ctypes.c_ubyte * 37)()
        # 存储解析后的电压数据
        self.series_port_leads_datas = (ctypes.c_double * 3)()
        # 用于判断EEG数据的频谱
        queue_length = 1024
        self.data_queue_fp1 = deque([0] * queue_length, maxlen=queue_length)
        self.data_queue_fpz = deque([0] * queue_length, maxlen=queue_length)
        self.data_queue_fp2 = deque([0] * queue_length, maxlen=queue_length)
        self.eegs_dll.WaveUpDat_FFT_General.argtypes = [ctypes.POINTER(ctypes.c_double),
                                                        ctypes.POINTER(ctypes.c_double)]
        self.eegs_dll.WaveUpDat_FFT_General.restype = ctypes.POINTER(ctypes.c_double)

        # 通过指定的端口和波特率 与设备进行通信,如果1秒内没有读取到任何数据，读操作将会超时并返回
        port = com_name
        self.baudrate = 115200
        self.ser = ""
        # 这个串口对象用于 数据读取 和 写入操作。
        try:
            self.ser = serial.Serial(port, self.baudrate, timeout=1)

        except Exception as e:
            logger.error('db_left_egg/serial_join_error%s', str(e))
            self.requestInterruption()

    def waveUpDat_FFT(self, fp1, fpz, fp2):
        # 初始化
        spectrum_result_fp1 = [0] * 1024
        spectrum_result_fp1 = (ctypes.c_double * (1024))(*spectrum_result_fp1)
        spectrum_result_fpz = [0] * 1024
        spectrum_result_fpz = (ctypes.c_double * (1024))(*spectrum_result_fpz)
        spectrum_result_fp2 = [0] * 1024
        spectrum_result_fp2 = (ctypes.c_double * (1024))(*spectrum_result_fp2)
        # 将新的数据添加到队列中
        self.data_queue_fp1.extend(fp1)
        self.data_queue_fpz.extend(fpz)
        self.data_queue_fp2.extend(fp2)

        spectrum_fp1 = (ctypes.c_double * (1024))(*self.data_queue_fp1)
        spectrum_fpz = (ctypes.c_double * (1024))(*self.data_queue_fpz)
        spectrum_fp2 = (ctypes.c_double * (1024))(*self.data_queue_fp2)
        spectrum_result_fp1 = self.eegs_dll.WaveUpDat_FFT_General(spectrum_fp1, spectrum_result_fp1)
        spectrum_result_fpz = self.eegs_dll.WaveUpDat_FFT_General(spectrum_fpz, spectrum_result_fpz)
        spectrum_result_fp2 = self.eegs_dll.WaveUpDat_FFT_General(spectrum_fp2, spectrum_result_fp2)
        # 将结果转成numpy
        spectrum_result_fp1 = np.ctypeslib.as_array(
            ctypes.cast(spectrum_result_fp1, ctypes.POINTER(ctypes.c_double * (1024))).contents)
        spectrum_result_fpz = np.ctypeslib.as_array(
            ctypes.cast(spectrum_result_fpz, ctypes.POINTER(ctypes.c_double * (1024))).contents)
        spectrum_result_fp2 = np.ctypeslib.as_array(
            ctypes.cast(spectrum_result_fp2, ctypes.POINTER(ctypes.c_double * (1024))).contents)
        spectrum_result = np.column_stack((spectrum_result_fp1,
                                           spectrum_result_fpz,
                                           spectrum_result_fp2))
        # 画图横轴固定
        # x_fft_datas = [(i * (250 / 2)) / (1024 / 2) for i in range(1024 // 2)]
        y_fft_datas = spectrum_result[:512, :]

        return y_fft_datas

    def adjust_baseline(self, data):
        data_mean = np.mean(data)
        return data - data_mean

    def adjust_p1pzp2(self, p1pzp2_lst, fp):
        if isinstance(fp, str):
            p1pzp2_ = np.array(p1pzp2_lst) / eval(fp)
        else:
            p1pzp2_ = np.array(p1pzp2_lst) / fp

        p1pzp2_lst = p1pzp2_.reshape(-1, 3)
        p1 = p1pzp2_lst[:, 0].tolist()
        pz = p1pzp2_lst[:, 1].tolist()
        p2 = p1pzp2_lst[:, 2].tolist()
        return p1 + pz + p2

    def process_received_data(self, data, accumulated_voltage):
        # 填充 rawbyte 数组
        for i in range(min(len(data), 37)):
            self.rawbyte[i] = data[i]

        # 调用解析函数
        real_voltage_value = self.eegs_dll.ThreeLead_EEGSensor_DataFrameParse(self.rawbyte,
                                                                              self.series_port_leads_datas)
        real_voltage_value = np.ctypeslib.as_array(
            ctypes.cast(real_voltage_value, ctypes.POINTER(ctypes.c_double * (3))).contents)
        real_voltage_value = real_voltage_value * -1
        # 将解析出的电压值添加到 accumulated_voltage 列表中
        accumulated_voltage.append(real_voltage_value[0])
        accumulated_voltage.append(real_voltage_value[1])
        accumulated_voltage.append(real_voltage_value[2])

        # 如果累积的电压值足够多
        if len(accumulated_voltage) == 250 * 3:
            accumulated_voltage = self.adjust_p1pzp2(accumulated_voltage, self.settings['fp'])

            # 调用去噪函数
            raw_eeg_data_fp1_fp2 = (ctypes.c_double * (250 * 3))(*accumulated_voltage)
            dsp_eeg_data_fp1_fp2_fpz = (ctypes.c_double * (250 * 3 + 54))(*self.dsp_eeg_initData_fp1_fp2_fpz)
            eeg_data_without_noise = self.eegs_dll.ThreeLead_EEGSensor_DataDSP(raw_eeg_data_fp1_fp2,
                                                                               dsp_eeg_data_fp1_fp2_fpz)
            # 将去噪后的数据转换为 NumPy 数组
            eeg_data_without_noise_array_withargs = np.ctypeslib.as_array(
                ctypes.cast(eeg_data_without_noise, ctypes.POINTER(ctypes.c_double * (250 * 3 + 54))).contents)

            eeg_data_without_noise_array_show = np.column_stack((eeg_data_without_noise_array_withargs[:250],
                                                                 eeg_data_without_noise_array_withargs[250:250 * 2],
                                                                 eeg_data_without_noise_array_withargs[
                                                                 250 * 2:250 * 3]))
            self.dsp_eeg_initData_fp1_fp2_fpz[:] = eeg_data_without_noise_array_withargs[:]
            # print('参数值', self.dsp_eeg_initData_fp1_fp2_fpz[-18:])
            spectrum_show = self.waveUpDat_FFT(eeg_data_without_noise_array_withargs[:250],
                                               eeg_data_without_noise_array_withargs[250:250 * 2],
                                               eeg_data_without_noise_array_withargs[250 * 2:250 * 3])

            fp1fpzfp2_baseline = eeg_data_without_noise_array_withargs.tolist()

            # 准备输入数据
            EEGDatafp1FpzFp2 = (ctypes.c_double * (250 * 3))(*fp1fpzfp2_baseline[:750])  # EEG三导联数据
            EEGQualityFlag_init = np.zeros(3, dtype=np.int32)
            EEGQualityFlag_ctypes = EEGQualityFlag_init.ctypes.data_as(ctypes.POINTER(ctypes.c_int))

            # 调用函数
            EEGQualityFlag = self.eegs_dll.EEGQuality(EEGDatafp1FpzFp2, EEGQualityFlag_ctypes)
            EEGQualityFlag = np.ctypeslib.as_array(
                ctypes.cast(EEGQualityFlag, ctypes.POINTER(ctypes.c_int * (3))).contents)
            # print('质量参数', EEGQualityFlag)

            # 保留未去噪的原始数据
            eeg_data_without_noise_array_predict = np.column_stack((accumulated_voltage[:250],
                                                                    accumulated_voltage[250:250 * 2],
                                                                    accumulated_voltage[250 * 2:250 * 3]))
            # 移除已使用的数据
            accumulated_voltage = accumulated_voltage[250 * 3:]

            return eeg_data_without_noise_array_show, eeg_data_without_noise_array_predict, accumulated_voltage, EEGQualityFlag, spectrum_show
        return None, None, accumulated_voltage, None, None

    # 原读取数据函数
    def read_frame(self):
        # 函数用于从串口读取数据帧。它不断读取串口数据，直到找到一个完整的数据帧（包括帧头和帧尾），然后返回该数据帧。
        while True:
            # 读取一个字节
            if self.isInterruptionRequested():
                if self.ser:
                    if self.ser.is_open:
                        self.ser.write(b'uaisb')
                        self.ser.flush()
                        self.ser.close()
                return ""
            byte1 = self.ser.read(1)
            # 如果这个字节是帧头的第一个字节 0xA0
            if byte1 != b'':
                if byte1[0] == 0XA0:
                    # 再读取一个字节
                    byte2 = self.ser.read(1)
                    # 如果这个字节是帧头的第二个字节 0x10
                    if byte2[0] == 0X10:
                        # 读取其余的35个字节，形成一个完整的37字节帧
                        frame = byte1 + byte2 + self.ser.read(35)
                        # 检查帧的最后一个字节是否是帧尾 0xC0
                        if frame[-1] == 0xC0:
                            # 返回完整的37字节帧
                            return frame

    def run(self):
        if self.isInterruptionRequested():
            if self.ser:
                if self.ser.is_open:
                    self.ser.write(b'uaisb')
                    self.ser.flush()
                    self.ser.close()
            return

        try:
            print("Sending 'a'...")
            # 发送'uaisa'字符串以启动通信
            self.ser.write(b'uaisa')
            self.ser.flush()
            # 等待5秒以确保设备准备好

            wait_noblock()
            # 开始从串口读取数据
            print("Starting to read data...")
            # 初始化一个空数组以累积数据  即 0 行 3 列的二维数组。
            accumulated_data = np.empty((0, 3))

            predict_data = np.empty((0, 3))
            # 初始化一个列表以累积电压值
            accumulated_voltage = []

            while True:
                # 读取一个数据帧
                if self.isInterruptionRequested():
                    if self.ser:
                        if self.ser.is_open:
                            self.ser.write(b'uaisb')
                            self.ser.flush()
                            self.ser.close()
                    return

                frame = self.read_frame()

                if frame:
                    eeg_data_without_noise_array, eeg_data_without_noise_array_predict, accumulated_voltage, EEGQualityFlag, spectrum_show = self.process_received_data(
                        frame,
                        accumulated_voltage)
                    if eeg_data_without_noise_array is not None:
                        # 将去噪后的EEG数据添加到累积的数据中
                        column1, column2, column3 = eeg_data_without_noise_array.transpose().tolist()

                        column4, column5, column6 = spectrum_show.transpose().tolist()
                        self.eeg_items[0].update_signal.emit(column1, column2, column3)

                        if EEGQualityFlag is not None:
                            self.eeg_items[1].update_signal.emit(EEGQualityFlag[0], EEGQualityFlag[1],
                                                                 EEGQualityFlag[2], column4[:250], column5[:250],
                                                                 column6[:250])
                        else:
                            self.eeg_items[1].update_signal.emit(None, None, None, column4[:250], column5[:250],
                                                                 column6[:250])

                        if self.collect_flag:
                            eeg_data_without_noise_array[np.abs(eeg_data_without_noise_array) < 1e-15] = 1e-6
                            accumulated_data = np.vstack((accumulated_data, eeg_data_without_noise_array))

                            if self.count_flag == 2:
                                eeg_data_without_noise_array_predict[
                                    np.abs(eeg_data_without_noise_array_predict) < 1e-15] = 1e-6
                                predict_data = np.vstack((predict_data, eeg_data_without_noise_array_predict))

                    if self.save_flag:
                        save_path = self.settings["save_path"]
                        dir_path = os.path.join(save_path, self.db_main.phone)
                        if not os.path.exists(dir_path):
                            os.makedirs(dir_path)

                        # 动态设置 csv_file 路径
                        csv_suffix = "_s" if self.count_flag == 2 else ""
                        csv_file = os.path.join(dir_path,
                                                f"{self.db_main.phone}_{self.db_main.name}_{self.db_main.count}{csv_suffix}.csv")

                        self.db_main.csv_file_s = csv_file

                        if accumulated_data.shape[0] >= 18000:
                            eeg_data = accumulated_data[-18000:]

                        else:
                            eeg_data = accumulated_data

                        df = pd.DataFrame(data=eeg_data)
                        df.to_csv(csv_file, index=False, header=False)

                        if self.count_flag == 2:
                            csv_file_r = os.path.join(dir_path,
                                                      f"{self.db_main.phone}_{self.db_main.name}_{self.db_main.count}_r.csv")
                            if accumulated_data.shape[0] >= 18000:
                                eeg_data_r = predict_data[-18000:]
                            else:
                                eeg_data_r = predict_data
                            df = pd.DataFrame(data=eeg_data_r)
                            df.to_csv(csv_file_r, index=False, header=False)

                            self.count_flag = ""
                            # 在生成三个小的csv
                            csv_file1 = os.path.join(dir_path,
                                                     f"{self.db_main.phone}_{self.db_main.name}_{self.db_main.count}_FP1.csv")
                            csv_file2 = os.path.join(dir_path,
                                                     f"{self.db_main.phone}_{self.db_main.name}_{self.db_main.count}_FPz.csv")
                            csv_file3 = os.path.join(dir_path,
                                                     f"{self.db_main.phone}_{self.db_main.name}_{self.db_main.count}_FP2.csv")
                            df.iloc[:, 0].to_csv(csv_file1, index=False, header=False)
                            df.iloc[:, 1].to_csv(csv_file2, index=False, header=False)
                            df.iloc[:, 2].to_csv(csv_file3, index=False, header=False)

                        accumulated_data = np.empty((0, 3))
                        predict_data = np.empty((0, 3))
                        accumulated_voltage = []
                        self.save_flag = False

        except Exception as e:
            logger.error('db_left_egg/send_serial_data_error/%s', str(e))
        finally:
            if self.ser:
                if self.ser.is_open:
                    self.ser.write(b'uaisb')
                    self.ser.flush()
                    self.ser.close()
