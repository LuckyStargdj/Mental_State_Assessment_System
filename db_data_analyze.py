import random

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QCursor, QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListView

from gui.new_untitled import Ui_analyze_form
from gui.untitled import Ui_data_
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.patches as patches
import pandas as pd
class PieChart_right(FigureCanvas):
    def __init__(self, parent=None, rang_list=None, data_count=None,type=None):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111, aspect='equal')
        super(PieChart_right, self).__init__(self.fig)
        self.setParent(parent)

        self.type=type
        self.ranges = rang_list  # 每个区间的范围百分比
        self.data = [float(x) for x in data_count]  # 确保数据为数字类型

        self.colors = ["rgb(50,145,248)",'rgb(235,244,255)']
        # 将颜色从 "rgb(r, g, b)" 格式转换为 Matplotlib 可识别的 (r, g, b) 元组格式
        self.colors = [self.rgb_to_mpl(color) for color in self.colors]

        self.fig.patch.set_facecolor((245 / 255, 245 / 255, 245 / 255))  #

        self.legend_labels = ["正常","异常"]  # 图例文字
        self.plot_pie()

    def rgb_to_mpl(self, rgb_string):
        # 移除前缀 "rgb(" 和后缀 ")"，并将 RGB 值拆分为整数列表
        rgb_values = rgb_string.replace("rgb(", "").replace(")", "").split(',')
        # 转换为 0-1 范围内的浮点数，并返回元组格式
        return tuple(int(value.strip()) / 255.0 for value in rgb_values)

    def clear_and_clean(self):
        # 清除图形和图例
        self.ax.clear()
        self.ax.axis('off')  # 隐藏坐标轴
        self.draw()  # 更新画布以反映清除操作

    def plot_pie(self):
        self.ax.clear()
        self.ax.axis('off')  # 隐藏坐标轴

        # 绘制饼图
        wedges, texts, autotexts = self.ax.pie(
            self.data,
            colors=self.colors,
            autopct='',  # 不自动绘制百分比
            startangle=90,  # 起始角度
            wedgeprops={'width': 0.5}  # 设置宽度
        )

        # 调整注释的位置
        annotation_positions = []
        for i, wedge in enumerate(wedges):
            if self.ranges[i] == 0:
                continue  # 跳过范围为0的扇区

            # 计算注释的角度和位置
            angle = (wedge.theta2 + wedge.theta1) / 2
            x = wedge.r * np.cos(np.deg2rad(angle))
            y = wedge.r * np.sin(np.deg2rad(angle))

            distance_multiplier = 1.55  # 调整基础距离倍数
            dx = distance_multiplier * x
            dy = distance_multiplier * y

            # # 防止标签重叠
            for ann_x, ann_y in annotation_positions:
                while np.hypot(dx - ann_x, dy - ann_y) < 1:  # 增加最小距离
                    dx += 0.7 * np.sign(dx - ann_x)
                    # dy += 0.08 * np.sign(dy - ann_y)

            # 限制标签位置在视图内
            dx = np.clip(dx, -1.5, 1.5)
            dy = np.clip(dy, -1.5, 1.5)

            xytext = (dx, dy)
            bbox_props = dict(boxstyle="round,pad=0.3", edgecolor="none", facecolor=self.colors[i], alpha=0.5)
            if self.type==0:
                # 添加百分比标签作为注释
                self.ax.annotate(
                    f'0%,0人',  # 使用 \n 换行
                    xy=(x, y),
                    xytext=xytext,
                    arrowprops=dict(
                        arrowstyle="-",
                        connectionstyle="arc3,rad=0.3",  # 让箭头弯曲，调整 rad 的值可以改变弯曲度
                        color='black'
                    ),
                    horizontalalignment='center',
                    verticalalignment='center',
                    bbox=bbox_props,
                    fontproperties='Microsoft YaHei', fontsize=12
                )
                annotation_positions.append((dx, dy))
            else:
                # 添加百分比标签作为注释
                self.ax.annotate(
                    f'{self.legend_labels[i]}\n{self.ranges[i]}%,{int(self.data[i])}人',  # 使用 \n 换行
                    xy=(x, y),
                    xytext=xytext,
                    arrowprops=dict(
                        arrowstyle="-",
                        connectionstyle="arc3,rad=0.3",  # 让箭头弯曲，调整 rad 的值可以改变弯曲度
                        color='black'
                    ),
                    horizontalalignment='center',
                    verticalalignment='center',
                    bbox=bbox_props,
                    fontproperties='Microsoft YaHei', fontsize=12
                )
                annotation_positions.append((dx, dy))

        # 调整饼图的位置以给图例留出空间
        self.ax.set_position([0.2, 0.38, 0.55, 0.55])
        # 创建图例句柄并将图例移动到饼图下方
        legend_handles = [patches.Patch(color=color, label=label) for color, label in
                          zip(self.colors, self.legend_labels)]
        self.ax.legend(
            handles=legend_handles,
            loc='upper center',  # 将图例放置在饼图下方
            bbox_to_anchor=(0.5, -0.15),  # 将图例水平居中放置在饼图下方
            ncol=4,  # 将图例项水平排列成一行
            fontsize=13.5,  # 调小字体大小
            handletextpad=0.3,  # 缩小图例标记与文本之间的距离
            columnspacing=0.5, #减少图例项之间的水平间距
            frameon=False  # 去掉图例框
        )

        self.draw()  # 重绘更新后的图形

class PieChart(FigureCanvas):
    def __init__(self, parent=None, rang_list=None, data_count=None,type=None):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111, aspect='equal')
        super(PieChart, self).__init__(self.fig)
        self.setParent(parent)

        self.type=type
        self.ranges = rang_list  # 每个区间的范围百分比
        self.data = [float(x) for x in data_count]  # 确保数据为数字类型
        #self.colors = [(0.6, 1, 0.6), 'orange', 'red']

        self.colors = ["rgb(184,217,253)", 'rgb(122,184,251)', 'rgb(50,145,248)', 'rgb(166,236,255)']
        # 将颜色从 "rgb(r, g, b)" 格式转换为 Matplotlib 可识别的 (r, g, b) 元组格式
        self.colors = [self.rgb_to_mpl(color) for color in self.colors]

        self.fig.patch.set_facecolor((245 / 255, 245 / 255, 245 / 255))

        self.legend_labels = ["正常", "轻度", "中度", "重度"]  # 图例文字
        self.ann_flag=False
        self.plot_pie()

    def rgb_to_mpl(self, rgb_string):
        # 移除前缀 "rgb(" 和后缀 ")"，并将 RGB 值拆分为整数列表
        rgb_values = rgb_string.replace("rgb(", "").replace(")", "").split(',')
        # 转换为 0-1 范围内的浮点数，并返回元组格式
        return tuple(int(value.strip()) / 255.0 for value in rgb_values)

    def clear_and_clean(self):
        # 清除图形和图例
        self.ax.clear()
        self.ax.axis('off')  # 隐藏坐标轴
        self.draw()  # 更新画布以反映清除操作

    def plot_pie(self):
        self.ax.clear()
        self.ax.axis('off')  # 隐藏坐标轴

        # 绘制饼图
        wedges, texts, autotexts = self.ax.pie(
            self.data,
            colors=self.colors,
            autopct='',  # 不自动绘制百分比
            startangle=90,  # 起始角度
            wedgeprops={'width': 0.5}  # 设置宽度
        )

        # 调整注释的位置
        annotation_positions = []
        for i, wedge in enumerate(wedges):
            if self.ranges[i] == 0:
                continue  # 跳过范围为0的扇区

            # 计算注释的角度和位置
            angle = (wedge.theta2 + wedge.theta1) / 2
            x = wedge.r * np.cos(np.deg2rad(angle))
            y = wedge.r * np.sin(np.deg2rad(angle))

            distance_multiplier = 1.45  # 调整基础距离倍数
            dx = distance_multiplier * x
            dy = distance_multiplier * y

            # # 防止标签重叠
            for ann_x, ann_y in annotation_positions:
                while np.hypot(dx - ann_x, dy - ann_y) < 1:  # 增加最小距离
                    dx += 0.7 * np.sign(dx - ann_x)
                    self.ann_flag=True
                    # dy += 0.08 * np.sign(dy - ann_y)
            if not self.ann_flag:
                distance_multiplier = 1.55
                dx = distance_multiplier * x
                dy = distance_multiplier * y

            # 限制标签位置在视图内
            dx = np.clip(dx, -1.8, 1.8)
            dy = np.clip(dy, -1.8, 1.8)

            xytext = (dx, dy)
            bbox_props = dict(boxstyle="round,pad=0.3", edgecolor="none", facecolor=self.colors[i], alpha=0.5)

            if self.type==0:
                self.ax.annotate(
                    f'0%,0人',  # 使用 \n 换行
                    xy=(x, y),
                    xytext=xytext,
                    arrowprops=dict(
                        arrowstyle="-",
                        connectionstyle="arc3,rad=0.3",  # 让箭头弯曲，调整 rad 的值可以改变弯曲度
                        color='black'
                    ),
                    horizontalalignment='center',
                    verticalalignment='center',
                    bbox=bbox_props,
                    fontproperties='Microsoft YaHei', fontsize=12
                )
                annotation_positions.append((dx, dy))
            else:
                # 添加百分比标签作为注释
                self.ax.annotate(
                    f'{self.legend_labels[i]}\n{self.ranges[i]}%,{int(self.data[i])}人',  # 使用 \n 换行
                    xy=(x, y),
                    xytext=xytext,
                    arrowprops=dict(
                        arrowstyle="-",
                        connectionstyle="arc3,rad=0.3",  # 让箭头弯曲，调整 rad 的值可以改变弯曲度
                        color='black'
                    ),
                    horizontalalignment='center',
                    verticalalignment='center',
                    bbox=bbox_props,
                    fontproperties='Microsoft YaHei', fontsize=12
                )
                annotation_positions.append((dx, dy))

        # 调整饼图的位置以给图例留出空间
        self.ax.set_position([0.2, 0.38, 0.55, 0.55])  # 调整以居中饼图并在下方留出空间

        # 创建图例句柄并将图例移动到饼图下方
        legend_handles = [patches.Patch(color=color, label=label) for color, label in
                          zip(self.colors, self.legend_labels)]
        self.ax.legend(
            handles=legend_handles,
            loc='upper center',  # 将图例放置在饼图下方
            bbox_to_anchor=(0.5, -0.15),  # 将图例水平居中放置在饼图下方
            ncol=4,  # 将图例项水平排列成一行
            fontsize=14,  # 调小字体大小
            handletextpad=0.3,  # 缩小图例标记与文本之间的距离
            columnspacing=1,  # 减少图例项之间的水平间距
            frameon=False  # 去掉图例框
        )

        self.draw()  # 重绘更新后的图形

