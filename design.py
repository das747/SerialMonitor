# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'design.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1438, 782)
        MainWindow.setTabShape(QtWidgets.QTabWidget.Rounded)
        MainWindow.setUnifiedTitleAndToolBarOnMac(True)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setObjectName("main_layout")
        self.output_layot = QtWidgets.QVBoxLayout()
        self.output_layot.setObjectName("output_layot")
        self.top_outpyt_layout = QtWidgets.QHBoxLayout()
        self.top_outpyt_layout.setObjectName("top_outpyt_layout")
        self.input_line = QtWidgets.QLineEdit(self.centralwidget)
        self.input_line.setObjectName("input_line")
        self.top_outpyt_layout.addWidget(self.input_line)
        self.send_btn = QtWidgets.QPushButton(self.centralwidget)
        self.send_btn.setObjectName("send_btn")
        self.top_outpyt_layout.addWidget(self.send_btn)
        self.output_layot.addLayout(self.top_outpyt_layout)
        self.out_view = QtWidgets.QColumnView(self.centralwidget)
        self.out_view.setTextElideMode(QtCore.Qt.ElideNone)
        self.out_view.setObjectName("out_view")
        self.output_layot.addWidget(self.out_view)
        self.bottom_output_layout = QtWidgets.QHBoxLayout()
        self.bottom_output_layout.setObjectName("bottom_output_layout")
        self.time_chk = QtWidgets.QCheckBox(self.centralwidget)
        self.time_chk.setObjectName("time_chk")
        self.bottom_output_layout.addWidget(self.time_chk)
        self.scroll_chk = QtWidgets.QCheckBox(self.centralwidget)
        self.scroll_chk.setObjectName("scroll_chk")
        self.bottom_output_layout.addWidget(self.scroll_chk)
        spacerItem = QtWidgets.QSpacerItem(16, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.bottom_output_layout.addItem(spacerItem)
        self.end_box = QtWidgets.QComboBox(self.centralwidget)
        self.end_box.setObjectName("end_box")
        self.bottom_output_layout.addWidget(self.end_box)
        self.clear_btn = QtWidgets.QPushButton(self.centralwidget)
        self.clear_btn.setObjectName("clear_btn")
        self.bottom_output_layout.addWidget(self.clear_btn)
        self.output_layot.addLayout(self.bottom_output_layout)
        self.main_layout.addLayout(self.output_layot)
        self.pref_layout = QtWidgets.QVBoxLayout()
        self.pref_layout.setObjectName("pref_layout")
        self.port_pref_label = QtWidgets.QLabel(self.centralwidget)
        self.port_pref_label.setAlignment(QtCore.Qt.AlignCenter)
        self.port_pref_label.setObjectName("port_pref_label")
        self.pref_layout.addWidget(self.port_pref_label)
        self.port_layout = QtWidgets.QHBoxLayout()
        self.port_layout.setObjectName("port_layout")
        self.port_switch_label = QtWidgets.QLabel(self.centralwidget)
        self.port_switch_label.setObjectName("port_switch_label")
        self.port_layout.addWidget(self.port_switch_label)
        self.port_box = QtWidgets.QComboBox(self.centralwidget)
        self.port_box.setObjectName("port_box")
        self.port_layout.addWidget(self.port_box)
        self.input_sep_label = QtWidgets.QLabel(self.centralwidget)
        self.input_sep_label.setObjectName("input_sep_label")
        self.port_layout.addWidget(self.input_sep_label)
        self.input_sep_box = QtWidgets.QComboBox(self.centralwidget)
        self.input_sep_box.setObjectName("input_sep_box")
        self.port_layout.addWidget(self.input_sep_box)
        self.baudreate_label = QtWidgets.QLabel(self.centralwidget)
        self.baudreate_label.setObjectName("baudreate_label")
        self.port_layout.addWidget(self.baudreate_label)
        self.baudrate_box = QtWidgets.QComboBox(self.centralwidget)
        self.baudrate_box.setObjectName("baudrate_box")
        self.port_layout.addWidget(self.baudrate_box)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.port_layout.addItem(spacerItem1)
        self.connect_btn = QtWidgets.QPushButton(self.centralwidget)
        self.connect_btn.setObjectName("connect_btn")
        self.port_layout.addWidget(self.connect_btn)
        self.pref_layout.addLayout(self.port_layout)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.pref_layout.addWidget(self.label)
        self.export_layout = QtWidgets.QHBoxLayout()
        self.export_layout.setObjectName("export_layout")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.export_layout.addWidget(self.label_2)
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setObjectName("comboBox")
        self.export_layout.addWidget(self.comboBox)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.export_layout.addItem(spacerItem2)
        self.pref_layout.addLayout(self.export_layout)
        self.main_layout.addLayout(self.pref_layout)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.main_layout.addItem(spacerItem3)
        self.horizontalLayout.addLayout(self.main_layout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionexport_as = QtWidgets.QAction(MainWindow)
        self.actionexport_as.setObjectName("actionexport_as")

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.send_btn.setText(_translate("MainWindow", "PushButton"))
        self.time_chk.setText(_translate("MainWindow", "CheckBox"))
        self.scroll_chk.setText(_translate("MainWindow", "CheckBox"))
        self.clear_btn.setText(_translate("MainWindow", "PushButton"))
        self.port_pref_label.setText(_translate("MainWindow", "TextLabel"))
        self.port_switch_label.setText(_translate("MainWindow", "TextLabel"))
        self.input_sep_label.setText(_translate("MainWindow", "TextLabel"))
        self.baudreate_label.setText(_translate("MainWindow", "TextLabel"))
        self.connect_btn.setText(_translate("MainWindow", "PushButton"))
        self.label.setText(_translate("MainWindow", "TextLabel"))
        self.label_2.setText(_translate("MainWindow", "TextLabel"))
        self.actionexport_as.setText(_translate("MainWindow", "export as..."))
