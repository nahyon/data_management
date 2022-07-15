from PySide6 import QtGui
from PySide6.QtCore import QRect, Qt
from PySide6.QtWidgets import *

import config


class ViewMonitorUI(object):
    def setupUi(self, window: QDialog, job_name):
        window.setWindowTitle("현황 상태")  # 창 제목
        window.setFixedSize(570, 320)  # 창 크기
        window.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # 창 크기 고정

        self.monitor_table = QTableWidget(window)
        self.monitor_table.setGeometry(QRect(10, 10, 550, 300))
        self.monitor_table.setColumnCount(4)
        client = config.get_client()
        database = client[config.database_name]
        monitor = database["monitor"]
        result = database["result"]
        result20 = database["result20"]
        
        
        monitor_list = monitor.find({"job_id": job_name}).distinct("monitor_id")
        
        self.monitor_table.setRowCount(len(monitor_list))
        
        
        self.monitor_table.setColumnWidth(0, 250)
        self.monitor_table.setColumnWidth(1, 75) 
        self.monitor_table.setColumnWidth(2, 75)
        self.monitor_table.setColumnWidth(3, 75)

        self.monitor_table.setHorizontalHeaderLabels(["조사 ID", "조사 연장", "등록된 연장", "차이"])
        self.monitor_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        

        query_monitor = monitor.aggregate(
            [
                {"$match": {"job_id": job_name}},
                {"$group": {
                    "_id": "$monitor_id",
                    "length": {"$sum": {"$subtract": ["$monitor_end_station", "$monitor_start_station"]}},
                    "count": {"$sum": 1}
                }},
                {"$sort" : {"monitor_id" : 1}},
            ]
        )

        
        
        result_list = []
        for monitor_item in query_monitor:
            query_result = result.count_documents({"job_name": job_name, "monitor_id": monitor_item["_id"]})
            result_list.append({"_id": monitor_item["_id"], "length": monitor_item["length"], "count": query_result})

        result_list = sorted(result_list, key=lambda x: (-abs(round((float(x["count"]) / 100) - (float(x["length"]) / 1000), 2))))
        for index, monitor_item in enumerate(result_list):
            self.monitor_table.setItem(index, 0, QTableWidgetItem(monitor_item["_id"]))
            self.monitor_table.setItem(index, 1, QTableWidgetItem(str(float(monitor_item["length"]) / 1000)))
            self.monitor_table.setItem(index, 2, QTableWidgetItem(str(float(monitor_item["count"]) / 100)))
            self.monitor_table.setItem(index, 3, QTableWidgetItem(str(round((float(monitor_item["count"]) / 100) - (float(monitor_item["length"]) / 1000), 2))))
            if monitor_item["count"] * 10 != monitor_item["length"]:
                self.monitor_table.item(index, 0).setBackground(QtGui.QColor(255, 0, 0))
                self.monitor_table.item(index, 1).setBackground(QtGui.QColor(255, 0, 0))
                self.monitor_table.item(index, 2).setBackground(QtGui.QColor(255, 0, 0))
                self.monitor_table.item(index, 3).setBackground(QtGui.QColor(255, 0, 0))
                self.monitor_table.item(index, 0).setForeground(QtGui.QColor(255, 255, 255))
                self.monitor_table.item(index, 1).setForeground(QtGui.QColor(255, 255, 255))
                self.monitor_table.item(index, 2).setForeground(QtGui.QColor(255, 255, 255))
                self.monitor_table.item(index, 3).setForeground(QtGui.QColor(255, 255, 255))