class PieChart_statistics(FigureCanvas):
    def __init__(self, parent=None, rang_list=None, data_count=None,type=None):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111, aspect='equal')
        super(PieChart_statistics, self).__init__(self.fig)
        self.setParent(parent)


        self.ranges = rang_list  # 每个区间的范围百分比
        self.data = [float(x) for x in data_count]  # 确保数据为数字类型
        #self.colors = ['green','red',"","","","","","",""]

        self.colors = ["rgb(184,217,253)", 'rgb(122,184,251)', 'rgb(50,145,248)', 'rgb(166,236,255)', 'rgb(89,219,255)', 'rgb(0,199,255)', 'rgb(153,162,234)', 'rgb(105,105,213)','rgb(54,54,219)']
        # 将颜色从 "rgb(r, g, b)" 格式转换为 Matplotlib 可识别的 (r, g, b) 元组格式
        self.colors = [self.rgb_to_mpl(color) for color in self.colors]

        self.fig.patch.set_facecolor((245 / 255, 245 / 255, 245 / 255))
        self.ann_flag=False
        self.legend_labels = ["轻抑轻焦", "轻抑中焦","轻抑重焦","中抑轻焦","中抑中焦","中抑重焦","重抑轻焦","重抑中焦","重抑重焦"]  # 图例文字
        self.type=type
        self.plot_pie()

    def rgb_to_mpl(self, rgb_string):
        # 移除前缀 "rgb(" 和后缀 ")"，并将 RGB 值拆分为整数列表
        rgb_values = rgb_string.replace("rgb(", "").replace(")", "").split(',')
        # 转换为 0-1 范围内的浮点数，并返回元组格式
        return tuple(int(value.strip()) / 255.0 for value in rgb_values)

    def clear_and_clean(self):
        # 清除图形和图例
        self.ax.clear()
        self.ax.axis('off')  # 隐藏坐标轴
        self.draw()  # 更新画布以反映清除操作

    def plot_pie(self):
        self.ax.clear()
        self.ax.axis('off')  # 隐藏坐标轴
        # 绘制饼图
        wedges, texts, autotexts = self.ax.pie(
            self.data,
            colors=self.colors,
            autopct='',  # 不自动绘制百分比
            startangle=90,  # 起始角度
            wedgeprops={'width': 0.5}  # 设置宽度
        )


        annotation_positions = []
        for i, wedge in enumerate(wedges):
            if self.ranges[i] == 0:
                continue  # 跳过范围为0的扇区

            angle = (wedge.theta2 + wedge.theta1) / 2
            x = wedge.r * np.cos(np.deg2rad(angle))
            y = wedge.r * np.sin(np.deg2rad(angle))

            distance_multiplier = 1.45  # 调整基础距离倍数
            dx = distance_multiplier * x
            dy = distance_multiplier * y

            # # 防止标签重叠
            for ann_x, ann_y in annotation_positions:
                while np.hypot(dx - ann_x, dy - ann_y) < 1:  # 增加最小距离
                    dx += 0.7 * np.sign(dx - ann_x)
                    self.ann_flag = True
                    # dy += 0.08 * np.sign(dy - ann_y)
            if not self.ann_flag:
                distance_multiplier = 1.55
                dx = distance_multiplier * x
                dy = distance_multiplier * y

            # 防止超出视角
            dx = np.clip(dx, -1.5, 1.5)
            dy = np.clip(dy, -1.5, 1.5)

            xytext = (dx, dy)
            bbox_props = dict(boxstyle="round,pad=0.3", edgecolor="none", facecolor=self.colors[i], alpha=0.5)

            # 调整箭头指向
            # 调整箭头指向
            if self.type==0:
                self.ax.annotate(
                    f'0%,0人',  # 使用 \n 换行
                    xy=(x, y),
                    xytext=xytext,
                    arrowprops=dict(
                        arrowstyle="-",
                        connectionstyle="arc3,rad=0.3",  # 让箭头弯曲，调整 rad 的值可以改变弯曲度
                        color='black'
                    ),
                    horizontalalignment='center',
                    verticalalignment='center',
                    bbox=bbox_props,
                    fontproperties='Microsoft YaHei', fontsize=12
                )
                annotation_positions.append((dx, dy))
            else:
                self.ax.annotate(
                    f'{self.legend_labels[i]}\n{self.ranges[i]}%,{int(self.data[i])}人',  # 使用 \n 换行
                    xy=(x, y),
                    xytext=xytext,
                    arrowprops=dict(
                        arrowstyle="-",
                        connectionstyle="arc3,rad=0.3",  # 让箭头弯曲，调整 rad 的值可以改变弯曲度
                        color='black'
                    ),
                    horizontalalignment='center',
                    verticalalignment='center',
                    bbox=bbox_props,
                    fontproperties='Microsoft YaHei', fontsize=12
                )
                annotation_positions.append((dx, dy))

        # 添加图例
        # 调整饼图的位置
        #self.ax.set_position([0.2, 0.07, 0.70, 0.80])  # 调整饼图以腾出空间给图例
        self.ax.set_position([0.35, 0.38, 0.55, 0.55])  # 调整以居中饼图并在下方留出空间
        legend_handles = [patches.Patch(color=color, label=label) for color, label in
                          zip(self.colors, self.legend_labels)]

        self.legend=self.ax.legend(
            handles=legend_handles,
            loc='center left',  # 将图例放置在左边中部
            bbox_to_anchor=(-0.85, 0.55),  # 调整图例的位置
            ncol=1,  # 每行显示1个条目，这样垂直显示
            fontsize=14,  # 增大图例中文字的字体大小
            handletextpad=0.5,  # 缩短图例标签和图例标记之间的距离
            columnspacing=1.0,  # 缩短图例列之间的距离
        )
        self.legend.get_frame().set_facecolor((245/255, 245/255, 245/255))  # 设置为浅灰色
        # 去掉图例的边框
        self.legend.get_frame().set_edgecolor('none')  # 移除边框颜色
        self.draw()  # 重新绘制图形

