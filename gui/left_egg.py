# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'left_egg.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_left_eeg_form(object):
    def setupUi(self, left_eeg_form):
        left_eeg_form.setObjectName("left_eeg_form")
        left_eeg_form.resize(725, 338)
        left_eeg_form.setStyleSheet("")
        self.verticalLayout = QtWidgets.QVBoxLayout(left_eeg_form)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.retranslateUi(left_eeg_form)
        QtCore.QMetaObject.connectSlotsByName(left_eeg_form)

    def retranslateUi(self, left_eeg_form):
        _translate = QtCore.QCoreApplication.translate
        left_eeg_form.setWindowTitle(_translate("left_eeg_form", "Form"))
