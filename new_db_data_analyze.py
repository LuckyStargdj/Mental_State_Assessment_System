import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QCursor, QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListView

from gui.untitled import Ui_data_
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.patches as patches

from utils.utils import wait_noblock


class PieChart_left(FigureCanvas):
    def __init__(self, parent=None, rang_list=None, data_count=None):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111, aspect='equal')
        super(PieChart_left, self).__init__(self.fig)
        self.setParent(parent)

        self.ranges = rang_list  # 每个区间的范围百分比
        self.data = [float(x) for x in data_count]  # 确保数据为数字类型
        self.colors = ['green','red']
        self.legend_labels = ["正常", "异常"]  # 图例文字
        self.plot_pie()

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

            distance_multiplier = 1.40  # 调整基础距离倍数
            dx = distance_multiplier * x
            dy = distance_multiplier * y

            # 防止标签重叠
            for ann_x, ann_y in annotation_positions:
                while np.hypot(dx - ann_x, dy - ann_y) < 0.5:  # 增加最小距离
                    dx += 0.05 * np.sign(dx - ann_x)
                    dy += 0.05 * np.sign(dy - ann_y)

            # 防止超出视角
            dx = np.clip(dx, -1.5, 1.5)
            dy = np.clip(dy, -1.5, 1.5)

            xytext = (dx, dy)
            bbox_props = dict(boxstyle="round,pad=0.3", edgecolor="none", facecolor=self.colors[i], alpha=0.5)

            # 调整箭头指向
            # 调整箭头指向
            self.ax.annotate(f'{self.ranges[i]}%',
                             xy=(x, y),
                             xytext=xytext,
                             arrowprops=dict(arrowstyle="-", connectionstyle="arc3", color='black'),
                             horizontalalignment='center',
                             verticalalignment='center',
                             bbox=bbox_props,
                             fontproperties='Microsoft YaHei', fontsize=12)
            annotation_positions.append((dx, dy))

        # 添加图例
        # 调整饼图的位置
        self.ax.set_position([0.2, 0.07, 0.70, 0.80])  # 调整饼图以腾出空间给图例

        legend_handles = [patches.Patch(color=color, label=label) for color, label in
                          zip(self.colors, self.legend_labels)]

        # 在图例上方添加文本
        self.ax.text(
            -0.8, 0.8,  # 文本的位置，(x, y) 坐标与 bbox_to_anchor 相关
            "正常/异常统计图",  # 你要添加的文字内容
            transform=self.ax.transAxes,  # 使用轴坐标系
            fontsize=14,  # 字体大小
            verticalalignment='bottom',  # 垂直对齐方式
            horizontalalignment='center'  # 水平对齐方式
        )

        self.ax.legend(
            handles=legend_handles,
            loc='center left',  # 将图例放置在左边中部
            bbox_to_anchor=(-1.2, 0.5),  # 调整图例的位置
            ncol=1,  # 每行显示1个条目，这样垂直显示
            fontsize=14,  # 增大图例中文字的字体大小
            handletextpad=0.5,  # 缩短图例标签和图例标记之间的距离
            columnspacing=1.0,  # 缩短图例列之间的距离
        )

        self.draw()  # 重新绘制图形


class PieChart_right(FigureCanvas):
    def __init__(self, parent=None, rang_list=None, data_count=None):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111, aspect='equal')
        super(PieChart_right, self).__init__(self.fig)
        self.setParent(parent)

        #self.labels = ['', '', '', '']  # 去掉扇形上的文字
        self.ranges = rang_list  # 每个区间的范围百分比
        self.data = [float(x) for x in data_count]  # 确保数据为数字类型
        self.colors = ['green', (0.6, 1, 0.6), 'orange', 'red']
        self.legend_labels = ["正常", "抑郁", "焦虑", "抑郁焦虑"]  # 图例文字
        self.plot_pie()

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

            distance_multiplier = 1.40  # 调整基础距离倍数
            dx = distance_multiplier * x
            dy = distance_multiplier * y

            # 防止标签重叠
            for ann_x, ann_y in annotation_positions:
                while np.hypot(dx - ann_x, dy - ann_y) < 0.5:  # 增加最小距离
                    dx += 0.05 * np.sign(dx - ann_x)
                    dy += 0.05 * np.sign(dy - ann_y)

            # 防止超出视角
            dx = np.clip(dx, -1.5, 1.5)
            dy = np.clip(dy, -1.5, 1.5)

            xytext = (dx, dy)
            bbox_props = dict(boxstyle="round,pad=0.3", edgecolor="none", facecolor=self.colors[i], alpha=0.5)

            # 调整箭头指向
            # 调整箭头指向
            self.ax.annotate(f'{self.ranges[i]}%',
                             xy=(x, y),
                             xytext=xytext,
                             arrowprops=dict(arrowstyle="-", connectionstyle="arc3", color='black'),
                             horizontalalignment='center',
                             verticalalignment='center',
                             bbox=bbox_props,
                             fontproperties='Microsoft YaHei', fontsize=12)
            annotation_positions.append((dx, dy))

        # 添加图例
        # 调整饼图的位置
        self.ax.set_position([0.2, 0.07, 0.70, 0.80])  # 调整饼图以腾出空间给图例

        legend_handles = [patches.Patch(color=color, label=label) for color, label in
                          zip(self.colors, self.legend_labels)]
        # 在图例上方添加文本
        self.ax.text(
            -0.8, 0.8,  # 文本的位置，(x, y) 坐标与 bbox_to_anchor 相关
            "抑郁/焦虑统计图",  # 你要添加的文字内容
            transform=self.ax.transAxes,  # 使用轴坐标系
            fontsize=14,  # 字体大小
            verticalalignment='bottom',  # 垂直对齐方式
            horizontalalignment='center'  # 水平对齐方式
        )

        self.ax.legend(
            handles=legend_handles,
            loc='center left',  # 将图例放置在左边中部
            bbox_to_anchor=(-1.2, 0.4),  # 调整图例的位置
            ncol=1,  # 每行显示1个条目，这样垂直显示
            fontsize=14,  # 增大图例中文字的字体大小
            handletextpad=0.5,  # 缩短图例标签和图例标记之间的距离
            columnspacing=1.0,  # 缩短图例列之间的距离
        )

        self.draw()

class PieChart(FigureCanvas):
    def __init__(self, parent=None, rang_list=None, data_count=None,type=None):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111, aspect='equal')
        super(PieChart, self).__init__(self.fig)
        self.setParent(parent)

        self.type=type
        #self.labels = ['', '', '', '']  # 去掉扇形上的文字
        self.ranges = rang_list  # 每个区间的范围百分比
        self.data = [float(x) for x in data_count]  # 确保数据为数字类型
        self.colors = ['green', (0.6, 1, 0.6), 'orange', 'red']
        self.legend_labels = ["正常", "轻度", "中度", "重度"]  # 图例文字
        self.plot_pie()

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

            distance_multiplier = 1.38  # 调整基础距离倍数
            dx = distance_multiplier * x
            dy = distance_multiplier * y

            # 防止标签重叠
            for ann_x, ann_y in annotation_positions:
                while np.hypot(dx - ann_x, dy - ann_y) < 0.5:  # 增加最小距离
                    dx += 0.05 * np.sign(dx - ann_x)
                    dy += 0.05 * np.sign(dy - ann_y)

            # 防止超出视角
            dx = np.clip(dx, -1.5, 1.5)
            dy = np.clip(dy, -1.5, 1.5)

            xytext = (dx, dy)
            bbox_props = dict(boxstyle="round,pad=0.3", edgecolor="none", facecolor=self.colors[i], alpha=0.5)

            # 调整箭头指向
            # 调整箭头指向
            self.ax.annotate(f'{self.ranges[i]}%',
                             xy=(x, y),
                             xytext=xytext,
                             arrowprops=dict(arrowstyle="-", connectionstyle="arc3", color='black'),
                             horizontalalignment='center',
                             verticalalignment='center',
                             bbox=bbox_props,
                             fontproperties='Microsoft YaHei', fontsize=12)
            annotation_positions.append((dx, dy))

        # 添加图例
        # 调整饼图的位置
        self.ax.set_position([0.2, 0.068, 0.75, 0.80])  # 调整饼图以腾出空间给图例

        legend_handles = [patches.Patch(color=color, label=label) for color, label in
                          zip(self.colors, self.legend_labels)]

        if self.type == 0:
            # 在图例上方添加文本
            self.ax.text(
                -0.9, 0.8,  # 文本的位置，(x, y) 坐标与 bbox_to_anchor 相关
                "抑郁统计图",  # 你要添加的文字内容
                transform=self.ax.transAxes,  # 使用轴坐标系
                fontsize=14,  # 字体大小
                verticalalignment='bottom',  # 垂直对齐方式
                horizontalalignment='center'  # 水平对齐方式
            )
        elif self.type == 1:
            self.ax.text(
                -0.9, 0.8,  # 文本的位置，(x, y) 坐标与 bbox_to_anchor 相关
                "焦虑统计图",  # 你要添加的文字内容
                transform=self.ax.transAxes,  # 使用轴坐标系
                fontsize=14,  # 字体大小
                verticalalignment='bottom',  # 垂直对齐方式
                horizontalalignment='center'  # 水平对齐方式
            )

        self.ax.legend(
            handles=legend_handles,
            loc='center left',  # 将图例放置在左边中部
            bbox_to_anchor=(-1.2, 0.4),  # 调整图例的位置
            ncol=1,  # 每行显示1个条目，这样垂直显示
            fontsize=14,  # 增大图例中文字的字体大小
            handletextpad=0.5,  # 缩短图例标签和图例标记之间的距离
            columnspacing=1.0,  # 缩短图例列之间的距离
        )

        # # 在中间上方加个标题
        # if self.type==0:
        #     self.ax.set_title("抑郁统计图", fontsize=15, pad=0)
        # elif self.type==1:
        #     self.ax.set_title("焦虑统计图", fontsize=15, pad=0)
        self.draw()


