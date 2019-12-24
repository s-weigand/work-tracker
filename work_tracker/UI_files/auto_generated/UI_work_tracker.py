# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\inno_Admin_Dropbox\Dropbox\innoAdmin\adminTools\work_tracker_new\UI_files\UI_work_tracker.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_work_tracker(object):
    def setupUi(self, work_tracker):
        work_tracker.setObjectName("work_tracker")
        work_tracker.resize(307, 166)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(work_tracker.sizePolicy().hasHeightForWidth())
        work_tracker.setSizePolicy(sizePolicy)
        work_tracker.setMaximumSize(QtCore.QSize(307, 166))
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/icons/inno_admin.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off
        )
        work_tracker.setWindowIcon(icon)
        work_tracker.setStyleSheet(
            "#work_tracker{\n"
            "    margin:0px;\n"
            "    padding:0px;\n"
            "}\n"
            "QGroupBox{\n"
            'font: 12pt "Times New Roman";\n'
            "}\n"
            "QPushButton{\n"
            'font: 75 20pt "Times New Roman";\n'
            "}\n"
            "QComboBox{\n"
            "border:                    none;\n"
            "background-color:  rgba(255, 0, 0, 0);\n"
            "font-weight:            bold;\n"
            "padding-left:           5px;\n"
            "}\n"
            "QComboBox::drop-down{\n"
            "    border:                 none;\n"
            "    background-color:   rgba(255, 0, 0, 0);\n"
            "    font-weight:            bold;\n"
            "    margin-right:        5px;\n"
            "}\n"
            "\n"
            "QComboBox::down-arrow{\n"
            "    image:                      url(:/icons/down_arrow.svg);\n"
            "    width:                    16px;\n"
            "    height:                    16px;\n"
            "    padding:                    10px;\n"
            "}\n"
            "*{\n"
            "font:                        bold;\n"
            "}"
        )
        self.gridLayout = QtWidgets.QGridLayout(work_tracker)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(5)
        self.gridLayout.setObjectName("gridLayout")
        self.start_btn = QtWidgets.QPushButton(work_tracker)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.start_btn.sizePolicy().hasHeightForWidth())
        self.start_btn.setSizePolicy(sizePolicy)
        self.start_btn.setMinimumSize(QtCore.QSize(150, 40))
        self.start_btn.setCheckable(True)
        self.start_btn.setFlat(True)
        self.start_btn.setObjectName("start_btn")
        self.gridLayout.addWidget(self.start_btn, 2, 0, 1, 1)
        self.stop_btn = QtWidgets.QPushButton(work_tracker)
        self.stop_btn.setMinimumSize(QtCore.QSize(150, 40))
        self.stop_btn.setCheckable(True)
        self.stop_btn.setFlat(True)
        self.stop_btn.setObjectName("stop_btn")
        self.gridLayout.addWidget(self.stop_btn, 2, 1, 1, 1)
        self.session_box = QtWidgets.QGroupBox(work_tracker)
        self.session_box.setMinimumSize(QtCore.QSize(150, 40))
        self.session_box.setAlignment(QtCore.Qt.AlignCenter)
        self.session_box.setFlat(False)
        self.session_box.setObjectName("session_box")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.session_box)
        self.verticalLayout.setObjectName("verticalLayout")
        self.session_time = QtWidgets.QLCDNumber(self.session_box)
        self.session_time.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.session_time.sizePolicy().hasHeightForWidth())
        self.session_time.setSizePolicy(sizePolicy)
        self.session_time.setMinimumSize(QtCore.QSize(131, 61))
        self.session_time.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.session_time.setLineWidth(0)
        self.session_time.setSmallDecimalPoint(False)
        self.session_time.setObjectName("session_time")
        self.verticalLayout.addWidget(self.session_time)
        self.gridLayout.addWidget(self.session_box, 1, 1, 1, 1)
        self.startBox = QtWidgets.QGroupBox(work_tracker)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.startBox.sizePolicy().hasHeightForWidth())
        self.startBox.setSizePolicy(sizePolicy)
        self.startBox.setMinimumSize(QtCore.QSize(150, 100))
        self.startBox.setAlignment(QtCore.Qt.AlignCenter)
        self.startBox.setFlat(False)
        self.startBox.setObjectName("startBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.startBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.start_time = QtWidgets.QLCDNumber(self.startBox)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.start_time.sizePolicy().hasHeightForWidth())
        self.start_time.setSizePolicy(sizePolicy)
        self.start_time.setMinimumSize(QtCore.QSize(131, 61))
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.start_time.setFont(font)
        self.start_time.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.start_time.setLineWidth(0)
        self.start_time.setSmallDecimalPoint(False)
        self.start_time.setObjectName("start_time")
        self.verticalLayout_2.addWidget(self.start_time)
        self.gridLayout.addWidget(self.startBox, 1, 0, 1, 1)
        self.occupation_comboBox = QtWidgets.QComboBox(work_tracker)
        self.occupation_comboBox.setStyleSheet("")
        self.occupation_comboBox.setFrame(False)
        self.occupation_comboBox.setObjectName("occupation_comboBox")
        self.occupation_comboBox.addItem("")
        self.occupation_comboBox.addItem("")
        self.occupation_comboBox.addItem("")
        self.gridLayout.addWidget(self.occupation_comboBox, 0, 1, 1, 1)
        self.occupation_label = QtWidgets.QLabel(work_tracker)
        self.occupation_label.setIndent(5)
        self.occupation_label.setObjectName("occupation_label")
        self.gridLayout.addWidget(self.occupation_label, 0, 0, 1, 1)

        self.retranslateUi(work_tracker)
        QtCore.QMetaObject.connectSlotsByName(work_tracker)

    def retranslateUi(self, work_tracker):
        _translate = QtCore.QCoreApplication.translate
        work_tracker.setWindowTitle(_translate("work_tracker", "Stechkarte"))
        self.start_btn.setText(_translate("work_tracker", "Start"))
        self.stop_btn.setText(_translate("work_tracker", "Stop"))
        self.session_box.setTitle(_translate("work_tracker", "   time today   "))
        self.startBox.setTitle(_translate("work_tracker", "  working since   "))
        self.occupation_comboBox.setItemText(0, _translate("work_tracker", "OnPrEx"))
        self.occupation_comboBox.setItemText(1, _translate("work_tracker", "RemEx"))
        self.occupation_comboBox.setItemText(2, _translate("work_tracker", "Inno"))
        self.occupation_label.setText(_translate("work_tracker", "Occupation:"))


from . import icons_rc

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    work_tracker = QtWidgets.QWidget()
    ui = Ui_work_tracker()
    ui.setupUi(work_tracker)
    work_tracker.show()
    sys.exit(app.exec_())
