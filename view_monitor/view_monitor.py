from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog

from view_monitor.view_monitor_ui import ViewMonitorUI


class ViewMonitor(QDialog, ViewMonitorUI):
    def __init__(self, job_name):
        QDialog.__init__(self, None, Qt.Dialog)
        self.setupUi(self, job_name)