class New_WgtData_Analyze(QWidget, Ui_data_):
    def __init__(self,api):
        super(New_WgtData_Analyze, self).__init__()
        self.setupUi(self)


        self.setWindowFlags(Qt.FramelessWindowHint) #无边框

        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setWindowIcon(QIcon(":/icon/res/logo.png"))
        self.setWindowTitle('数据分析')

        self.comboBox_3.setView(QListView())  # 性别
        self.comboBox_3.addItems(["所有","男", "女"])
        self.comboBox_3.setCurrentIndex(0)

        self.comboBox_3.currentIndexChanged.connect(self.on_combobox_index_changed_sex)

        self.pbhide_6.setMouseTracking(True)
        self.pbhide_6.setToolTip("窗口最小化")
        self.pbhide_6.clicked.connect(self.showMinimized)

        self.pbClose_5.setMouseTracking(True)
        self.pbClose_5.setToolTip("关闭程序")
        self.pbClose_5.clicked.connect(self.close)
        self.pie_chart_left=None
        self.pie_chart_right = None
        self.pie_chart1 = None
        self.pie_chart = None
        self.api=api

        self.textEdit_6.setFont(QFont("Microsoft YaHei", 10))
        self.textEdit_2.setFont(QFont("Microsoft YaHei", 10))
        self.textEdit_3.setFont(QFont("Microsoft YaHei", 10))

        self.textEdit_6.setText("通过分析Fp1(左前额)、Fpz(前正中)和Fp2(右前额)三导联的EEG数据，提取出与抑郁相关的脑电特征，包括α波、θ波和β波频率带功率和前额叶不对称性等。这些特征可以帮助评估心理健康，为临床诊断和治疗提供有价值的信息")

        self.textEdit_2.setReadOnly(True)
        self.textEdit_3.setReadOnly(True)
        self.textEdit_6.setReadOnly(True)


        self.comboBox_11.setView(QListView())
        res, school_list = self.api.get_school_order_by()
        self.comboBox_11.addItem("请选择")
        self.comboBox_11.addItems(school_list)
        self.comboBox_11.setCurrentIndex(0)


        self.comboBox_9.setView(QListView())
        self.comboBox_10.setView(QListView())  # 学校

        self.comboBox_11.currentIndexChanged.connect(self.on_combobox_index_changed)
        self.comboBox_9.currentIndexChanged.connect(self.on_combobox_index_changed)
        self.comboBox_10.currentIndexChanged.connect(self.on_combobox_index_changed)
        self.school_name = ""
        self.grade_name = ""

        self.init_data()


    def on_combobox_index_changed(self):
        try:
            self.comboBox_11.blockSignals(True)
            self.comboBox_9.blockSignals(True)
            self.comboBox_10.blockSignals(True)

            school_text = self.comboBox_11.currentText()
            sender = self.sender()

            if self.comboBox_11.currentText() == "请选择":
                self.comboBox_10.clear()
                self.comboBox_9.clear()

            if self.comboBox_9.currentText() == "请选择":
                self.comboBox_10.clear()

            if sender == self.comboBox_11:
                self.comboBox_9.clear()
                self.comboBox_10.clear()
                res, grade_list = self.api.get_grade_order_by(school_text)
                self.comboBox_9.addItem("请选择")
                self.comboBox_9.addItems(grade_list)
                self.comboBox_9.setCurrentIndex(0)

            if sender == self.comboBox_9:
                self.comboBox_10.clear()
                grade_text = self.comboBox_9.currentText()
                res, class_list = self.api.get_class_order_by(school_text, grade_text)
                self.comboBox_10.addItem("请选择")
                self.comboBox_10.addItems(class_list)
                self.comboBox_10.setCurrentIndex(0)

        finally:
            # 重新启用信号
            self.comboBox_11.blockSignals(False)
            self.comboBox_9.blockSignals(False)
            self.comboBox_10.blockSignals(False)


        self.search_()

    def search_(self):
        school=self.comboBox_11.currentText()
        if school=="请选择":
            school=""
        grade=self.comboBox_9.currentText()
        if grade=="请选择":
            grade=""
        Class=self.comboBox_10.currentText()
        if Class=="请选择":
            Class=""

        res,self.step_list=self.api.new_get_anxiety_depressed_result(school=school,grade=grade,Class= Class)
        if res:
            self.school_name=school
            self.grade_name=grade

            self.search_init_data()
            self.on_combobox_index_changed_sex()
            # anxiety

    def search_init_data(self):
        self.total_people = len(self.step_list)  # 总人数

        self.normal_count = 0  # 正常
        self.normal_man = 0  # 正常男
        self.normal_woman = 0  # 正常女

        self.abnormal_count = 0  # 异常
        self.abnormal_man = 0  # 异常男
        self.abnormal_woman = 0  # 异常女

        self.depressed_count = 0  # 抑郁
        self.depressed_man = 0
        self.depressed_woman = 0

        self.anxiety_count = 0  # 焦虑
        self.anxiety_man = 0
        self.anxiety_woman = 0

        self.anxiety_depressed_count = 0  # 焦虑
        self.anxiety_depressed_man = 0
        self.anxiety_depressed_woman = 0

        self.depressed_zc_count = 0  # 抑郁正常人
        self.depressed_qd_count = 0  # 轻度抑郁
        self.depressed_zd_count = 0  # 中度抑郁
        self.depressed_zhong_count = 0  # 重度抑郁

        self.depressed_qd_man = 0  # 轻度抑郁男
        self.depressed_zd_man = 0  # 中度抑郁男
        self.depressed_zhong_man = 0  # 重度抑郁男

        self.anxiety_zc_count = 0  # 焦虑正常人
        self.anxiety_qd_count = 0  # 轻度焦虑
        self.anxiety_zd_count = 0  # 中度焦虑
        self.anxiety_zhong_count = 0  # 重度焦虑

        self.anxiety_qd_man = 0  # 轻度焦虑男
        self.anxiety_zd_man = 0  # 中度焦虑男
        self.anxiety_zhong_man = 0  # 重度焦虑男

        for i in self.step_list:
            if i["anxiety_result"] == "正常" and i["depressed_result"] == '正常':  # 正常
                self.normal_count += 1
                if i["sex"] == "男":
                    self.normal_man += 1
                else:
                    self.normal_woman += 1

            if i["depressed_result"] == "正常":  # 抑郁
                self.depressed_zc_count += 1

            if i["depressed_result"] != "正常":
                if i["depressed_result"] == "轻度":
                    self.depressed_qd_count += 1
                    if i["sex"] == "男":
                        self.depressed_qd_man += 1

                elif i["depressed_result"] == "中度":
                    self.depressed_zd_count += 1
                    if i["sex"] == "男":
                        self.depressed_zd_man += 1

                elif i["depressed_result"] == "重度":
                    self.depressed_zhong_count += 1
                    if i["sex"] == "男":
                        self.depressed_zhong_man += 1

                if i["depressed_result"] != "正常" and i["anxiety_result"] == '正常':  # 抑郁
                    self.depressed_count += 1
                    if i["sex"] == "男":
                        self.depressed_man += 1
                    else:
                        self.depressed_woman += 1

            if i["anxiety_result"] == "正常":  # 焦虑
                self.anxiety_zc_count += 1

            if i["anxiety_result"] != "正常":
                if i["anxiety_result"] == "轻度":
                    self.anxiety_qd_count += 1
                    if i["sex"] == "男":
                        self.anxiety_qd_man += 1

                elif i["anxiety_result"] == "中度":
                    self.anxiety_zd_count += 1
                    if i["sex"] == "男":
                        self.anxiety_zd_man += 1

                elif i["anxiety_result"] == "重度":
                    self.anxiety_zhong_count += 1
                    if i["sex"] == "男":
                        self.anxiety_zhong_man += 1

                if i["depressed_result"] == "正常" and i["anxiety_result"] != '正常':  # 焦虑
                    self.anxiety_count += 1
                    if i["sex"] == "男":
                        self.anxiety_man += 1
                    else:
                        self.anxiety_woman += 1

            if i["depressed_result"] != "正常" and i["anxiety_result"] != '正常':  # 焦虑 抑郁
                self.anxiety_depressed_count += 1
                if i["sex"] == "男":
                    self.anxiety_depressed_man += 1
                else:
                    self.anxiety_depressed_woman += 1

            if i["anxiety_result"] != "正常" or i["depressed_result"] != '正常':  # 异常
                self.abnormal_count += 1
                if i["sex"] == "男":
                    if i["anxiety_result"] == "轻度" or i["depressed_result"] == '轻度':  # 男 焦虑抑郁
                        pass

                    self.abnormal_man += 1
                else:
                    if i["anxiety_result"] == "轻度" or i["depressed_result"] == '轻度':  # 女 焦虑抑郁
                        pass

                    self.abnormal_woman += 1

        self.total_man = self.normal_man + self.depressed_man + self.anxiety_man + self.anxiety_depressed_man  # 男总人数
        self.total_woman = self.total_people - self.total_man  # 女总人数

        self.depressed_yy = self.total_people - self.depressed_zc_count  # 抑郁人数

        self.depressed_ = self.depressed_qd_man + self.depressed_zd_man + self.depressed_zhong_man  # 抑郁男人数
        self.depressed_wu = self.depressed_yy - self.depressed_  # 抑郁女人数

        self.anxiety_jl = self.total_people - self.anxiety_zc_count  # 焦虑人数
        self.anxiety_ = self.anxiety_qd_man + self.anxiety_zd_man + self.anxiety_zhong_man  # 焦虑男人数
        self.anxiety_wu = self.anxiety_jl - self.anxiety_  # 焦虑女人数


    def on_combobox_index_changed_sex(self):
        if self.comboBox_3.currentText() == "所有":
            self.init_data_man_woman()
        elif self.comboBox_3.currentText() == "女":
            self.init_data_woman()
        elif self.comboBox_3.currentText() == "男":
            self.init_data_man()

    def init_data_man_woman(self):
        if self.total_people == 0:
            comment_2 = "数据分析:抑郁总人数为0人(男0%,女0%),其中轻度抑郁有0人(男0%,女0%)占比检测总人数的0%。中度抑郁有0人(男0%,女0%)占比检测总人数的0%。重度抑郁有0人(男0%,女0%)占比检测总人数的0%"

            comment_3 = "数据分析:焦虑总人数为0人(男0%,女0%),其中轻度焦虑有0人(男0%,女0%)占比检测总人数的0%。中度焦虑有0人(男0%,女0%)占比检测总人数的0%。重度焦虑有0人(男0%,女0%)占比检测总人数的0%"
        else:
            comment_2 = f"数据分析:抑郁总人数为{self.depressed_yy}人"
            if self.depressed_yy != 0:
                male_percent = int((self.depressed_ / self.depressed_yy) * 100)
                female_percent = 100 - male_percent
            else:
                male_percent = female_percent = 0

            comment_2 += f"(男{male_percent}%, 女{female_percent}%)"
            if self.depressed_qd_count != 0:
                male_qd_percent = int((self.depressed_qd_man / self.depressed_qd_count) * 100)
                female_qd_percent = 100 - male_qd_percent
                qd_total_percent = (self.depressed_qd_count / self.total_people) * 100
            else:
                male_qd_percent = female_qd_percent = qd_total_percent = 0

            comment_2 += f"，其中轻度抑郁有{self.depressed_qd_count}人(男{male_qd_percent}%, 女{female_qd_percent}%)占比检测总人数的{qd_total_percent:.2f}%"

            if self.depressed_zd_count != 0:
                male_zd_percent = int((self.depressed_zd_man / self.depressed_zd_count) * 100)
                female_zd_percent = 100 - male_zd_percent
                zd_total_percent = (self.depressed_zd_count / self.total_people) * 100
            else:
                male_zd_percent = female_zd_percent = zd_total_percent = 0

            comment_2 += f"，中度抑郁有{self.depressed_zd_count}人(男{male_zd_percent}%, 女{female_zd_percent}%)占比检测总人数的{zd_total_percent:.2f}%"

            if self.depressed_zhong_count != 0:
                male_zhong_percent = int((self.depressed_zhong_man / self.depressed_zhong_count) * 100)
                female_zhong_percent = 100 - male_zhong_percent
                zhong_total_percent = (self.depressed_zhong_count / self.total_people) * 100
            else:
                male_zhong_percent = female_zhong_percent = zhong_total_percent = 0

            comment_2 += f"，重度抑郁有{self.depressed_zhong_count}人(男{male_zhong_percent}%, 女{female_zhong_percent}%)占比检测总人数的{zhong_total_percent:.2f}%"

            comment_3 = f"数据分析:焦虑总人数为{self.anxiety_jl}人"

            if self.anxiety_jl != 0:
                male_percent = int((self.anxiety_ / self.anxiety_jl) * 100)
                female_percent = 100 - male_percent
            else:
                male_percent = female_percent = 0

            comment_3 += f"(男{male_percent}%, 女{female_percent}%)"

            if self.anxiety_qd_count != 0:
                male_qd_percent = int((self.anxiety_qd_man / self.anxiety_qd_count) * 100)
                female_qd_percent = 100 - male_qd_percent
                qd_total_percent = (self.anxiety_qd_count / self.total_people) * 100
            else:
                male_qd_percent = female_qd_percent = qd_total_percent = 0

            comment_3 += f"，其中轻度焦虑有{self.anxiety_qd_count}人(男{male_qd_percent}%, 女{female_qd_percent}%)占比检测总人数的{qd_total_percent:.2f}%"

            if self.anxiety_zd_count != 0:
                male_zd_percent = int((self.anxiety_zd_man / self.anxiety_zd_count) * 100)
                female_zd_percent = 100 - male_zd_percent
                zd_total_percent = (self.anxiety_zd_count / self.total_people) * 100
            else:
                male_zd_percent = female_zd_percent = zd_total_percent = 0

            comment_3 += f"，中度焦虑有{self.anxiety_zd_count}人(男{male_zd_percent}%, 女{female_zd_percent}%)占比检测总人数的{zd_total_percent:.2f}%"

            if self.anxiety_zhong_count != 0:
                male_zhong_percent = int((self.anxiety_zhong_man / self.anxiety_zhong_count) * 100)
                female_zhong_percent = 100 - male_zhong_percent
                zhong_total_percent = (self.anxiety_zhong_count / self.total_people) * 100
            else:
                male_zhong_percent = female_zhong_percent = zhong_total_percent = 0

            comment_3 += f"，重度焦虑有{self.anxiety_zhong_count}人(男{male_zhong_percent}%, 女{female_zhong_percent}%)占比检测总人数的{zhong_total_percent:.2f}%"

        self.textEdit_2.setText(comment_2)  # 抑郁数据
        self.textEdit_3.setText(comment_3)  # 焦虑数据

        self.label_41.setText(str(self.total_people))  # 总人数
        self.label_43.setText(f"男{self.total_man}人,女{self.total_woman}人")

        self.label_37.setText(str(self.normal_count))  # 正常
        self.label_39.setText(f"男{self.normal_man}人,女{self.normal_woman}人")

        self.label_51.setText(str(self.abnormal_count))  # 异常
        self.label_53.setText(f"男{self.abnormal_man}人,女{self.abnormal_woman}人")

        self.label_46.setText(str(self.depressed_count))  # 抑郁
        self.label_48.setText(f"男{self.depressed_man}人,女{self.depressed_woman}人")

        self.label_60.setText(str(self.anxiety_count))  # 焦虑
        self.label_62.setText(f"男{self.anxiety_man}人,女{self.anxiety_woman}人")

        self.label_56.setText(str(self.anxiety_depressed_count))  # 抑郁焦虑
        self.label_58.setText(f"男{self.anxiety_depressed_man}人,女{self.anxiety_depressed_woman}人")

        self.label_64.setText(str(self.total_people))
        self.label_66.setText(f"男{self.total_man}人,女{self.total_woman}人")

        self.label_68.setText(str(self.depressed_zc_count))  # 抑郁正常
        self.label_70.setText(f"男{self.total_man - self.depressed_}人,女{self.total_woman - self.depressed_wu}人")

        self.label_73.setText(str(self.depressed_qd_count))  # 抑郁轻度
        self.label_75.setText(f"男{self.depressed_qd_man}人,女{self.depressed_qd_count - self.depressed_qd_man}人")

        self.label_78.setText(str(self.depressed_zd_count))  # 抑郁中度
        self.label_80.setText(f"男{self.depressed_zd_man}人,女{self.depressed_zd_count - self.depressed_zd_man}人")

        self.label_83.setText(str(self.depressed_zhong_count))  # 抑郁重度
        self.label_85.setText(
            f"男{self.depressed_zhong_man}人,女{self.depressed_zhong_count - self.depressed_zhong_man}人")

        self.label_88.setText(str(self.total_people))
        self.label_90.setText(f"男{self.total_man}人,女{self.total_woman}人")

        self.label_92.setText(str(self.anxiety_zc_count))  # 焦虑正常
        self.label_94.setText(f"男{self.total_man - self.anxiety_}人,女{self.total_woman - self.anxiety_wu}人")

        self.label_97.setText(str(self.anxiety_qd_count))  # 焦虑轻度
        self.label_99.setText(f"男{self.anxiety_qd_man}人,女{self.anxiety_qd_count - self.anxiety_qd_man}人")

        self.label_102.setText(str(self.anxiety_zd_count))  # 焦虑中度
        self.label_104.setText(f"男{self.anxiety_zd_man}人,女{self.anxiety_zd_count - self.anxiety_zd_man}人")

        self.label_107.setText(str(self.anxiety_zhong_count))  # 焦虑重度
        self.label_109.setText(
            f"男{self.anxiety_zhong_man}人,女{self.anxiety_zhong_count - self.anxiety_zhong_man}人")


        if self.total_people != 0:
            if self.normal_count == 0:  # 正常
                normal = 0
            else:
                result = self.normal_count / self.total_people
                rounded_result = round(result, 2)
                normal = int(rounded_result * 100)

            mild = 100 - normal

            rang_list = [normal, mild]
            data_count = [str(self.normal_count), str(self.abnormal_count)]

            if self.pie_chart_left:
                self.pie_chart_left.ranges=rang_list
                self.pie_chart_left.data=[float(x) for x in data_count]
                self.pie_chart_left.plot_pie()
            else:
                self.pie_chart_left = PieChart_left(self, rang_list, data_count)  # 正常  抑郁 焦虑  抑郁焦虑
                layout = QVBoxLayout()
                layout.addWidget(self.pie_chart_left)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)

                self.widget_2.setLayout(layout)

            if self.normal_count == 0:  # 正常
                normal = 0
            else:
                result = self.normal_count / self.total_people
                rounded_result = round(result, 2)
                normal = int(rounded_result * 100)

            if self.depressed_count == 0:  # 抑郁
                mild = 0
            else:
                result = self.depressed_count / self.total_people
                rounded_result = round(result, 2)
                mild = int(rounded_result * 100)

            if self.anxiety_count == 0:  # 焦虑
                moderate = 0
            else:
                result = self.anxiety_count / self.total_people
                rounded_result = round(result, 2)
                moderate = int(rounded_result * 100)

            severe = 100 - moderate - mild - normal
            rang_list = [normal, mild, moderate, severe]

            data_count = [str(self.normal_count), str(self.depressed_count), str(self.anxiety_count),
                          str(self.anxiety_depressed_count)]

            if self.pie_chart_right:
                self.pie_chart_right.ranges=rang_list
                self.pie_chart_right.data=[float(x) for x in data_count]
                self.pie_chart_right.plot_pie()
            else:
                self.pie_chart_right = PieChart_right(self, rang_list, data_count)  # 正常  抑郁 焦虑  抑郁焦虑
                layout = QVBoxLayout()
                layout.addWidget(self.pie_chart_right)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)
                self.widget_3.setLayout(layout)

            if self.depressed_zc_count == 0:  # 抑郁正常
                normal = 0
            else:
                result = self.depressed_zc_count / self.total_people
                rounded_result = round(result, 2)
                normal = int(rounded_result * 100)

            if self.depressed_qd_count == 0:  # 抑郁轻度
                mild = 0
            else:
                result = self.depressed_qd_count / self.total_people
                rounded_result = round(result, 2)
                mild = int(rounded_result * 100)

            if self.depressed_zd_count == 0:  # 抑郁中度
                moderate = 0
            else:
                result = self.depressed_zd_count / self.total_people
                rounded_result = round(result, 2)
                moderate = int(rounded_result * 100)

            if self.depressed_zhong_count == 0:  # 抑郁重度
                severe = 0
            else:
                result = self.depressed_zhong_count / self.total_people
                rounded_result = round(result, 2)
                severe = int(rounded_result * 100)

            rang_list = [normal, mild, moderate, severe]
            data_count = [str(self.depressed_zc_count), str(self.depressed_qd_count), str(self.depressed_zd_count),
                          str(self.depressed_zhong_count)]

            if self.pie_chart:
                self.pie_chart.ranges=rang_list
                self.pie_chart.data=[float(x) for x in data_count]
                self.pie_chart.plot_pie()
            else:
                self.pie_chart = PieChart(self, rang_list, data_count,0)  # 正常  抑郁 焦虑  抑郁焦虑
                layout = QVBoxLayout()
                layout.addWidget(self.pie_chart)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)
                self.widget.setLayout(layout)

            if self.anxiety_zc_count == 0:  # 抑郁正常
                normal = 0
            else:
                result = self.anxiety_zc_count / self.total_people
                rounded_result = round(result, 2)
                normal = int(rounded_result * 100)

            if self.anxiety_qd_count == 0:  # 抑郁轻度
                mild = 0
            else:
                result = self.anxiety_qd_count / self.total_people
                rounded_result = round(result, 2)
                mild = int(rounded_result * 100)

            if self.anxiety_zd_count == 0:  # 抑郁中度
                moderate = 0
            else:
                result = self.anxiety_zd_count / self.total_people
                rounded_result = round(result, 2)
                moderate = int(rounded_result * 100)

            if self.anxiety_zhong_count == 0:  # 抑郁重度
                severe = 0
            else:
                result = self.anxiety_zhong_count / self.total_people
                rounded_result = round(result, 2)
                severe = int(rounded_result * 100)

            rang_list = [normal, mild, moderate, severe]
            data_count = [str(self.anxiety_zc_count), str(self.anxiety_qd_count), str(self.anxiety_zd_count),
                          str(self.anxiety_zhong_count)]

            if self.pie_chart1:
                self.pie_chart1.ranges=rang_list
                self.pie_chart1.data=[float(x) for x in data_count]
                self.pie_chart1.plot_pie()
            else:
                self.pie_chart1 = PieChart(self, rang_list, data_count,1)  # 正常  抑郁 焦虑  抑郁焦虑
                layout = QVBoxLayout()
                layout.addWidget(self.pie_chart1)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)
                self.widget_5.setLayout(layout)

        else:
            if self.pie_chart_left:
                self.pie_chart_left.clear_and_clean()
            if self.pie_chart_right:
                self.pie_chart_right.clear_and_clean()
            if self.pie_chart1:
                self.pie_chart1.clear_and_clean()
            if self.pie_chart:
                self.pie_chart.clear_and_clean()


    def init_data_man(self):
        # 男
        self.label_43.setText("")
        self.label_39.setText("")
        self.label_53.setText("")
        self.label_48.setText("")
        self.label_62.setText("")
        self.label_58.setText("")
        self.label_66.setText("")
        self.label_70.setText("")
        self.label_75.setText("")
        self.label_80.setText("")
        self.label_85.setText("")
        self.label_90.setText("")
        self.label_94.setText("")
        self.label_99.setText("")
        self.label_104.setText("")
        self.label_109.setText("")

        self.label_41.setText(str(self.total_man))  # 总人数男
        self.label_37.setText(str(self.normal_man))  # 正常男

        self.label_51.setText(str(self.abnormal_man))  # 异常男
        self.label_46.setText(str(self.depressed_man))  # 抑郁男
        self.label_60.setText(str(self.anxiety_man))  # 焦虑男
        self.label_56.setText(str(self.anxiety_depressed_man))  # 抑郁焦虑男

        self.label_64.setText(str(self.total_man))
        self.label_68.setText(str(self.total_man - self.depressed_))  # 抑郁正常男
        self.label_73.setText(str(self.depressed_qd_man))  # 抑郁轻度男
        self.label_78.setText(str(self.depressed_zd_man))  # 抑郁中度男
        self.label_83.setText(str(self.depressed_zhong_man))  # 抑郁重度男

        self.label_88.setText(str(self.total_man))
        self.label_92.setText(str(self.total_man - self.anxiety_))  # 焦虑正常男
        self.label_97.setText(str(self.anxiety_qd_man))  # 焦虑轻度男
        self.label_102.setText(str(self.anxiety_zd_man))  # 焦虑中度男
        self.label_107.setText(str(self.anxiety_zhong_man))  # 焦虑重度男

        if self.total_man==0:
            comment_2 = f"数据分析:抑郁总人数为0人,其中轻度抑郁有0人,占比检测总人数的0%。中度抑郁有0人,占比检测总数0%。重度抑郁0人,占比检测总人致的0%"

            comment_3 = "数据分析:焦虑总人数为0人,其中轻度焦虑有0人,占比检测总人数的0%。中度焦虑有0人,占比检测总数0%。重度焦虑0人,占比检测总人致的0%"
        else:
            comment_2 = f"数据分析:抑郁总人数为{self.depressed_}人,其中轻度抑郁有{self.depressed_qd_man}人,占比检测总人数的{int((self.depressed_qd_man / self.total_man) * 100) if self.total_man != 0 else 0}%。中度抑郁有{self.depressed_zd_man}人,占比检测总人数的{int((self.depressed_zd_man / self.total_man) * 100) if self.total_man != 0 else 0}%。重度抑郁有{self.depressed_zhong_man}人,占比检测总人数的{int((self.depressed_zhong_man / self.total_man) * 100) if self.total_man != 0 else 0}%。"

            comment_3 = f"数据分析:焦虑总人数为{self.anxiety_}人,其中轻度焦虑有{self.anxiety_qd_man}人,占比检测总人数的{int((self.anxiety_qd_man / self.total_man) * 100) if self.total_man != 0 else 0}%。中度焦虑有{self.anxiety_zd_man}人,占比检测总人数的{int((self.anxiety_zd_man / self.total_man) * 100) if self.total_man != 0 else 0}%。重度焦虑有{self.anxiety_zhong_man}人,占比检测总人数的{int((self.anxiety_zhong_man / self.total_man) * 100) if self.total_man != 0 else 0}%。"


        self.textEdit_2.setText(comment_2)  # 抑郁男数据
        self.textEdit_3.setText(comment_3)  # 焦虑男数据

        if self.total_man != 0:
            if self.normal_man == 0:  # 正常
                normal = 0
            else:
                result = self.normal_man / self.total_man
                rounded_result = round(result, 2)
                normal = int(rounded_result * 100)

            mild = 100 - normal

            rang_list = [normal, mild]
            data_count = [str(self.normal_man), str(self.abnormal_man)]
            if self.pie_chart_left:
                self.pie_chart_left.ranges=rang_list
                self.pie_chart_left.data=[float(x) for x in data_count]
                self.pie_chart_left.plot_pie()
            else:
                self.pie_chart_left = PieChart_left(self, rang_list, data_count)  # 正常 异常
                layout = QVBoxLayout()
                layout.addWidget(self.pie_chart_left)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)
                self.widget_2.setLayout(layout)


            if self.normal_man == 0:  # 正常
                normal = 0
            else:
                result = self.normal_man / self.total_man
                rounded_result = round(result, 2)
                normal = int(rounded_result * 100)

            if self.depressed_man == 0:  # 抑郁
                mild = 0
            else:
                result = self.depressed_man / self.total_man
                rounded_result = round(result, 2)
                mild = int(rounded_result * 100)

            if self.anxiety_man == 0:  # 焦虑
                moderate = 0
            else:
                result = self.anxiety_man / self.total_man
                rounded_result = round(result, 2)
                moderate = int(rounded_result * 100)

            severe = 100 - moderate - mild - normal
            rang_list = [normal, mild, moderate, severe]

            data_count = [str(self.normal_man), str(self.depressed_man), str(self.anxiety_man),
                          str(self.anxiety_depressed_man)]

            if self.pie_chart_right:
                self.pie_chart_right.ranges=rang_list
                self.pie_chart_right.data=[float(x) for x in data_count]
                self.pie_chart_right.plot_pie()
            else:
                self.pie_chart_right = PieChart_right(self, rang_list, data_count)  # 正常  抑郁 焦虑  抑郁焦虑
                layout = QVBoxLayout()
                layout.addWidget(self.pie_chart_right)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)
                self.widget_3.setLayout(layout)

            if (self.total_man - self.depressed_) == 0:  # 抑郁正常
                normal = 0
            else:
                result = (self.total_man - self.depressed_) / self.total_man
                rounded_result = round(result, 2)
                normal = int(rounded_result * 100)

            if (self.depressed_qd_man) == 0:  # 抑郁轻度
                mild = 0
            else:
                result = (self.depressed_qd_man) / self.total_man
                rounded_result = round(result, 2)
                mild = int(rounded_result * 100)

            if (self.depressed_zd_man) == 0:  # 抑郁中度
                moderate = 0
            else:
                result = (self.depressed_zd_man) / self.total_man
                rounded_result = round(result, 2)
                moderate = int(rounded_result * 100)

            if (self.depressed_zhong_man) == 0:  # 抑郁重度
                severe = 0
            else:
                result = (self.depressed_zhong_man) / self.total_man
                rounded_result = round(result, 2)
                severe = int(rounded_result * 100)

            rang_list = [normal, mild, moderate, severe]
            data_count = [str(self.total_man - self.depressed_), str(self.depressed_qd_man), str(self.depressed_zd_man),
                          str(self.depressed_zhong_man)]

            if self.pie_chart:
                self.pie_chart.ranges=rang_list
                self.pie_chart.data=[float(x) for x in data_count]
                self.pie_chart.plot_pie()
            else:
                self.pie_chart = PieChart(self, rang_list, data_count,0)  # 正常  抑郁 焦虑  抑郁焦虑
                layout = QVBoxLayout()
                layout.addWidget(self.pie_chart)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)
                self.widget.setLayout(layout)


            if (self.total_man - self.anxiety_) == 0:  # 焦虑正常
                normal = 0
            else:
                result = (self.total_man - self.anxiety_)/ self.total_man
                rounded_result = round(result, 2)
                normal = int(rounded_result * 100)

            if (self.anxiety_qd_man) == 0:  # 焦虑轻度
                mild = 0
            else:
                result = (self.anxiety_qd_man) / self.total_man
                rounded_result = round(result, 2)
                mild = int(rounded_result * 100)

            if (self.anxiety_zd_man) == 0:  # 焦虑中度
                moderate = 0
            else:
                result = (self.anxiety_zd_man) / self.total_man
                rounded_result = round(result, 2)
                moderate = int(rounded_result * 100)

            if (self.anxiety_zhong_man) == 0:  # 焦虑重度
                severe = 0
            else:
                result = (self.anxiety_zhong_man) / self.total_man
                rounded_result = round(result, 2)
                severe = int(rounded_result * 100)

            rang_list = [normal, mild, moderate, severe]
            data_count = [str(self.total_man - self.anxiety_), str(self.anxiety_qd_man), str(self.anxiety_zd_man),
                          str(self.anxiety_zhong_man)]

            if self.pie_chart1:
                self.pie_chart1.ranges=rang_list
                self.pie_chart1.data=[float(x) for x in data_count]
                self.pie_chart1.plot_pie()
            else:
                self.pie_chart1 = PieChart(self, rang_list, data_count,1)  # 正常  抑郁 焦虑  抑郁焦虑
                layout = QVBoxLayout()
                layout.addWidget(self.pie_chart1)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)
                self.widget_5.setLayout(layout)

        else:
            if self.pie_chart_left:
                self.pie_chart_left.clear_and_clean()
            if self.pie_chart_right:
                self.pie_chart_right.clear_and_clean()
            if self.pie_chart1:
                self.pie_chart1.clear_and_clean()
            if self.pie_chart:
                self.pie_chart.clear_and_clean()

    def init_data_woman(self):
        #女
        self.label_43.setText("")
        self.label_39.setText("")
        self.label_53.setText("")
        self.label_48.setText("")
        self.label_62.setText("")
        self.label_58.setText("")
        self.label_66.setText("")
        self.label_70.setText("")
        self.label_75.setText("")
        self.label_80.setText("")
        self.label_85.setText("")
        self.label_90.setText("")
        self.label_94.setText("")
        self.label_99.setText("")
        self.label_104.setText("")
        self.label_109.setText("")

        self.label_41.setText(str(self.total_woman))  #总人数女
        self.label_37.setText(str(self.normal_woman)) #正常女

        self.label_51.setText(str(self.abnormal_woman)) # 异常女
        self.label_46.setText(str(self.depressed_woman))  #抑郁女
        self.label_60.setText(str(self.anxiety_woman))  #焦虑女
        self.label_56.setText(str(self.anxiety_depressed_woman))  #抑郁焦虑女

        self.label_64.setText(str(self.total_woman))
        self.label_68.setText(str(self.total_woman-self.depressed_wu)) #抑郁正常女
        self.label_73.setText(str(self.depressed_qd_count-self.depressed_qd_man)) #抑郁轻度女
        self.label_78.setText(str(self.depressed_zd_count-self.depressed_zd_man))  #抑郁中度女
        self.label_83.setText(str(self.depressed_zhong_count-self.depressed_zhong_man))#抑郁重度女

        self.label_88.setText(str(self.total_woman))
        self.label_92.setText(str(self.total_woman - self.anxiety_wu))  # 焦虑正常女
        self.label_97.setText(str(self.anxiety_qd_count - self.anxiety_qd_man))  # 焦虑轻度女
        self.label_102.setText(str(self.anxiety_zd_count - self.anxiety_zd_man))  # 焦虑中度女
        self.label_107.setText(str(self.anxiety_zhong_count - self.anxiety_zhong_man))  # 焦虑重度女

        if self.total_woman==0:
            comment_2 = "数据分析:抑郁总人数为0人,其中轻度抑郁有0人,占比检测总人数0%。中度抑郁有0人,占比检测总人数0%。重度抑郁0人,占比检测总人致的0%"

            comment_3 = "数据分析:焦虑总人数为0人,其中轻度焦虑有0人,占比检测总人数的0%。中度焦虑有0人,占比检测总人数的0%。重度焦虑0人,占比检测总人致的0%"

        else:
            comment_2 = f"数据分析:抑郁总人数为{self.depressed_wu}人,其中轻度抑郁有{self.depressed_qd_count - self.depressed_qd_man}人,占比检测总人数的{int(((self.depressed_qd_count - self.depressed_qd_man) / self.total_woman) * 100) if self.total_woman != 0 else 0}%。中度抑郁有{self.depressed_zd_count - self.depressed_zd_man}人,占比检测总人数的{int(((self.depressed_zd_count - self.depressed_zd_man) / self.total_woman) * 100) if self.total_woman != 0 else 0}%。重度抑郁有{self.depressed_zhong_count - self.depressed_zhong_man}人,占比检测总人数的{int(((self.depressed_zhong_count - self.depressed_zhong_man) / self.total_woman) * 100) if self.total_woman != 0 else 0}%。"


            comment_3 = f"数据分析:焦虑总人数为{self.anxiety_wu}人,其中轻度焦虑有{self.anxiety_qd_count - self.anxiety_qd_man}人,占比检测总人数的{int(((self.anxiety_qd_count - self.anxiety_qd_man) / self.total_woman) * 100) if self.total_woman != 0 else 0}%。中度焦虑有{self.anxiety_zd_count - self.anxiety_zd_man}人,占比检测总人数的{int(((self.anxiety_zd_count - self.anxiety_zd_man) / self.total_woman) * 100) if self.total_woman != 0 else 0}%。重度焦虑有{self.anxiety_zhong_count - self.anxiety_zhong_man}人,占比检测总人数的{int(((self.anxiety_zhong_count - self.anxiety_zhong_man) / self.total_woman) * 100) if self.total_woman != 0 else 0}%。"



        self.textEdit_2.setText(comment_2)  # 抑郁女数据
        self.textEdit_3.setText(comment_3)  # 焦虑女数据



        if self.total_woman != 0:
            if self.normal_woman == 0:  # 正常
                normal = 0
            else:
                result = self.normal_woman / self.total_woman
                rounded_result = round(result, 2)
                normal = int(rounded_result * 100)

            mild = 100 - normal

            rang_list = [normal, mild]
            data_count = [str(self.normal_woman), str(self.abnormal_woman)]
            if self.pie_chart_left:
                self.pie_chart_left.ranges=rang_list
                self.pie_chart_left.data=[float(x) for x in data_count]
                self.pie_chart_left.plot_pie()
            else:
                self.pie_chart_left = PieChart_left(self, rang_list, data_count)  # 正常 异常
                layout = QVBoxLayout()
                layout.addWidget(self.pie_chart_left)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)
                self.widget_2.setLayout(layout)


            if self.normal_woman == 0:  # 正常
                normal = 0
            else:
                result = self.normal_woman / self.total_woman
                rounded_result = round(result, 2)
                normal = int(rounded_result * 100)

            if self.depressed_woman == 0:  # 抑郁
                mild = 0
            else:
                result = self.depressed_woman / self.total_woman
                rounded_result = round(result, 2)
                mild = int(rounded_result * 100)

            if self.anxiety_woman == 0:  # 焦虑
                moderate = 0
            else:
                result = self.anxiety_woman / self.total_woman
                rounded_result = round(result, 2)
                moderate = int(rounded_result * 100)

            severe = 100 - moderate - mild - normal
            rang_list = [normal, mild, moderate, severe]

            data_count = [str(self.normal_woman), str(self.depressed_woman), str(self.anxiety_woman),
                          str(self.anxiety_depressed_woman)]

            if self.pie_chart_right:
                self.pie_chart_right.ranges=rang_list
                self.pie_chart_right.data=[float(x) for x in data_count]
                self.pie_chart_right.plot_pie()
            else:
                self.pie_chart_right = PieChart_right(self, rang_list, data_count)  # 正常  抑郁 焦虑  抑郁焦虑
                layout = QVBoxLayout()
                layout.addWidget(self.pie_chart_right)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)
                self.widget_3.setLayout(layout)

            if (self.total_woman-self.depressed_wu) == 0:  # 抑郁正常
                normal = 0
            else:
                result = (self.total_woman-self.depressed_wu) / self.total_woman
                rounded_result = round(result, 2)
                normal = int(rounded_result * 100)

            if (self.depressed_qd_count-self.depressed_qd_man) == 0:  # 抑郁轻度
                mild = 0
            else:
                result = (self.depressed_qd_count-self.depressed_qd_man) / self.total_woman
                rounded_result = round(result, 2)
                mild = int(rounded_result * 100)

            if (self.depressed_zd_count-self.depressed_zd_man) == 0:  # 抑郁中度
                moderate = 0
            else:
                result = (self.depressed_zd_count-self.depressed_zd_man) / self.total_woman
                rounded_result = round(result, 2)
                moderate = int(rounded_result * 100)

            if (self.depressed_zhong_count-self.depressed_zhong_man) == 0:  # 抑郁重度
                severe = 0
            else:
                result = (self.depressed_zhong_count-self.depressed_zhong_man) / self.total_woman
                rounded_result = round(result, 2)
                severe = int(rounded_result * 100)

            rang_list = [normal, mild, moderate, severe]
            data_count = [str(self.total_woman-self.depressed_wu), str(self.depressed_qd_count-self.depressed_qd_man), str(self.depressed_zd_count-self.depressed_zd_man),
                          str(self.depressed_zhong_count-self.depressed_zhong_man)]

            if self.pie_chart:
                self.pie_chart.ranges=rang_list
                self.pie_chart.data=[float(x) for x in data_count]
                self.pie_chart.plot_pie()
            else:
                self.pie_chart = PieChart(self, rang_list, data_count,0)  # 正常  抑郁 焦虑  抑郁焦虑
                layout = QVBoxLayout()
                layout.addWidget(self.pie_chart)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)
                self.widget.setLayout(layout)


            if (self.total_woman - self.anxiety_wu) == 0:  # 焦虑正常
                normal = 0
            else:
                result = (self.total_woman - self.anxiety_wu)/ self.total_woman
                rounded_result = round(result, 2)
                normal = int(rounded_result * 100)

            if (self.anxiety_qd_count - self.anxiety_qd_man) == 0:  # 焦虑轻度
                mild = 0
            else:
                result = (self.anxiety_qd_count - self.anxiety_qd_man) / self.total_woman
                rounded_result = round(result, 2)
                mild = int(rounded_result * 100)

            if (self.anxiety_zd_count - self.anxiety_zd_man) == 0:  # 焦虑中度
                moderate = 0
            else:
                result = (self.anxiety_zd_count - self.anxiety_zd_man) / self.total_woman
                rounded_result = round(result, 2)
                moderate = int(rounded_result * 100)

            if (self.anxiety_zhong_count - self.anxiety_zhong_man) == 0:  # 焦虑重度
                severe = 0
            else:
                result = (self.anxiety_zhong_count - self.anxiety_zhong_man) / self.total_woman
                rounded_result = round(result, 2)
                severe = int(rounded_result * 100)

            rang_list = [normal, mild, moderate, severe]
            data_count = [str(self.total_woman - self.anxiety_wu), str(self.anxiety_qd_count - self.anxiety_qd_man), str(self.anxiety_zd_count - self.anxiety_zd_man),
                          str(self.anxiety_zhong_count - self.anxiety_zhong_man)]

            if self.pie_chart1:
                self.pie_chart1.ranges=rang_list
                self.pie_chart1.data=[float(x) for x in data_count]
                self.pie_chart1.plot_pie()
            else:
                self.pie_chart1 = PieChart(self, rang_list, data_count,1)  # 正常  抑郁 焦虑  抑郁焦虑
                layout = QVBoxLayout()
                layout.addWidget(self.pie_chart1)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)
                self.widget_5.setLayout(layout)

        else:
            if self.pie_chart_left:
                self.pie_chart_left.clear_and_clean()
            if self.pie_chart_right:
                self.pie_chart_right.clear_and_clean()
            if self.pie_chart1:
                self.pie_chart1.clear_and_clean()
            if self.pie_chart:
                self.pie_chart.clear_and_clean()



    def init_data(self):
        res,self.step_list=self.api.new_get_anxiety_depressed_result()
        if res:
            self.search_init_data()
            if self.total_people == 0:
                comment_2 = "数据分析:抑郁总人数为0人(男0%,女0%),其中轻度抑郁有0人(男0%,女0%)占比检测总人数的0%。中度抑郁有0人(男0%,女0%)占比检测总人数的0%。重度抑郁有0人(男0%,女0%)占比检测总人数的0%"

                comment_3 = "数据分析:焦虑总人数为0人(男0%,女0%),其中轻度焦虑有0人(男0%,女0%)占比检测总人数的0%。中度焦虑有0人(男0%,女0%)占比检测总人数的0%。重度焦虑有0人(男0%,女0%)占比检测总人数的0%"
            else:

                comment_2 = f"数据分析:抑郁总人数为{self.depressed_yy}人(男{int((self.depressed_ / self.depressed_yy) * 100) if self.depressed_yy != 0 else 0}%, 女{100 - int((self.depressed_ / self.depressed_yy) * 100) if self.depressed_yy != 0 else 0}%), 其中轻度抑郁有{self.depressed_qd_count}人(男{int((self.depressed_qd_man / self.depressed_qd_count) * 100) if self.depressed_qd_count != 0 else 0}%, 女{100 - int((self.depressed_qd_man / self.depressed_qd_count) * 100) if self.depressed_qd_count != 0 else 0}%)占比检测总人数的{self.depressed_qd_count / self.total_people:.2f}%" if self.total_people != 0 else "占比检测总人数的0.00%中度抑郁有{self.depressed_zd_count}人(男{int((self.depressed_zd_man / self.depressed_zd_count) * 100) if self.depressed_zd_count != 0 else 0}%, 女{100 - int((self.depressed_zd_man / self.depressed_zd_count) * 100) if self.depressed_zd_count != 0 else 0}%)占比检测总人数的{self.depressed_zd_count / self.total_people:.2f}%" if self.total_people != 0 else "占比检测总人数的0.00%重度抑郁有{self.depressed_zhong_count}人(男{int((self.depressed_zhong_man / self.depressed_zhong_count) * 100) if self.depressed_zhong_count != 0 else 0}%, 女{100 - int((self.depressed_zhong_man / self.depressed_zhong_count) * 100) if self.depressed_zhong_count != 0 else 0}%)占比检测总人数的{self.depressed_zhong_count / self.total_people:.2f}%" if self.total_people != 0 else "占比检测总人数的0.00%"


                comment_3 = "数据分析:焦虑总人数为" + str(self.anxiety_jl) + "人" + "(男" + str(int((self.anxiety_ / self.anxiety_jl) * 100) if self.anxiety_jl != 0 else 0) + "%, " + "女" + str(100 - int((self.anxiety_ / self.anxiety_jl) * 100) if self.anxiety_jl != 0 else 0) + "%), " + "其中轻度焦虑有" + str(self.anxiety_qd_count) + "人" + "(男" + str(int((self.anxiety_qd_man / self.anxiety_qd_count) * 100) if self.anxiety_qd_count != 0 else 0) + "%, " + "女" + str(100 - int((self.anxiety_qd_man / self.anxiety_qd_count) * 100) if self.anxiety_qd_count != 0 else 0) + "%) " + "占比检测总人数的" + "{:.2f}".format(self.anxiety_qd_count / self.total_people * 100) + "%" if self.total_people != 0 else "占比检测总人数的0.00%, " + "中度焦虑有" + str(self.anxiety_zd_count) + "人" + "(男" + str(int((self.anxiety_zd_man / self.anxiety_zd_count) * 100) if self.anxiety_zd_count != 0 else 0) + "%, " + "女" + str(100 - int((self.anxiety_zd_man / self.anxiety_zd_count) * 100) if self.anxiety_zd_count != 0 else 0) + "%) " + "占比检测总人数的" + "{:.2f}".format(self.anxiety_zd_count / self.total_people * 100) + "%" if self.total_people != 0 else "占比检测总人数的0.00%, " + "重度焦虑有" + str(self.anxiety_zhong_count) + "人" + "(男" + str(int((self.anxiety_zhong_man / self.anxiety_zhong_count) * 100) if self.anxiety_zhong_count != 0 else 0) + "%, " + "女" + str(100 - int((self.anxiety_zhong_man / self.anxiety_zhong_count) * 100) if self.anxiety_zhong_count != 0 else 0) + "%) " + "占比检测总人数的" + "{:.2f}".format(self.anxiety_zhong_count / self.total_people * 100) + "%" if self.total_people != 0 else "占比检测总人数的0.00%"


            self.textEdit_2.setText(comment_2)  # 抑郁数据
            self.textEdit_3.setText(comment_3)  #焦虑数据

            self.label_41.setText(str(self.total_people))  # 总人数
            self.label_43.setText(f"男{self.total_man}人,女{self.total_woman}人")

            self.label_37.setText(str(self.normal_count))  # 正常
            self.label_39.setText(f"男{self.normal_man}人,女{self.normal_woman}人")

            self.label_51.setText(str(self.abnormal_count))  # 异常
            self.label_53.setText(f"男{self.abnormal_man}人,女{self.abnormal_woman}人")

            self.label_46.setText(str(self.depressed_count))  # 抑郁
            self.label_48.setText(f"男{self.depressed_man}人,女{self.depressed_woman}人")

            self.label_60.setText(str(self.anxiety_count))  # 焦虑
            self.label_62.setText(f"男{self.anxiety_man}人,女{self.anxiety_woman}人")

            self.label_56.setText(str(self.anxiety_depressed_count))  # 抑郁焦虑
            self.label_58.setText(f"男{self.anxiety_depressed_man}人,女{self.anxiety_depressed_woman}人")

            self.label_64.setText(str(self.total_people))
            self.label_66.setText(f"男{self.total_man}人,女{self.total_woman}人")

            self.label_68.setText(str(self.depressed_zc_count))  # 抑郁正常
            self.label_70.setText(f"男{self.total_man - self.depressed_}人,女{self.total_woman - self.depressed_wu}人")

            self.label_73.setText(str(self.depressed_qd_count))  # 抑郁轻度
            self.label_75.setText(f"男{self.depressed_qd_man}人,女{self.depressed_qd_count - self.depressed_qd_man}人")

            self.label_78.setText(str(self.depressed_zd_count))  # 抑郁中度
            self.label_80.setText(f"男{self.depressed_zd_man}人,女{self.depressed_zd_count - self.depressed_zd_man}人")

            self.label_83.setText(str(self.depressed_zhong_count))  # 抑郁重度
            self.label_85.setText(f"男{self.depressed_zhong_man}人,女{self.depressed_zhong_count - self.depressed_zhong_man}人")

            self.label_88.setText(str(self.total_people))
            self.label_90.setText(f"男{self.total_man}人,女{self.total_woman}人")

            self.label_92.setText(str(self.anxiety_zc_count))  # 焦虑正常
            self.label_94.setText(f"男{self.total_man - self.anxiety_}人,女{self.total_woman - self.anxiety_wu}人")

            self.label_97.setText(str(self.anxiety_qd_count))  # 焦虑轻度
            self.label_99.setText(f"男{self.anxiety_qd_man}人,女{self.anxiety_qd_count - self.anxiety_qd_man}人")

            self.label_102.setText(str(self.anxiety_zd_count))  # 焦虑中度
            self.label_104.setText(f"男{self.anxiety_zd_man}人,女{self.anxiety_zd_count - self.anxiety_zd_man}人")

            self.label_107.setText(str(self.anxiety_zhong_count))  # 焦虑重度
            self.label_109.setText(f"男{self.anxiety_zhong_man}人,女{self.anxiety_zhong_count - self.anxiety_zhong_man}人")


            if self.total_people!=0:
                if self.normal_count == 0: #正常
                    normal = 0
                else:
                    result = self.normal_count / self.total_people
                    rounded_result = round(result, 2)
                    normal = int(rounded_result * 100)


                mild = 100-normal

                rang_list = [normal, mild]
                data_count = [str(self.normal_count), str(self.abnormal_count)]

                self.pie_chart_left = PieChart_left(self, rang_list, data_count)  # 正常 异常
                layout = QVBoxLayout()
                layout.addWidget(self.pie_chart_left)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)
                self.widget_2.setLayout(layout)


                if self.normal_count == 0:  # 正常
                    normal = 0
                else:
                    result = self.normal_count / self.total_people
                    rounded_result = round(result, 2)
                    normal = int(rounded_result * 100)

                if self.depressed_count == 0:  # 抑郁
                    mild = 0
                else:
                    result = self.depressed_count / self.total_people
                    rounded_result = round(result, 2)
                    mild = int(rounded_result * 100)

                if self.anxiety_count == 0:  # 焦虑
                    moderate = 0
                else:
                    result = self.anxiety_count / self.total_people
                    rounded_result = round(result, 2)
                    moderate = int(rounded_result * 100)


                severe = 100-moderate-mild-normal
                rang_list = [normal, mild, moderate, severe]

                data_count = [str(self.normal_count), str(self.depressed_count), str(self.anxiety_count),
                              str(self.anxiety_depressed_count)]

                self.pie_chart_right = PieChart_right(self, rang_list, data_count)  # 正常  抑郁 焦虑  抑郁焦虑
                layout = QVBoxLayout()
                layout.addWidget(self.pie_chart_right)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)
                self.widget_3.setLayout(layout)

                if self.depressed_zc_count == 0: #抑郁正常
                    normal = 0
                else:
                    result = self.depressed_zc_count / self.total_people
                    rounded_result = round(result, 2)
                    normal = int(rounded_result * 100)

                if self.depressed_qd_count == 0: #抑郁轻度
                    mild = 0
                else:
                    result = self.depressed_qd_count / self.total_people
                    rounded_result = round(result, 2)
                    mild = int(rounded_result * 100)

                if self.depressed_zd_count == 0: #抑郁中度
                    moderate = 0
                else:
                    result = self.depressed_zd_count /self.total_people
                    rounded_result = round(result, 2)
                    moderate = int(rounded_result * 100)

                if self.depressed_zhong_count == 0: #抑郁重度
                    severe = 0
                else:
                    result = self.depressed_zhong_count / self.total_people
                    rounded_result = round(result, 2)
                    severe = int(rounded_result * 100)

                rang_list = [normal, mild, moderate, severe]
                data_count = [str(self.depressed_zc_count), str(self.depressed_qd_count), str(self.depressed_zd_count), str(self.depressed_zhong_count)]

                self.pie_chart = PieChart(self, rang_list, data_count,0)  # 抑郁
                self.pie_chart.type=0

                layout = QVBoxLayout()
                layout.addWidget(self.pie_chart)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)
                self.widget.setLayout(layout)


                if self.anxiety_zc_count == 0: #抑郁正常
                    normal = 0
                else:
                    result = self.anxiety_zc_count / self.total_people
                    rounded_result = round(result, 2)
                    normal = int(rounded_result * 100)

                if self.anxiety_qd_count == 0: #抑郁轻度
                    mild = 0
                else:
                    result = self.anxiety_qd_count / self.total_people
                    rounded_result = round(result, 2)
                    mild = int(rounded_result * 100)

                if self.anxiety_zd_count == 0: #抑郁中度
                    moderate = 0
                else:
                    result = self.anxiety_zd_count /self.total_people
                    rounded_result = round(result, 2)
                    moderate = int(rounded_result * 100)

                if self.anxiety_zhong_count == 0: #抑郁重度
                    severe = 0
                else:
                    result = self.anxiety_zhong_count / self.total_people
                    rounded_result = round(result, 2)
                    severe = int(rounded_result * 100)

                rang_list = [normal, mild, moderate, severe]
                data_count = [str(self.anxiety_zc_count), str(self.anxiety_qd_count), str(self.anxiety_zd_count), str(self.anxiety_zhong_count)]

                self.pie_chart1 = PieChart(self, rang_list, data_count,1)  # 焦虑

                layout1 = QVBoxLayout()
                layout1.addWidget(self.pie_chart1)
                layout1.setContentsMargins(0, 0, 0, 0)
                layout1.setSpacing(0)
                self.widget_5.setLayout(layout1)