class WgtData_Analyze(QWidget, Ui_analyze_form):
    def __init__(self,api):
        super(WgtData_Analyze, self).__init__()
        self.setupUi(self)


        self.setWindowFlags(Qt.FramelessWindowHint) #无边框

        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setWindowIcon(QIcon(":/icon/res/logo.png"))
        self.setWindowTitle('数据分析')

        self.comboBox_4.setView(QListView())  # 性别
        self.comboBox_4.addItems(["所有","男", "女"])
        self.comboBox_4.setCurrentIndex(0)

        self.comboBox_4.currentIndexChanged.connect(self.on_combobox_index_changed_sex)

        self.pbhide_6.setMouseTracking(True)
        self.pbhide_6.setToolTip("窗口最小化")
        self.pbhide_6.clicked.connect(self.showMinimized)

        self.pbClose_5.setMouseTracking(True)
        self.pbClose_5.setToolTip("关闭程序")
        self.pbClose_5.clicked.connect(self.close)
        self.pie_chart_statistics=None
        self.pie_chart_right = None
        self.pie_chart1 = None
        self.pie_chart = None
        self.api=api

        self.comboBox_12.setView(QListView())
        res, school_list = self.api.get_school_order_by()
        self.comboBox_12.addItem("请选择")
        self.comboBox_12.addItems(school_list)
        self.comboBox_12.setCurrentIndex(0)


        self.comboBox_10.setView(QListView())
        self.comboBox_11.setView(QListView())  # 学校

        self.comboBox_12.currentIndexChanged.connect(self.on_combobox_index_changed)
        self.comboBox_10.currentIndexChanged.connect(self.on_combobox_index_changed)
        self.comboBox_11.currentIndexChanged.connect(self.on_combobox_index_changed)

        self.school_name = ""
        self.grade_name = ""

        self.textEdit_2.setFont(QFont("Microsoft YaHei", 10))
        self.textEdit_5.setFont(QFont("Microsoft YaHei", 10))
        self.textEdit_4.setFont(QFont("Microsoft YaHei", 10))
        self.textEdit_3.setFont(QFont("Microsoft YaHei", 10))

        self.textEdit_2.setReadOnly(True)
        self.textEdit_5.setReadOnly(True)
        self.textEdit_4.setReadOnly(True)
        self.textEdit_3.setReadOnly(True)

        self.textEdit_2.setText("")
        self.textEdit_5.setText("")
        self.textEdit_4.setText("")
        self.textEdit_3.setText("")

        self.init_data()

    def on_combobox_index_changed(self):
        try:
            self.comboBox_12.blockSignals(True)
            self.comboBox_10.blockSignals(True)
            self.comboBox_11.blockSignals(True)

            school_text = self.comboBox_12.currentText()
            sender = self.sender()

            if self.comboBox_12.currentText() == "请选择":
                self.comboBox_11.clear()
                self.comboBox_10.clear()

            if self.comboBox_10.currentText() == "请选择":
                self.comboBox_11.clear()

            if sender == self.comboBox_12:
                self.comboBox_10.clear()
                self.comboBox_11.clear()

                if school_text=="请选择":
                    school_text =""
                res, grade_list = self.api.get_grade_order_by(school_text)
                self.comboBox_10.addItem("请选择")
                self.comboBox_10.addItems(grade_list)
                self.comboBox_10.setCurrentIndex(0)

            if sender == self.comboBox_10:
                self.comboBox_11.clear()
                grade_text = self.comboBox_10.currentText()

                if school_text=="请选择":
                    school_text =""
                if grade_text=="请选择":
                    grade_text =""

                res, class_list = self.api.get_class_order_by(school_text, grade_text)
                self.comboBox_11.addItem("请选择")
                self.comboBox_11.addItems(class_list)
                self.comboBox_11.setCurrentIndex(0)

        finally:
            # 重新启用信号
            self.comboBox_12.blockSignals(False)
            self.comboBox_10.blockSignals(False)
            self.comboBox_11.blockSignals(False)

        self.search_()

    def search_(self):
        school = self.comboBox_12.currentText()
        if school == "请选择":
            school = ""
        grade = self.comboBox_10.currentText()
        if grade == "请选择":
            grade = ""

        Class = self.comboBox_11.currentText()
        if Class == "请选择":
            Class = ""

        res, self.totle_dict = self.api.totle_check_people(school=school, grade=grade,Class=Class)

        res, self.normal_dict = self.api.is_normal_people(school=school, grade=grade,Class=Class)

        res, self.depressed_dict = self.api.is_depressed_people(school=school, grade=grade,Class=Class)

        res, self.anxiety_dict = self.api.is_anxiety_people(school=school, grade=grade,Class=Class)

        res, self.anxiety_depression_dict = self.api.is_anxiety_depression_comorbidity_people(school=school,
                                                                                              grade=grade,Class=Class)

        res, self.depression_statistics_dict = self.api.is_depression_statistics(school=school, grade=grade,Class=Class)

        res, self.anxiety_statistics_dict = self.api.is_anxiety_statistics(school=school, grade=grade,Class=Class)

        res, self.statistics_dict = self.api.is_anxiety_depression_statistics(school=school, grade=grade,Class=Class)

        self.school_name = school
        self.grade_name = grade
        self.on_combobox_index_changed_sex()

    def on_combobox_index_changed_sex(self):
        if self.comboBox_4.currentText() == "所有":
            self.init_data_man_woman()
        elif self.comboBox_4.currentText() == "女":
            self.init_data_woman()
        elif self.comboBox_4.currentText() == "男":
            self.init_data_man()

    def init_data_man(self):

        self.label_8.setText("")
        self.label_21.setText("")
        self.label_29.setText("")
        self.label_14.setText("")
        self.label_35.setText("")

        self.label_4.setText(str(self.totle_dict['male_total']))  # 总人数
        self.label_6.setText(str(self.totle_dict['male_total']))  # 男人数

        self.label_16.setText(str(self.normal_dict["male_normal_total"]))  # 正常
        self.label_19.setText(str(self.normal_dict["male_normal_total"]))  # 男正常

        self.label_24.setText(str(self.depressed_dict["male_depressed_total"]))  # 抑郁
        self.label_26.setText(str(self.depressed_dict["male_depressed_total"]))  # 男抑郁

        self.label_10.setText(str(self.anxiety_dict["male_anxiety_total"]))  # 焦虑
        self.label_12.setText(str(self.anxiety_dict["male_anxiety_total"]))  # 男正常

        self.label_31.setText(str(self.anxiety_depression_dict["male_comorbidity_total"]))  # 抑郁焦虑
        self.label_33.setText(str(self.anxiety_depression_dict["male_comorbidity_total"]))  # 男抑郁焦虑

        # 共病表没加
        if self.anxiety_depression_dict["male_comorbidity_total"] == 0:
            comment_4 = f"根据图表可知总检测{self.totle_dict['male_total']}人中，未发现有共病情况存在。"
            self.textEdit_3.setText(comment_4)
            rang_list = [100, 0, 0, 0, 0, 0, 0, 0, 0]
            data_count = ["1", "0", "0", "0", "0", "0", "0", "0", "0"]
            if self.pie_chart_statistics:
                self.pie_chart_statistics.type = 0
                self.pie_chart_statistics.ranges = rang_list
                self.pie_chart_statistics.data = [float(x) for x in data_count]
                self.pie_chart_statistics.plot_pie()
            else:
                self.pie_chart_statistics = PieChart_statistics(self, rang_list, data_count, 0)
                self.verticalLayout_15.addWidget(self.pie_chart_statistics)
        else:
            abnormal_1 = round((self.statistics_dict["male_mild_light_total"] / self.anxiety_depression_dict[
                "male_comorbidity_total"]) * 100)  # 抑郁焦虑

            abnormal_2 = round((self.statistics_dict["male_moderate_light_total"] / self.anxiety_depression_dict[
                "male_comorbidity_total"]) * 100)  # 抑郁焦虑

            abnormal_3 = round((self.statistics_dict["male_severe_light_total"] / self.anxiety_depression_dict[
                "male_comorbidity_total"]) * 100)  # 抑郁焦虑

            abnormal_4 = round((self.statistics_dict["male_mild_moderate_total"] / self.anxiety_depression_dict[
                "male_comorbidity_total"]) * 100)  # 抑郁焦虑

            abnormal_5 = round(
                (self.statistics_dict["male_moderate_moderate_total"] / self.anxiety_depression_dict[
                    "male_comorbidity_total"]) * 100)  # 抑郁焦虑

            abnormal_6 = round((self.statistics_dict["male_severe_moderate_total"] / self.anxiety_depression_dict[
                "male_comorbidity_total"]) * 100)  # 抑郁焦虑

            abnormal_7 = round((self.statistics_dict["male_mild_severe_total"] / self.anxiety_depression_dict[
                "male_comorbidity_total"]) * 100)  # 抑郁焦虑

            abnormal_8 = round((self.statistics_dict["male_moderate_severe_total"] / self.anxiety_depression_dict[
                "male_comorbidity_total"]) * 100)  # 抑郁焦虑

            abnormal_9 = round((self.statistics_dict["male_severe_severe_total"] / self.anxiety_depression_dict[
                "male_comorbidity_total"]) * 100)  # 抑郁焦虑

            rang_list = [abnormal_1, abnormal_2, abnormal_3, abnormal_4, abnormal_5, abnormal_6, abnormal_7,
                         abnormal_8, abnormal_9]
            # 计算总和
            total_sum = sum(rang_list)
            rang_list = self.difference_total(total_sum, rang_list)

            data_count = [str(self.statistics_dict["male_mild_light_total"]),
                          str(self.statistics_dict["male_moderate_light_total"]),
                          str(self.statistics_dict["male_severe_light_total"]),
                          str(self.statistics_dict["male_mild_moderate_total"]),
                          str(self.statistics_dict["male_moderate_moderate_total"]),
                          str(self.statistics_dict["male_severe_moderate_total"]),
                          str(self.statistics_dict["male_mild_severe_total"]),
                          str(self.statistics_dict["male_moderate_severe_total"]),
                          str(self.statistics_dict["male_severe_severe_total"])]

            if self.pie_chart_statistics:
                self.pie_chart_statistics.ranges = rang_list
                self.pie_chart_statistics.data = [float(x) for x in data_count]
                self.pie_chart_statistics.plot_pie()
            else:
                self.pie_chart_statistics = PieChart_statistics(self, rang_list, data_count)  # 正常  抑郁 焦虑  抑郁焦虑
                self.verticalLayout_15.addWidget(self.pie_chart_statistics)

            comment_4 = f"根据图表可知总检测{self.totle_dict['male_total']}人中，检测共病人数结果为{self.anxiety_depression_dict['male_comorbidity_total']}人。其中:"

            if self.anxiety_depression_dict['male_comorbidity_total'] != 0:
                if self.statistics_dict['male_mild_light_total'] > 0:
                    comment_4 += f"\n检测轻抑轻焦占比共病人数的{rang_list[0]}%，共计{self.statistics_dict['male_mild_light_total']}人。"
                if self.statistics_dict['male_moderate_light_total'] > 0:
                    comment_4 += f"\n检测轻抑中焦占比共病人数的{rang_list[1]}%，共计{self.statistics_dict['male_moderate_light_total']}人。"
                if self.statistics_dict['male_severe_light_total'] > 0:
                    comment_4 += f"\n检测轻抑重焦占比共病人数的{rang_list[2]}%，共计{self.statistics_dict['male_severe_light_total']}人。"
                if self.statistics_dict['male_mild_moderate_total'] > 0:
                    comment_4 += f"\n检测中抑轻焦占比共病人数的{rang_list[3]}%，共计{self.statistics_dict['male_mild_moderate_total']}人。"
                if self.statistics_dict['male_moderate_moderate_total'] > 0:
                    comment_4 += f"\n检测中抑中焦占比共病人数的{rang_list[4]}%，共计{self.statistics_dict['male_moderate_moderate_total']}人。"
                if self.statistics_dict['male_severe_moderate_total'] > 0:
                    comment_4 += f"\n检测中抑重焦占比共病人数的{rang_list[5]}%，共计{self.statistics_dict['male_severe_moderate_total']}人。"
                if self.statistics_dict['male_mild_severe_total'] > 0:
                    comment_4 += f"\n检测重抑轻焦占比共病人数的{rang_list[6]}%，共计{self.statistics_dict['male_mild_severe_total']}人。"
                if self.statistics_dict['male_moderate_severe_total'] > 0:
                    comment_4 += f"\n检测重抑中焦占比共病人数的{rang_list[7]}%，共计{self.statistics_dict['male_moderate_severe_total']}人。"
                if self.statistics_dict['male_severe_severe_total'] > 0:
                    comment_4 += f"\n检测重抑重焦占比共病人数的{rang_list[8]}%，共计{self.statistics_dict['male_severe_severe_total']}人。"
            self.textEdit_3.setText(comment_4)

        if self.totle_dict['male_total'] == 0:
            comment_1 = f"暂无检查人员。"
            self.textEdit_2.setText(comment_1)
            rang_list = [100, 0]
            data_count = ["1", "0"]
            if self.pie_chart_right:
                self.pie_chart_right.type = 0
                self.pie_chart_right.ranges = rang_list
                self.pie_chart_right.data = [float(x) for x in data_count]
                self.pie_chart_right.plot_pie()
            else:
                self.pie_chart_right = PieChart_right(self, rang_list, data_count, 0)  # 正常  抑郁 焦虑  抑郁焦虑
                self.verticalLayout_9.addWidget(self.pie_chart_right)
        else:
            normal = round((self.normal_dict["male_normal_total"] / self.totle_dict['male_total']) * 100)

            abnormal_count = self.totle_dict['male_total'] - self.normal_dict["male_normal_total"]

            mild = round((abnormal_count / self.totle_dict['male_total']) * 100)  # 异常

            # 放入列表并计算总和
            rang_list = [normal, mild]

            total = sum(rang_list)
            rang_list = self.difference_total(total, rang_list)

            data_count = [str(self.normal_dict["male_normal_total"]), str(abnormal_count)]


            if self.pie_chart_right:
                self.pie_chart_right.ranges = rang_list
                self.pie_chart_right.data = [float(x) for x in data_count]
                self.pie_chart_right.plot_pie()
            else:
                self.pie_chart_right = PieChart_right(self, rang_list, data_count)  # 正常  抑郁 焦虑  抑郁焦虑
                self.verticalLayout_9.addWidget(self.pie_chart_right)

            comment_1 = f"根据图表可知总检测{self.totle_dict['total_people']}人中，男生共计{self.totle_dict['male_total']}人。其中:\n检测正常人数占比总人数的{rang_list[0]}%，共计{self.normal_dict['male_normal_total']}人。\n检测异常人数占比总人数的{rang_list[1]}%，共计{abnormal_count}人。"

            self.textEdit_2.setText(comment_1)

        if self.totle_dict['male_total'] == 0:
            comment_2 = f"暂无抑郁人员。"
            self.textEdit_5.setText(comment_2)  # 抑郁数据
            rang_list = [100, 0, 0, 0]
            data_count = ["1", "0", "0", "0"]
            if self.pie_chart:
                self.pie_chart.type = 0
                self.pie_chart.ranges = rang_list
                self.pie_chart.data = [float(x) for x in data_count]
                self.pie_chart.plot_pie()
            else:
                self.pie_chart = PieChart(self, rang_list, data_count, 0)  # 抑郁
                self.verticalLayout_13.addWidget(self.pie_chart)
        else:
            # 抑郁
            depression_normal = self.totle_dict['male_total'] - self.depressed_dict['male_depressed_total']

            normal = round((depression_normal / self.totle_dict['male_total']) * 100)

            mild = round(
                (self.depression_statistics_dict["male_mild_total"] / self.totle_dict['male_total']) * 100)

            moderate = round(
                (self.depression_statistics_dict["male_moderate_total"] / self.totle_dict['male_total']) * 100)

            severe = round(
                (self.depression_statistics_dict["male_severe_total"] / self.totle_dict['male_total']) * 100)

            total = sum([normal, mild, moderate, severe])

            rang_list = self.difference_total(total, [normal, mild, moderate, severe])

            data_count = [str(depression_normal), str(self.depression_statistics_dict["male_mild_total"]),
                          str(self.depression_statistics_dict["male_moderate_total"]),
                          str(self.depression_statistics_dict["male_severe_total"])]
            if self.pie_chart:
                self.pie_chart.ranges = rang_list
                self.pie_chart.data = [float(x) for x in data_count]
                self.pie_chart.plot_pie()
            else:
                self.pie_chart = PieChart(self, rang_list, data_count)  # 抑郁
                self.verticalLayout_13.addWidget(self.pie_chart)

            comment_2 = f"根据图表可知总检测{self.totle_dict['male_total']}人中，正常人数共{depression_normal}人,占比总人数的{rang_list[0]}%,抑郁人数共{self.depressed_dict['male_depressed_total']}人,占比总人数的{100 - rang_list[0]}%，这其中:\n检测为轻度抑郁的共{self.depression_statistics_dict['male_mild_total']}人，占比抑郁总数的{rang_list[0]}%。\n检测为中度抑郁的共{self.depression_statistics_dict['male_moderate_total']}人，占比抑郁总数的{rang_list[1]}%。\n检测为重度抑郁的共{self.depression_statistics_dict['male_severe_total']}人，占比抑郁总数的{rang_list[2]}%。"
            self.textEdit_5.setText(comment_2)  # 抑郁数据

        if self.totle_dict['male_total'] == 0:
            comment_3 = f"暂无焦虑人员。"
            self.textEdit_4.setText(comment_3)  # 焦虑数据
            rang_list = [100, 0, 0, 0]
            data_count = ["1", "0", "0", "0"]
            if self.pie_chart1:
                self.pie_chart1.type = 0
                self.pie_chart1.ranges = rang_list
                self.pie_chart1.data = [float(x) for x in data_count]
                self.pie_chart1.plot_pie()
            else:
                self.pie_chart1 = PieChart(self, rang_list, data_count, 0)  # 抑郁
                self.verticalLayout_11.addWidget(self.pie_chart1)
        else:
            # 焦虑
            anxiety_normal = self.totle_dict['male_total'] - self.anxiety_dict['male_anxiety_total']

            normal = round((anxiety_normal / self.totle_dict['male_total']) * 100)

            mild = round(
                (self.anxiety_statistics_dict["male_mild_total"] / self.totle_dict['male_total']) * 100)

            moderate = round(
                (self.anxiety_statistics_dict["male_moderate_total"] / self.totle_dict['male_total']) * 100)

            severe = round(
                (self.anxiety_statistics_dict["male_severe_total"] / self.totle_dict['male_total']) * 100)

            total = sum([normal, mild, moderate, severe])
            rang_list = self.difference_total(total, [normal, mild, moderate, severe])
            data_count = [str(anxiety_normal), str(self.anxiety_statistics_dict["male_mild_total"]),
                          str(self.anxiety_statistics_dict["male_moderate_total"]),
                          str(self.anxiety_statistics_dict["male_severe_total"])]
            if self.pie_chart1:
                self.pie_chart1.ranges = rang_list
                self.pie_chart1.data = [float(x) for x in data_count]
                self.pie_chart1.plot_pie()
            else:
                self.pie_chart1 = PieChart(self, rang_list, data_count)  # 抑郁

                self.verticalLayout_11.addWidget(self.pie_chart1)

            comment_3 = f"根据图表可知总检测{self.totle_dict['male_total']}人中，正常人数共{anxiety_normal}人,占比总人数的{rang_list[0]}%,焦虑人数共{self.anxiety_dict['male_anxiety_total']}人,占比总人数的{100 - rang_list[0]}%，这其中:\n检测为轻度焦虑的共{self.anxiety_statistics_dict['male_mild_total']}人，占比焦虑总数的{rang_list[0]}%。\n检测为中度焦虑的共{self.anxiety_statistics_dict['male_moderate_total']}人，占比焦虑总数的{rang_list[1]}%。\n检测为重度焦虑的共{self.anxiety_statistics_dict['male_severe_total']}人，占比焦虑总数的{rang_list[2]}%。"
            self.textEdit_4.setText(comment_3)  # 焦虑数据


    def init_data_man_woman(self):
        self.label_4.setText(str(self.totle_dict['total_people']))  # 总人数
        self.label_6.setText(str(self.totle_dict['male_total']))  # 男人数
        self.label_8.setText(str(self.totle_dict['female_total']))  # 女人数

        self.label_16.setText(str(self.normal_dict["normal_total"]))  # 正常
        self.label_19.setText(str(self.normal_dict["male_normal_total"]))  # 男正常
        self.label_21.setText(str(self.normal_dict["female_normal_total"]))  # 女正常

        self.label_24.setText(str(self.depressed_dict["depressed_total"]))  # 抑郁
        self.label_26.setText(str(self.depressed_dict["male_depressed_total"]))  # 男抑郁
        self.label_29.setText(str(self.depressed_dict["female_depressed_total"]))  # 女抑郁

        self.label_10.setText(str(self.anxiety_dict["anxiety_total"]))  # 焦虑
        self.label_12.setText(str(self.anxiety_dict["male_anxiety_total"]))  # 男正常
        self.label_14.setText(str(self.anxiety_dict["female_anxiety_total"]))  # 女正常

        self.label_31.setText(str(self.anxiety_depression_dict["comorbidity_total"]))  # 抑郁焦虑
        self.label_33.setText(str(self.anxiety_depression_dict["male_comorbidity_total"]))  # 男正常
        self.label_35.setText(str(self.anxiety_depression_dict["female_comorbidity_total"]))  # 女正常

        # 共病表没加
        if self.anxiety_depression_dict["comorbidity_total"] == 0:
            comment_4 = f"根据图表可知总检测{self.totle_dict['total_people']}人中，未发现有共病情况存在。"
            self.textEdit_3.setText(comment_4)
            rang_list = [100, 0, 0, 0, 0, 0, 0, 0, 0]
            data_count = ["1", "0", "0", "0", "0", "0", "0", "0", "0"]
            if self.pie_chart_statistics:
                self.pie_chart_statistics.type = 0
                self.pie_chart_statistics.ranges = rang_list
                self.pie_chart_statistics.data = [float(x) for x in data_count]
                self.pie_chart_statistics.plot_pie()
            else:
                self.pie_chart_statistics = PieChart_statistics(self, rang_list, data_count, 0)
                self.verticalLayout_15.addWidget(self.pie_chart_statistics)
        else:
            abnormal_1 = round((self.statistics_dict["mild_light_total"] / self.anxiety_depression_dict[
                "comorbidity_total"]) * 100)  # 抑郁焦虑

            abnormal_2 = round((self.statistics_dict["moderate_light_total"] / self.anxiety_depression_dict[
                "comorbidity_total"]) * 100)  # 抑郁焦虑

            abnormal_3 = round((self.statistics_dict["severe_light_total"] / self.anxiety_depression_dict[
                "comorbidity_total"]) * 100)  # 抑郁焦虑

            abnormal_4 = round((self.statistics_dict["mild_moderate_total"] / self.anxiety_depression_dict[
                "comorbidity_total"]) * 100)  # 抑郁焦虑

            abnormal_5 = round(
                (self.statistics_dict["moderate_moderate_total"] / self.anxiety_depression_dict[
                    "comorbidity_total"]) * 100)  # 抑郁焦虑

            abnormal_6 = round((self.statistics_dict["severe_moderate_total"] / self.anxiety_depression_dict[
                "comorbidity_total"]) * 100)  # 抑郁焦虑

            abnormal_7 = round((self.statistics_dict["mild_severe_total"] / self.anxiety_depression_dict[
                "comorbidity_total"]) * 100)  # 抑郁焦虑

            abnormal_8 = round((self.statistics_dict["moderate_severe_total"] / self.anxiety_depression_dict[
                "comorbidity_total"]) * 100)  # 抑郁焦虑

            abnormal_9 = round((self.statistics_dict["severe_severe_total"] / self.anxiety_depression_dict[
                "comorbidity_total"]) * 100)  # 抑郁焦虑

            rang_list = [abnormal_1, abnormal_2, abnormal_3, abnormal_4, abnormal_5, abnormal_6, abnormal_7,
                         abnormal_8, abnormal_9]
            # 计算总和
            total_sum = sum(rang_list)
            rang_list = self.difference_total(total_sum, rang_list)

            data_count = [str(self.statistics_dict["mild_light_total"]),
                          str(self.statistics_dict["moderate_light_total"]),
                          str(self.statistics_dict["severe_light_total"]),
                          str(self.statistics_dict["mild_moderate_total"]),
                          str(self.statistics_dict["moderate_moderate_total"]),
                          str(self.statistics_dict["severe_moderate_total"]),
                          str(self.statistics_dict["mild_severe_total"]),
                          str(self.statistics_dict["moderate_severe_total"]),
                          str(self.statistics_dict["severe_severe_total"])]

            if self.pie_chart_statistics:
                self.pie_chart_statistics.ranges = rang_list
                self.pie_chart_statistics.data = [float(x) for x in data_count]
                self.pie_chart_statistics.plot_pie()
            else:
                self.pie_chart_statistics = PieChart_statistics(self, rang_list, data_count)  # 正常  抑郁 焦虑  抑郁焦虑
                self.verticalLayout_15.addWidget(self.pie_chart_statistics)

            comment_4 = f"根据图表可知总检测{self.totle_dict['total_people']}人中，检测共病人数结果为{self.anxiety_depression_dict['comorbidity_total']}人。其中:"

            if self.anxiety_depression_dict['comorbidity_total'] != 0:
                if self.statistics_dict['mild_light_total'] > 0:
                    comment_4 += f"\n检测轻抑轻焦占比共病人数的{rang_list[0]}%，共计{self.statistics_dict['mild_light_total']}人。"
                if self.statistics_dict['moderate_light_total'] > 0:
                    comment_4 += f"\n检测轻抑中焦占比共病人数的{rang_list[1]}%，共计{self.statistics_dict['moderate_light_total']}人。"
                if self.statistics_dict['severe_light_total'] > 0:
                    comment_4 += f"\n检测轻抑重焦占比共病人数的{rang_list[2]}%，共计{self.statistics_dict['severe_light_total']}人。"
                if self.statistics_dict['mild_moderate_total'] > 0:
                    comment_4 += f"\n检测中抑轻焦占比共病人数的{rang_list[3]}%，共计{self.statistics_dict['mild_moderate_total']}人。"
                if self.statistics_dict['moderate_moderate_total'] > 0:
                    comment_4 += f"\n检测中抑中焦占比共病人数的{rang_list[4]}%，共计{self.statistics_dict['moderate_moderate_total']}人。"
                if self.statistics_dict['severe_moderate_total'] > 0:
                    comment_4 += f"\n检测中抑重焦占比共病人数的{rang_list[5]}%，共计{self.statistics_dict['severe_moderate_total']}人。"
                if self.statistics_dict['mild_severe_total'] > 0:
                    comment_4 += f"\n检测重抑轻焦占比共病人数的{rang_list[6]}%，共计{self.statistics_dict['mild_severe_total']}人。"
                if self.statistics_dict['moderate_severe_total'] > 0:
                    comment_4 += f"\n检测重抑中焦占比共病人数的{rang_list[7]}%，共计{self.statistics_dict['moderate_severe_total']}人。"
                if self.statistics_dict['severe_severe_total'] > 0:
                    comment_4 += f"\n检测重抑重焦占比共病人数的{rang_list[8]}%，共计{self.statistics_dict['severe_severe_total']}人。"
            self.textEdit_3.setText(comment_4)

        if self.totle_dict['total_people'] == 0:
            comment_1 = f"暂无检查人员。"
            self.textEdit_2.setText(comment_1)
            rang_list = [100, 0]
            data_count = ["1", "0"]
            if self.pie_chart_right:
                self.pie_chart_right.type = 0
                self.pie_chart_right.ranges = rang_list
                self.pie_chart_right.data = [float(x) for x in data_count]
                self.pie_chart_right.plot_pie()
            else:
                self.pie_chart_right = PieChart_right(self, rang_list, data_count, 0)  # 正常  抑郁 焦虑  抑郁焦虑
                self.verticalLayout_9.addWidget(self.pie_chart_right)
        else:
            normal = round((self.normal_dict["normal_total"] / self.totle_dict['total_people']) * 100)

            abnormal_count = self.totle_dict['total_people'] - self.normal_dict["normal_total"]

            mild = round((abnormal_count / self.totle_dict['total_people']) * 100)  # 异常

            # 放入列表并计算总和
            rang_list = [normal, mild]

            total = sum(rang_list)
            rang_list = self.difference_total(total, rang_list)

            data_count = [str(self.normal_dict["normal_total"]), str(abnormal_count)]

            if self.pie_chart_right:
                self.pie_chart_right.ranges = rang_list
                self.pie_chart_right.data = [float(x) for x in data_count]
                self.pie_chart_right.plot_pie()
            else:
                self.pie_chart_right = PieChart_right(self, rang_list, data_count)  # 正常  抑郁 焦虑  抑郁焦虑
                self.verticalLayout_9.addWidget(self.pie_chart_right)

            man = round((self.totle_dict['male_total'] / self.totle_dict['total_people']) * 100)
            woman = round((self.totle_dict['female_total'] / self.totle_dict['total_people']) * 100)
            total = sum([man, woman])
            sex_list = self.difference_total(total, [man, woman])

            comment_1 = f"根据图表可知总检测{self.totle_dict['total_people']}人中，男生占比{sex_list[0]}%共计{self.totle_dict['male_total']}人。女生占比{sex_list[1]}%，共计{self.totle_dict['female_total']}人。其中:\n检测正常人数占比总人数的{rang_list[0]}%，共计{self.normal_dict['normal_total']}人。\n检测异常人数占比总人数的{rang_list[1]}%，共计{abnormal_count}人。"

            self.textEdit_2.setText(comment_1)

        if self.totle_dict['total_people'] == 0:
            comment_2 = f"暂无抑郁人员。"
            self.textEdit_5.setText(comment_2)  # 抑郁数据
            rang_list = [100, 0, 0, 0]
            data_count = ["1", "0", "0", "0"]
            if self.pie_chart:
                self.pie_chart.type = 0
                self.pie_chart.ranges = rang_list
                self.pie_chart.data = [float(x) for x in data_count]
                self.pie_chart.plot_pie()
            else:
                self.pie_chart = PieChart(self, rang_list, data_count, 0)  # 抑郁
                self.verticalLayout_13.addWidget(self.pie_chart)
        else:
            # 抑郁
            depression_normal = self.totle_dict['total_people'] - self.depressed_dict['depressed_total']

            normal = round((depression_normal / self.totle_dict['total_people']) * 100)

            mild = round((self.depression_statistics_dict["mild_total"] / self.totle_dict['total_people']) * 100)

            moderate = round(
                (self.depression_statistics_dict["moderate_total"] / self.totle_dict['total_people']) * 100)

            severe = round(
                (self.depression_statistics_dict["severe_total"] / self.totle_dict['total_people']) * 100)

            total = sum([normal, mild, moderate, severe])

            rang_list = self.difference_total(total, [normal, mild, moderate, severe])

            data_count = [str(depression_normal), str(self.depression_statistics_dict["mild_total"]),
                          str(self.depression_statistics_dict["moderate_total"]),
                          str(self.depression_statistics_dict["severe_total"])]
            if self.pie_chart:
                self.pie_chart.ranges = rang_list
                self.pie_chart.data = [float(x) for x in data_count]
                self.pie_chart.plot_pie()
            else:
                self.pie_chart = PieChart(self, rang_list, data_count)  # 抑郁
                self.verticalLayout_13.addWidget(self.pie_chart)

            comment_2 = f"根据图表可知总检测{self.totle_dict['total_people']}人中，正常人数共{depression_normal}人,占比总人数的{rang_list[0]}%,抑郁人数共{self.depressed_dict['depressed_total']}人,占比总人数的{100 - rang_list[0]}%，这其中:\n检测为轻度抑郁的共{self.depression_statistics_dict['mild_total']}人，占比抑郁总数的{rang_list[0]}%。\n检测为中度抑郁的共{self.depression_statistics_dict['moderate_total']}人，占比抑郁总数的{rang_list[1]}%。\n检测为重度抑郁的共{self.depression_statistics_dict['severe_total']}人，占比抑郁总数的{rang_list[2]}%。"
            self.textEdit_5.setText(comment_2)  # 抑郁数据

        if self.totle_dict['total_people'] == 0:
            comment_3 = f"暂无焦虑人员。"
            self.textEdit_4.setText(comment_3)  # 焦虑数据
            rang_list = [100, 0, 0, 0]
            data_count = ["1", "0", "0", "0"]
            if self.pie_chart1:
                self.pie_chart1.type = 0
                self.pie_chart1.ranges = rang_list
                self.pie_chart1.data = [float(x) for x in data_count]
                self.pie_chart1.plot_pie()
            else:
                self.pie_chart1 = PieChart(self, rang_list, data_count, 0)  # 抑郁
                self.verticalLayout_11.addWidget(self.pie_chart1)
        else:
            # 焦虑
            anxiety_normal = self.totle_dict['total_people'] - self.anxiety_dict['anxiety_total']

            normal = round((anxiety_normal / self.totle_dict['total_people']) * 100)

            mild = round(
                (self.anxiety_statistics_dict["mild_total"] / self.totle_dict['total_people']) * 100)

            moderate = round(
                (self.anxiety_statistics_dict["moderate_total"] / self.totle_dict['total_people']) * 100)

            severe = round(
                (self.anxiety_statistics_dict["severe_total"] / self.totle_dict['total_people']) * 100)

            total = sum([normal, mild, moderate, severe])
            rang_list = self.difference_total(total, [normal, mild, moderate, severe])
            data_count = [str(anxiety_normal), str(self.anxiety_statistics_dict["mild_total"]),
                          str(self.anxiety_statistics_dict["moderate_total"]),
                          str(self.anxiety_statistics_dict["severe_total"])]
            if self.pie_chart1:
                self.pie_chart1.ranges = rang_list
                self.pie_chart1.data = [float(x) for x in data_count]
                self.pie_chart1.plot_pie()
            else:
                self.pie_chart1 = PieChart(self, rang_list, data_count)  # 抑郁
                self.verticalLayout_11.addWidget(self.pie_chart1)

            comment_3 = f"根据图表可知总检测{self.totle_dict['total_people']}人中，正常人数共{anxiety_normal}人,占比总人数的{rang_list[0]}%,焦虑人数共{self.anxiety_dict['anxiety_total']}人,占比总人数的{100 - rang_list[0]}%，这其中:\n检测为轻度焦虑的共{self.anxiety_statistics_dict['mild_total']}人，占比焦虑总数的{rang_list[0]}%。\n检测为中度焦虑的共{self.anxiety_statistics_dict['moderate_total']}人，占比焦虑总数的{rang_list[1]}%。\n检测为重度焦虑的共{self.anxiety_statistics_dict['severe_total']}人，占比焦虑总数的{rang_list[2]}%。"
            self.textEdit_4.setText(comment_3)  # 焦虑数据

    def init_data_woman(self):
        self.label_6.setText("")
        self.label_19.setText("")
        self.label_26.setText("")
        self.label_12.setText("")
        self.label_33.setText("")

        self.label_4.setText(str(self.totle_dict['female_total']))  # 总人数
        self.label_8.setText(str(self.totle_dict['female_total']))  # 女人数

        self.label_16.setText(str(self.normal_dict["female_normal_total"]))  # 正常
        self.label_21.setText(str(self.normal_dict["female_normal_total"]))  # 女正常

        self.label_24.setText(str(self.depressed_dict["female_depressed_total"]))  # 抑郁
        self.label_29.setText(str(self.depressed_dict["female_depressed_total"]))  # 女抑郁

        self.label_10.setText(str(self.anxiety_dict["female_anxiety_total"]))  # 焦虑
        self.label_14.setText(str(self.anxiety_dict["female_anxiety_total"]))  # 女正常

        self.label_31.setText(str(self.anxiety_depression_dict["female_comorbidity_total"]))  # 抑郁焦虑
        self.label_35.setText(str(self.anxiety_depression_dict["female_comorbidity_total"]))  # 女抑郁焦虑
        # 共病表没加
        if self.anxiety_depression_dict["female_comorbidity_total"] == 0:
            comment_4 = f"根据图表可知总检测{self.totle_dict['female_total']}人中，未发现有共病情况存在。"
            self.textEdit_3.setText(comment_4)
            rang_list = [100, 0, 0, 0, 0, 0, 0, 0, 0]
            data_count = ["1", "0", "0", "0", "0", "0", "0", "0", "0"]
            if self.pie_chart_statistics:
                self.pie_chart_statistics.type=0
                self.pie_chart_statistics.ranges = rang_list
                self.pie_chart_statistics.data = [float(x) for x in data_count]
                self.pie_chart_statistics.plot_pie()
            else:
                self.pie_chart_statistics = PieChart_statistics(self, rang_list, data_count, 0)
                self.verticalLayout_15.addWidget(self.pie_chart_statistics)
        else:
            abnormal_1 = round((self.statistics_dict["female_mild_light_total"] / self.anxiety_depression_dict[
                "female_comorbidity_total"]) * 100)  # 抑郁焦虑

            abnormal_2 = round((self.statistics_dict["female_moderate_light_total"] / self.anxiety_depression_dict[
                "female_comorbidity_total"]) * 100)  # 抑郁焦虑

            abnormal_3 = round((self.statistics_dict["female_severe_light_total"] / self.anxiety_depression_dict[
                "female_comorbidity_total"]) * 100)  # 抑郁焦虑

            abnormal_4 = round((self.statistics_dict["female_mild_moderate_total"] / self.anxiety_depression_dict[
                "female_comorbidity_total"]) * 100)  # 抑郁焦虑

            abnormal_5 = round((self.statistics_dict["female_moderate_moderate_total"] / self.anxiety_depression_dict[
                "female_comorbidity_total"]) * 100)  # 抑郁焦虑

            abnormal_6 = round((self.statistics_dict["female_severe_moderate_total"] / self.anxiety_depression_dict[
                "female_comorbidity_total"]) * 100)  # 抑郁焦虑

            abnormal_7 = round((self.statistics_dict["female_mild_severe_total"] / self.anxiety_depression_dict[
                "female_comorbidity_total"]) * 100)  # 抑郁焦虑

            abnormal_8 = round((self.statistics_dict["female_moderate_severe_total"] / self.anxiety_depression_dict[
                "female_comorbidity_total"]) * 100)  # 抑郁焦虑

            abnormal_9 = round((self.statistics_dict["female_severe_severe_total"] / self.anxiety_depression_dict[
                "female_comorbidity_total"]) * 100)  # 抑郁焦虑

            rang_list = [abnormal_1, abnormal_2, abnormal_3, abnormal_4, abnormal_5, abnormal_6, abnormal_7,
                         abnormal_8, abnormal_9]
            # 计算总和
            total_sum = sum(rang_list)
            rang_list = self.difference_total(total_sum, rang_list)

            data_count = [str(self.statistics_dict["female_mild_light_total"]),
                          str(self.statistics_dict["female_moderate_light_total"]),
                          str(self.statistics_dict["female_severe_light_total"]),
                          str(self.statistics_dict["female_mild_moderate_total"]),
                          str(self.statistics_dict["female_moderate_moderate_total"]),
                          str(self.statistics_dict["female_severe_moderate_total"]),
                          str(self.statistics_dict["female_mild_severe_total"]),
                          str(self.statistics_dict["female_moderate_severe_total"]),
                          str(self.statistics_dict["female_severe_severe_total"])]

            if self.pie_chart_statistics:
                self.pie_chart_statistics.ranges = rang_list
                self.pie_chart_statistics.data = [float(x) for x in data_count]
                self.pie_chart_statistics.plot_pie()
            else:
                self.pie_chart_statistics = PieChart_statistics(self, rang_list, data_count)  # 正常  抑郁 焦虑  抑郁焦虑
                self.verticalLayout_15.addWidget(self.pie_chart_statistics)

            comment_4 = f"根据图表可知总检测{self.totle_dict['female_total']}人中，检测共病人数结果为{self.anxiety_depression_dict['female_comorbidity_total']}人。其中:"

            if self.anxiety_depression_dict['female_comorbidity_total'] != 0:
                if self.statistics_dict['female_mild_light_total'] > 0:
                    comment_4 += f"\n检测轻抑轻焦占比共病人数的{rang_list[0]}%，共计{self.statistics_dict['female_mild_light_total']}人。"
                if self.statistics_dict['female_moderate_light_total'] > 0:
                    comment_4 += f"\n检测轻抑中焦占比共病人数的{rang_list[1]}%，共计{self.statistics_dict['female_moderate_light_total']}人。"
                if self.statistics_dict['female_severe_light_total'] > 0:
                    comment_4 += f"\n检测轻抑重焦占比共病人数的{rang_list[2]}%，共计{self.statistics_dict['female_severe_light_total']}人。"
                if self.statistics_dict['female_mild_moderate_total'] > 0:
                    comment_4 += f"\n检测中抑轻焦占比共病人数的{rang_list[3]}%，共计{self.statistics_dict['female_mild_moderate_total']}人。"
                if self.statistics_dict['female_moderate_moderate_total'] > 0:
                    comment_4 += f"\n检测中抑中焦占比共病人数的{rang_list[4]}%，共计{self.statistics_dict['female_moderate_moderate_total']}人。"
                if self.statistics_dict['female_severe_moderate_total'] > 0:
                    comment_4 += f"\n检测中抑重焦占比共病人数的{rang_list[5]}%，共计{self.statistics_dict['female_severe_moderate_total']}人。"
                if self.statistics_dict['female_mild_severe_total'] > 0:
                    comment_4 += f"\n检测重抑轻焦占比共病人数的{rang_list[6]}%，共计{self.statistics_dict['female_mild_severe_total']}人。"
                if self.statistics_dict['female_moderate_severe_total'] > 0:
                    comment_4 += f"\n检测重抑中焦占比共病人数的{rang_list[7]}%，共计{self.statistics_dict['female_moderate_severe_total']}人。"
                if self.statistics_dict['female_severe_severe_total'] > 0:
                    comment_4 += f"\n检测重抑重焦占比共病人数的{rang_list[8]}%，共计{self.statistics_dict['female_severe_severe_total']}人。"
            self.textEdit_3.setText(comment_4)

        if self.totle_dict['female_total'] == 0:
            comment_1 = f"暂无检查人员。"
            self.textEdit_2.setText(comment_1)
            rang_list = [100, 0]
            data_count = ["1", "0"]
            if self.pie_chart_right:
                self.pie_chart_right.type=0
                self.pie_chart_right.ranges = rang_list
                self.pie_chart_right.data = [float(x) for x in data_count]
                self.pie_chart_right.plot_pie()
            else:
                self.pie_chart_right = PieChart_right(self, rang_list, data_count,0)  # 正常  抑郁 焦虑  抑郁焦虑
                self.verticalLayout_9.addWidget(self.pie_chart_right)
        else:

            normal = round((self.normal_dict["female_normal_total"] / self.totle_dict['female_total']) * 100)

            abnormal_count = self.totle_dict['female_total'] - self.normal_dict["female_normal_total"]

            mild = round((abnormal_count / self.totle_dict['female_total']) * 100)  # 异常

            # 放入列表并计算总和
            rang_list = [normal, mild]

            total = sum(rang_list)
            rang_list = self.difference_total(total, rang_list)

            data_count = [str(self.normal_dict["female_normal_total"]), str(abnormal_count)]

            if self.pie_chart_right:
                self.pie_chart_right.ranges = rang_list
                self.pie_chart_right.data = [float(x) for x in data_count]
                self.pie_chart_right.plot_pie()
            else:
                self.pie_chart_right = PieChart_right(self, rang_list, data_count)  # 正常  抑郁 焦虑  抑郁焦虑
                self.verticalLayout_9.addWidget(self.pie_chart_right)

            comment_1 = f"根据图表可知总检测{self.totle_dict['total_people']}人中，女生共计{self.totle_dict['female_total']}人。其中:\n检测正常人数占比总人数的{rang_list[0]}%，共计{self.normal_dict['female_normal_total']}人。\n检测异常人数占比总人数的{rang_list[1]}%，共计{abnormal_count}人。"

            self.textEdit_2.setText(comment_1)

        if self.totle_dict['female_total'] == 0:
            comment_2 = f"暂无抑郁人员。"
            self.textEdit_5.setText(comment_2)  # 抑郁数据
            rang_list = [100, 0,0,0]
            data_count = ["1", "0", "0", "0"]
            if self.pie_chart:
                self.pie_chart.type=0
                self.pie_chart.ranges = rang_list
                self.pie_chart.data = [float(x) for x in data_count]
                self.pie_chart.plot_pie()
            else:
                self.pie_chart = PieChart(self, rang_list, data_count,0)  # 抑郁
                self.verticalLayout_13.addWidget(self.pie_chart)
        else:
            #抑郁
            depression_normal = self.totle_dict['female_total'] - self.depressed_dict['female_depressed_total']

            normal = round((depression_normal / self.totle_dict['female_total']) * 100)

            mild = round((self.depression_statistics_dict["female_mild_total"] / self.totle_dict['female_total']) * 100)

            moderate = round(
                (self.depression_statistics_dict["female_moderate_total"] / self.totle_dict['female_total']) * 100)

            severe = round(
                (self.depression_statistics_dict["female_severe_total"] / self.totle_dict['female_total']) * 100)

            total = sum([normal, mild, moderate, severe])

            rang_list = self.difference_total(total, [normal, mild, moderate, severe])

            data_count = [str(depression_normal), str(self.depression_statistics_dict["female_mild_total"]),
                          str(self.depression_statistics_dict["female_moderate_total"]),
                          str(self.depression_statistics_dict["female_severe_total"])]
            if self.pie_chart:
                self.pie_chart.ranges = rang_list
                self.pie_chart.data = [float(x) for x in data_count]
                self.pie_chart.plot_pie()
            else:
                self.pie_chart = PieChart(self, rang_list, data_count)  # 抑郁
                self.verticalLayout_13.addWidget(self.pie_chart)

            comment_2 = f"根据图表可知总检测{self.totle_dict['female_total']}人中，正常人数共{depression_normal}人,占比总人数的{rang_list[0]}%,抑郁人数共{self.depressed_dict['female_depressed_total']}人,占比总人数的{100 - rang_list[0]}%，这其中:\n检测为轻度抑郁的共{self.depression_statistics_dict['female_mild_total']}人，占比抑郁总数的{rang_list[0]}%。\n检测为中度抑郁的共{self.depression_statistics_dict['female_moderate_total']}人，占比抑郁总数的{rang_list[1]}%。\n检测为重度抑郁的共{self.depression_statistics_dict['female_severe_total']}人，占比抑郁总数的{rang_list[2]}%。"
            self.textEdit_5.setText(comment_2)  # 抑郁数据

        if self.totle_dict['female_total'] == 0:
            comment_3 = f"暂无焦虑人员。"
            self.textEdit_4.setText(comment_3)  # 焦虑数据
            rang_list = [100, 0,0,0]
            data_count = ["1", "0", "0", "0"]
            if self.pie_chart1:
                self.pie_chart1.type=0
                self.pie_chart1.ranges = rang_list
                self.pie_chart1.data = [float(x) for x in data_count]
                self.pie_chart1.plot_pie()
            else:
                self.pie_chart1 = PieChart(self, rang_list, data_count,0)  # 抑郁
                self.verticalLayout_11.addWidget(self.pie_chart1)
        else:
            # 焦虑
            anxiety_normal = self.totle_dict['female_total'] - self.anxiety_dict['female_anxiety_total']

            normal = round((anxiety_normal / self.totle_dict['female_total']) * 100)

            mild = round(
                (self.anxiety_statistics_dict["female_mild_total"] / self.totle_dict['female_total']) * 100)

            moderate = round(
                (self.anxiety_statistics_dict["female_moderate_total"] / self.totle_dict['female_total']) * 100)

            severe = round(
                (self.anxiety_statistics_dict["female_severe_total"] / self.totle_dict['female_total']) * 100)

            total = sum([normal, mild, moderate, severe])
            rang_list = self.difference_total(total, [normal, mild, moderate, severe])
            data_count = [str(anxiety_normal), str(self.anxiety_statistics_dict["female_mild_total"]),
                          str(self.anxiety_statistics_dict["female_moderate_total"]),
                          str(self.anxiety_statistics_dict["female_severe_total"])]
            if self.pie_chart1:
                self.pie_chart1.ranges = rang_list
                self.pie_chart1.data = [float(x) for x in data_count]
                self.pie_chart1.plot_pie()
            else:
                self.pie_chart1 = PieChart(self, rang_list, data_count)  # 抑郁

                self.verticalLayout_11.addWidget(self.pie_chart1)

            comment_3 = f"根据图表可知总检测{self.totle_dict['female_total']}人中，正常人数共{anxiety_normal}人,占比总人数的{rang_list[0]}%,焦虑人数共{self.anxiety_dict['female_anxiety_total']}人,占比总人数的{100 - rang_list[0]}%，这其中:\n检测为轻度焦虑的共{self.anxiety_statistics_dict['female_mild_total']}人，占比焦虑总数的{rang_list[0]}%。\n检测为中度焦虑的共{self.anxiety_statistics_dict['female_moderate_total']}人，占比焦虑总数的{rang_list[1]}%。\n检测为重度焦虑的共{self.anxiety_statistics_dict['female_severe_total']}人，占比焦虑总数的{rang_list[2]}%。"
            self.textEdit_4.setText(comment_3)  # 焦虑数据
        # else:
        #
        #     self.textEdit_2.setText("")
        #     self.textEdit_5.setText("")
        #     self.textEdit_4.setText("")
        #     self.textEdit_3.setText("")
        #     if self.pie_chart_statistics:
        #         self.pie_chart_statistics.clear_and_clean()
        #     if self.pie_chart_right:
        #         self.pie_chart_right.clear_and_clean()
        #     if self.pie_chart1:
        #         self.pie_chart1.clear_and_clean()
        #     if self.pie_chart:
        #         self.pie_chart.clear_and_clean()

    def init_data(self):
        school = self.comboBox_12.currentText()
        if school == "请选择":
            school = ""
        grade = self.comboBox_10.currentText()
        if grade == "请选择":
            grade = ""
        Class = self.comboBox_11.currentText()
        if Class == "请选择":
            Class = ""

        res,self.totle_dict=self.api.totle_check_people(school=school, grade=grade,Class=Class)

        res,self.normal_dict=self.api.is_normal_people(school=school, grade=grade,Class=Class)

        res,self.depressed_dict=self.api.is_depressed_people(school=school, grade=grade,Class=Class)

        res,self.anxiety_dict=self.api.is_anxiety_people(school=school, grade=grade,Class=Class)

        res,self.anxiety_depression_dict=self.api.is_anxiety_depression_comorbidity_people(school=school, grade=grade,Class=Class)

        res,self.depression_statistics_dict=self.api.is_depression_statistics(school=school, grade=grade,Class=Class)

        res,self.anxiety_statistics_dict=self.api.is_anxiety_statistics(school=school, grade=grade,Class=Class)

        res,self.statistics_dict=self.api.is_anxiety_depression_statistics(school=school, grade=grade,Class=Class)

        self.label_4.setText(str(self.totle_dict['total_people']))  # 总人数
        self.label_6.setText(str(self.totle_dict['male_total']))  # 男人数
        self.label_8.setText(str(self.totle_dict['female_total']))  # 女人数

        self.label_16.setText(str(self.normal_dict["normal_total"]))  # 正常
        self.label_19.setText(str(self.normal_dict["male_normal_total"]))  # 男正常
        self.label_21.setText(str(self.normal_dict["female_normal_total"]))  # 女正常


        self.label_24.setText(str(self.depressed_dict["depressed_total"]))  # 抑郁
        self.label_26.setText(str(self.depressed_dict["male_depressed_total"]))  # 男抑郁
        self.label_29.setText(str(self.depressed_dict["female_depressed_total"]))  # 女抑郁

        self.label_10.setText(str(self.anxiety_dict["anxiety_total"]))  # 焦虑
        self.label_12.setText(str(self.anxiety_dict["male_anxiety_total"]))  # 男正常
        self.label_14.setText(str(self.anxiety_dict["female_anxiety_total"]))  # 女正常

        self.label_31.setText(str(self.anxiety_depression_dict["comorbidity_total"]))  # 抑郁焦虑
        self.label_33.setText(str(self.anxiety_depression_dict["male_comorbidity_total"]))  # 男正常
        self.label_35.setText(str(self.anxiety_depression_dict["female_comorbidity_total"]))  # 女正常

        #共病表没加
        if self.anxiety_depression_dict["comorbidity_total"] == 0:
            comment_4 = f"根据图表可知总检测{self.totle_dict['total_people']}人中，未发现有共病情况存在。"
            self.textEdit_3.setText(comment_4)
            rang_list = [100,0,0,0,0,0,0,0,0]
            data_count = ["1","0","0","0","0","0","0","0","0"]
            self.pie_chart_statistics = PieChart_statistics(self, rang_list, data_count,0)
            self.verticalLayout_15.addWidget(self.pie_chart_statistics)

        else:
            abnormal_1 = round((self.statistics_dict["mild_light_total"] / self.anxiety_depression_dict["comorbidity_total"]) * 100)  # 抑郁焦虑

            abnormal_2 = round((self.statistics_dict["moderate_light_total"] / self.anxiety_depression_dict["comorbidity_total"]) * 100)  # 抑郁焦虑

            abnormal_3 = round((self.statistics_dict["severe_light_total"] / self.anxiety_depression_dict["comorbidity_total"]) * 100)  # 抑郁焦虑

            abnormal_4 = round((self.statistics_dict["mild_moderate_total"] / self.anxiety_depression_dict["comorbidity_total"]) * 100)  # 抑郁焦虑

            abnormal_5 = round((self.statistics_dict["moderate_moderate_total"] / self.anxiety_depression_dict["comorbidity_total"]) * 100)  # 抑郁焦虑

            abnormal_6 = round((self.statistics_dict["severe_moderate_total"] / self.anxiety_depression_dict["comorbidity_total"]) * 100)  # 抑郁焦虑

            abnormal_7 = round((self.statistics_dict["mild_severe_total"] / self.anxiety_depression_dict["comorbidity_total"]) * 100)  # 抑郁焦虑

            abnormal_8 = round((self.statistics_dict["moderate_severe_total"] / self.anxiety_depression_dict["comorbidity_total"]) * 100)  # 抑郁焦虑

            abnormal_9 = round((self.statistics_dict["severe_severe_total"] / self.anxiety_depression_dict["comorbidity_total"]) * 100)  # 抑郁焦虑

            rang_list = [abnormal_1, abnormal_2, abnormal_3, abnormal_4,abnormal_5,abnormal_6,abnormal_7,abnormal_8,abnormal_9]
            # 计算总和
            total_sum = sum(rang_list)
            rang_list=self.difference_total(total_sum,rang_list)

            data_count = [str(self.statistics_dict["mild_light_total"]),
                          str(self.statistics_dict["moderate_light_total"]),
                          str(self.statistics_dict["severe_light_total"]),
                          str(self.statistics_dict["mild_moderate_total"]),
                          str(self.statistics_dict["moderate_moderate_total"]),
                          str(self.statistics_dict["severe_moderate_total"]),
                          str(self.statistics_dict["mild_severe_total"]),
                          str(self.statistics_dict["moderate_severe_total"]),
                          str(self.statistics_dict["severe_severe_total"])]

            self.pie_chart_statistics = PieChart_statistics(self, rang_list, data_count)  # 正常  抑郁 焦虑  抑郁焦虑
            self.verticalLayout_15.addWidget(self.pie_chart_statistics)

            comment_4 = f"根据图表可知总检测{self.totle_dict['total_people']}人中，检测共病人数结果为{self.anxiety_depression_dict['comorbidity_total']}人。其中:"

            if self.anxiety_depression_dict['comorbidity_total'] != 0:
                if self.statistics_dict['mild_light_total'] > 0:
                    comment_4 += f"\n检测轻抑轻焦占比共病人数的{rang_list[0]}%，共计{self.statistics_dict['mild_light_total']}人。"
                if self.statistics_dict['moderate_light_total'] > 0:
                    comment_4 += f"\n检测轻抑中焦占比共病人数的{rang_list[1]}%，共计{self.statistics_dict['moderate_light_total']}人。"
                if self.statistics_dict['severe_light_total'] > 0:
                    comment_4 += f"\n检测轻抑重焦占比共病人数的{rang_list[2]}%，共计{self.statistics_dict['severe_light_total']}人。"
                if self.statistics_dict['mild_moderate_total'] > 0:
                    comment_4 += f"\n检测中抑轻焦占比共病人数的{rang_list[3]}%，共计{self.statistics_dict['mild_moderate_total']}人。"
                if self.statistics_dict['moderate_moderate_total'] > 0:
                    comment_4 += f"\n检测中抑中焦占比共病人数的{rang_list[4]}%，共计{self.statistics_dict['moderate_moderate_total']}人。"
                if self.statistics_dict['severe_moderate_total'] > 0:
                    comment_4 += f"\n检测中抑重焦占比共病人数的{rang_list[5]}%，共计{self.statistics_dict['severe_moderate_total']}人。"
                if self.statistics_dict['mild_severe_total'] > 0:
                    comment_4 += f"\n检测重抑轻焦占比共病人数的{rang_list[6]}%，共计{self.statistics_dict['mild_severe_total']}人。"
                if self.statistics_dict['moderate_severe_total'] > 0:
                    comment_4 += f"\n检测重抑中焦占比共病人数的{rang_list[7]}%，共计{self.statistics_dict['moderate_severe_total']}人。"
                if self.statistics_dict['severe_severe_total'] > 0:
                    comment_4 += f"\n检测重抑重焦占比共病人数的{rang_list[8]}%，共计{self.statistics_dict['severe_severe_total']}人。"
            self.textEdit_3.setText(comment_4)

        if self.totle_dict['total_people']==0:
            rang_list = [100, 0]
            data_count = ["1", "0"]
            self.pie_chart_right = PieChart_right(self, rang_list, data_count,0)  # 正常  抑郁 焦虑  抑郁焦虑
            self.verticalLayout_9.addWidget(self.pie_chart_right)
            comment_1 = f"暂无检查人员。"
            self.textEdit_2.setText(comment_1)
        else:
            normal = round((self.normal_dict["normal_total"] / self.totle_dict['total_people']) * 100)

            abnormal_count=self.totle_dict['total_people']-self.normal_dict["normal_total"]
            mild = round((abnormal_count / self.totle_dict['total_people']) * 100)  #异常

            # 放入列表并计算总和
            rang_list = [normal, mild]

            total = sum(rang_list)
            rang_list = self.difference_total(total,rang_list)

            data_count = [str(self.normal_dict["normal_total"]), str(abnormal_count)]

            self.pie_chart_right = PieChart_right(self, rang_list, data_count)  # 正常  抑郁 焦虑  抑郁焦虑
            self.verticalLayout_9.addWidget(self.pie_chart_right)

            man = round((self.totle_dict['male_total'] / self.totle_dict['total_people']) * 100)
            woman=round((self.totle_dict['female_total'] / self.totle_dict['total_people']) * 100)
            total = sum([man,woman])
            sex_list=self.difference_total(total,[man,woman])

            comment_1 = f"根据图表可知总检测{self.totle_dict['total_people']}人中，男生占比{sex_list[0]}%共计{self.totle_dict['male_total']}人。女生占比{sex_list[1]}%，共计{self.totle_dict['female_total']}人。其中:\n检测正常人数占比总人数的{rang_list[0]}%，共计{self.normal_dict['normal_total']}人。\n检测异常人数占比总人数的{rang_list[1]}%，共计{abnormal_count}人。"
            self.textEdit_2.setText(comment_1)

        if self.totle_dict['total_people']==0:
            rang_list = [100, 0, 0, 0]
            data_count = ["1", "0", "0", "0"]
            self.pie_chart = PieChart(self, rang_list, data_count,0)  # 抑郁
            self.verticalLayout_13.addWidget(self.pie_chart)

            comment_2 = "暂无抑郁人员。"
            self.textEdit_5.setText(comment_2)  # 抑郁数据
        else:
            # 抑郁
            depression_normal = self.totle_dict['total_people'] - self.depressed_dict['depressed_total']

            normal = round((depression_normal / self.totle_dict['total_people']) * 100)

            mild = round((self.depression_statistics_dict["mild_total"] / self.totle_dict['total_people']) * 100)

            moderate = round(
                (self.depression_statistics_dict["moderate_total"] / self.totle_dict['total_people']) * 100)

            severe = round(
                (self.depression_statistics_dict["severe_total"] / self.totle_dict['total_people']) * 100)

            total = sum([normal, mild, moderate, severe])

            rang_list = self.difference_total(total, [normal, mild, moderate, severe])

            data_count = [str(depression_normal), str(self.depression_statistics_dict["mild_total"]),
                          str(self.depression_statistics_dict["moderate_total"]),
                          str(self.depression_statistics_dict["severe_total"])]
            self.pie_chart = PieChart(self, rang_list, data_count)  # 抑郁
            self.verticalLayout_13.addWidget(self.pie_chart)

            comment_2 = f"根据图表可知总检测{self.totle_dict['total_people']}人中，正常人数共{depression_normal}人,占比总人数的{rang_list[0]}%,抑郁人数共{self.depressed_dict['depressed_total']}人,占比总人数的{100 - rang_list[0]}%，这其中:\n检测为轻度抑郁的共{self.depression_statistics_dict['mild_total']}人，占比抑郁总数的{rang_list[0]}%。\n检测为中度抑郁的共{self.depression_statistics_dict['moderate_total']}人，占比抑郁总数的{rang_list[1]}%。\n检测为重度抑郁的共{self.depression_statistics_dict['severe_total']}人，占比抑郁总数的{rang_list[2]}%。"
            self.textEdit_5.setText(comment_2)  # 抑郁数据

        if self.totle_dict['total_people'] == 0:
            rang_list = [100, 0,0,0]
            data_count = ["1", "0", "0", "0"]
            self.pie_chart1 = PieChart(self, rang_list, data_count,0)  # 抑郁
            self.verticalLayout_11.addWidget(self.pie_chart1)
            comment_3 = f"暂无焦虑人员。"
            self.textEdit_4.setText(comment_3)  # 焦虑数据
        # 焦虑
        else:
            anxiety_normal = self.totle_dict['total_people'] - self.anxiety_dict['anxiety_total']

            normal = round((anxiety_normal / self.totle_dict['total_people']) * 100)

            mild = round(
                (self.anxiety_statistics_dict["mild_total"] / self.totle_dict['total_people']) * 100)

            moderate = round(
                (self.anxiety_statistics_dict["moderate_total"] / self.totle_dict['total_people']) * 100)

            severe = round(
                (self.anxiety_statistics_dict["severe_total"] / self.totle_dict['total_people']) * 100)

            total = sum([normal, mild, moderate, severe])
            rang_list = self.difference_total(total, [normal, mild, moderate, severe])
            data_count = [str(anxiety_normal), str(self.anxiety_statistics_dict["mild_total"]),
                          str(self.anxiety_statistics_dict["moderate_total"]),
                          str(self.anxiety_statistics_dict["severe_total"])]
            self.pie_chart1 = PieChart(self, rang_list, data_count)  # 抑郁

            self.verticalLayout_11.addWidget(self.pie_chart1)

            comment_3 = f"根据图表可知总检测{self.totle_dict['total_people']}人中，正常人数共{anxiety_normal}人,占比总人数的{rang_list[0]}%,焦虑人数共{self.anxiety_dict['anxiety_total']}人,占比总人数的{100 - rang_list[0]}%，这其中:\n检测为轻度焦虑的共{self.anxiety_statistics_dict['mild_total']}人，占比焦虑总数的{rang_list[1]}%。\n检测为中度焦虑的共{self.anxiety_statistics_dict['moderate_total']}人，占比焦虑总数的{rang_list[2]}%。\n检测为重度焦虑的共{self.anxiety_statistics_dict['severe_total']}人，占比焦虑总数的{rang_list[3]}%。"
            self.textEdit_4.setText(comment_3)  # 焦虑数据


    def difference_total(self,total,rang_list):
        if total != 100:
            # 计算调整的差值
            difference = 100 - total

            # 过滤出非零的元素的索引
            non_zero_indices = [i for i, value in enumerate(rang_list) if value != 0]

            # 如果有非零元素，则随机选择一个索引进行调整
            if non_zero_indices:
                random_index = random.choice(non_zero_indices)
                rang_list[random_index] += difference

        return rang_list
