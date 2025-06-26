import queue
import threading
import time

import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, pyqtSlot,Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.ticker import AutoMinorLocator, AutoLocator
from matplotlib.ticker import MaxNLocator
from gui.right_egg import Ui_right_eeg_form
from utils.utils import wait_noblock, wait_noblock_
from utils.logger import logger
import pandas as pd

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None,count=None):
        fig = Figure() # 创建一个新的图形对象
        self.ax = fig.add_subplot(111) #添加子图
        super().__init__(fig)
        self.setParent(parent)
        self.parent=parent
        self.setAttribute(Qt.WA_OpaquePaintEvent, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_PaintOnScreen, False)

        self.count=count
        #self.all_data = []
        # self.all_data = [] # 初始化为 NumPy 数组
        self.line=""
        fig.subplots_adjust(left=0.25)  # 调整图形在窗口中的位置

        self.initialize_plot()
        # # 设置背景颜色
        fig.patch.set_facecolor('#000814')  # 图形背景颜色
        self.ax.set_facecolor('#000814')  # 坐标轴区域背景颜色
        # 固定的横坐标
        self.fixed_x = [(i * 125) / 512 for i in range(512)][:250]


    def initialize_plot(self):
        major_ticks = np.arange(0, 80, 20)
        # major_ticks = [(i * (250 / 2)) / (1024 / 2) for i in range(1024 // 2)] # 设置x轴刻度为0, 200, 400, 600, 800, 1000
        self.ax.set_xticks(major_ticks)
        self.ax.set_xlim(0, 65)

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
        self.ax.xaxis.label.set_fontsize(14)  # X轴标签
        self.ax.yaxis.label.set_fontsize(14)  # Y轴标签

        # 增大刻度标签字体大小
        self.ax.tick_params(axis='both', which='major', labelsize=14)

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
                    self.text = self.ax.text(0.5, 1.07, '频谱图(uV2)', transform=self.ax.transAxes, ha='center',
                                               color='#FCD34D', fontsize=15, va='center')
                elif self.count == 1:
                    self.text_2 = self.ax.text(0.5, 1.07, '频谱图(uV2)', transform=self.ax.transAxes, ha='center',
                      color='#FCD34D', fontsize=15, va='center')

                else:
                    self.text_3 = self.ax.text(0.5, 1.07, '频谱图(uV2)', transform=self.ax.transAxes, ha='center',
                                               color='#FCD34D', fontsize=15, va='center')

                self.draw()
                return

            # 对数据进行采样以减少密度
            sampling_interval = 1  # 调整此值以控制采样率
            sampled_data = data[::sampling_interval]
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
            self.ax.set_yticklabels([f'{tick:.2e}' for tick in ticks])

            if not self.line:
                if self.count==0:
                    self.line, = self.ax.plot(self.fixed_x, sampled_data, color='#FF9E00', linewidth=0.8)
                elif self.count==1:
                    self.line, = self.ax.plot(self.fixed_x, sampled_data, color='#FF9E00', linewidth=0.8)
                else:
                    self.line, = self.ax.plot(self.fixed_x, sampled_data, color='#FF9E00', linewidth=0.8)
            else:
                # 更新数据，只删除前250个点并添加新的250个点
                self.line.set_data(self.fixed_x, sampled_data)

            self.draw()

        except Exception as ex:

            logger.error('=========%s', str(ex))

class WgtRight(QWidget):
    update_signal = pyqtSignal(object,object,object,list,list,list)  # 定义信号
    def __init__(self):
        super(WgtRight, self).__init__()
        self.vbox = QVBoxLayout(self)
        self.WgtRight_1 = WgtRight_eggItem(0)
        self.WgtRight_1.label_2.setText("FP1信号质量")

        self.WgtRight_2 = WgtRight_eggItem(1)
        self.WgtRight_2.label_2.setText("FPz信号质量")

        self.WgtRight_3 = WgtRight_eggItem(2)
        self.WgtRight_3.label_2.setText("FP2信号质量")

        self.vbox.addWidget(self.WgtRight_1, stretch=1)
        self.vbox.addWidget(self.WgtRight_2, stretch=1)
        self.vbox.addWidget(self.WgtRight_3, stretch=1)

        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.vbox.setSpacing(0)

        self.setLayout(self.vbox)

        self.update_signal.connect(self.update_ui)  # 连接信号到槽

        self.data_queue = queue.Queue()  # 添加数据队列
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plots)
        self.timer.start(100)  # 每50毫秒更新一次图表

        self.WgtRight_1.canvas.plot([])
        self.WgtRight_2.canvas.plot([])
        self.WgtRight_3.canvas.plot([])


    def update_plots(self):
        while not self.data_queue.empty():
            data = self.data_queue.get()
            self.WgtRight_1.canvas.plot(data[0])
            self.WgtRight_2.canvas.plot(data[1])
            self.WgtRight_3.canvas.plot(data[2])

    @pyqtSlot(object,object,object,list,list,list)
    def update_ui(self,color_number,color_number2,color_number3,batch, batch1, batch2):
        self.data_queue.put((batch, batch1, batch2))

        if color_number is None:
            pass
        elif color_number == 1:
            self.WgtRight_1.label_2.setStyleSheet('background-color: green; border-radius: 15px;font: 75 15pt "思源黑体 CN Bold";')
        else:
            self.WgtRight_1.label_2.setStyleSheet('background-color: red; border-radius: 15px;font: 75 15pt "思源黑体 CN Bold";')

        if color_number2 is None:
            pass
        elif color_number2 == 1:
            self.WgtRight_2.label_2.setStyleSheet('background-color: green; border-radius: 15px;font: 75 15pt "思源黑体 CN Bold";')
        else:
            self.WgtRight_2.label_2.setStyleSheet('background-color: red; border-radius: 15px;font: 75 15pt "思源黑体 CN Bold";')

        if color_number3 is None:
            pass
        elif color_number3 == 1:
            self.WgtRight_3.label_2.setStyleSheet('background-color: green; border-radius: 15px;font: 75 15pt "思源黑体 CN Bold";')
        else:
            self.WgtRight_3.label_2.setStyleSheet('background-color: red; border-radius: 15px;font: 75 15pt "思源黑体 CN Bold";')


class WgtRight_eggItem(QWidget, Ui_right_eeg_form):
    def __init__(self,count):
        super(WgtRight_eggItem, self).__init__()
        self.setupUi(self)

        self.canvas = PlotCanvas(self,count)
        self.verticalLayout.addWidget(self.canvas)



