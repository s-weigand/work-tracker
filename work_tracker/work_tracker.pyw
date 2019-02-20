# -*- coding: utf-8 -*-
"""
"""
from PyQt5 import QtWidgets
from .UI_files.worktracker_main import WorkTracker

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    work_tracker = WorkTracker()
    work_tracker.show()
    #  pushing new db before exiting programm
    app.aboutToQuit.connect(work_tracker.quit_handler)
    sys.exit(app.exec_())
