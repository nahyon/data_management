import configparser
import os
import config

from PySide6.QtCore import QRect, Qt
from PySide6.QtWidgets import *
#from PyQt5.QtWidgets import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class GetFileUI(object):
    def setupUi(self, window: QDialog): #window: QMainWindow
        #database
        client = config.get_client()
        database = client[config.database_name]
        monitor = database["monitor"]
        result = database["result20"]
        
        window.setWindowTitle('서울시 데이터 저장')
        central = QWidget(window)
        #window.setCentralWidget(central)


        mainLayout = QGridLayout(central)
        
        #####################################################
        selectLayout = QHBoxLayout()
        mainLayout.addLayout(selectLayout, 0, 0) # main레이아웃에 추가

        # add a top "margin"
        selectLayout.addStretch(1) #중간정렬됨

        self.lineid_combobox = QComboBox()
        self.roadname_combobox = QComboBox()
        self.heading_combobox = QComboBox()
        self.track_combobox = QComboBox()
        selectLayout.addWidget(self.lineid_combobox)
        selectLayout.addWidget(self.roadname_combobox)
        selectLayout.addWidget(self.heading_combobox)
        selectLayout.addWidget(self.track_combobox)

        lineid_list = monitor.find({"job_id": "2022년_서울시"}).distinct("line_id")
        self.lineid_combobox.addItems(lineid_list)

        self.search_button = QPushButton('검색')
        selectLayout.addWidget(self.search_button, alignment=Qt.AlignHCenter)

        # add a bottom "margin"
        selectLayout.addStretch(1) #중간정렬됨

        ##############################################################
        tableLayout = QVBoxLayout()
        mainLayout.addLayout(tableLayout, 1, 0) # main레이아웃에 추가

        self.monitor_table = QTableWidget(window)
        tableLayout.addWidget(self.monitor_table)


        #tableLayout.addStretch(1)
        #####################################################
        filepathLayout = QGridLayout()
        mainLayout.addLayout(filepathLayout, 2, 0) # main레이아웃에 추가

        
        #filepathLayout.addStretch(1) #왼쪽에 마진 
        
        self.report_path_label = QLabel(window)
        filepathLayout.addWidget(self.report_path_label, 0,  0, alignment=Qt.AlignHCenter)
        self.report_path_label.setText("저장 경로 : ")
        #self.report_path_label.setAlignment(Qt.AlignCenter)

        self.report_path = QLineEdit(window)
        #self.report_path.setFixedWidth(400)
        filepathLayout.addWidget(self.report_path, 0,  1)
        self.report_path.setDisabled(True)

        self.find_button = QPushButton(window)
        filepathLayout.addWidget(self.find_button, 0, 2, alignment=Qt.AlignHCenter)
        self.find_button.setText("찾기")
        self.find_button.setDisabled(True)
        

        #####################################################
        selectLayout = QHBoxLayout()
        mainLayout.addLayout(selectLayout, 3, 0) # main레이아웃에 추가

        
        selectLayout.addStretch(1) #왼쪽에 마진 
        
        self.csv_save_button = QPushButton('csv 저장')
        selectLayout.addWidget(self.csv_save_button, alignment=Qt.AlignHCenter)
        self.graph_save_button = QPushButton('그래프 PNG 저장')
        selectLayout.addWidget(self.graph_save_button, alignment=Qt.AlignHCenter)
        self.pdf_save_button = QPushButton('PDF 변환')
        selectLayout.addWidget(self.pdf_save_button, alignment=Qt.AlignHCenter)
        self.csv_save_button.setDisabled(True) 
        self.graph_save_button.setDisabled(True) 
        self.pdf_save_button.setDisabled(True)

        ##############################################################
        window.setFixedSize(650, 360)

