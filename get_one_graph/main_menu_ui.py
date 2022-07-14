import configparser
import os

import pymongo
from PySide6.QtCore import QRect, Qt
from PySide6.QtWidgets import *
#from PyQt5.QtWidgets import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pymongo

host_ip: str = "192.168.0.241"
port_number: int = 27017
database_name = "Roadtech"
user_name = "Roadtech"
password = "031500455!"


def get_client():
    global host_ip, user_name, password
    connection = pymongo.MongoClient(f"mongodb://{user_name}:{password}@{host_ip}")
    return connection

class MainMenuUI(object):
    def setupUi(self, window: QMainWindow):
        window.setWindowTitle("로드텍 데이터베이스 관리 프로그램")  # 창 제목
        window.setFixedSize(710+350, 680)  # 창 크기 (가로, 세로)710, 680) 
        window.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # 창 크기 고정

        client = get_client()
        database = client[database_name]
        
        monitor = database["monitor"]
        result = database["result20"]

        
        #### table ####
        self.monitor_table_box = QGroupBox(window)
        self.monitor_table_box.setGeometry(QRect(670, 10, 380, 650))
        self.monitor_table_box.setTitle("22/21 비교")

        self.tableLayout = QVBoxLayout(self.monitor_table_box) # QVBoxLayout() 수직박스 레이아웃
        self.monitor_table = QTableWidget()
        self.tableLayout.addWidget(self.monitor_table)



        #### 도로명/노선번호/행선/차로 선택 메뉴 ####
        self.select_compare_id = QGroupBox(window)
        self.select_compare_id.setGeometry(QRect(10, 10, 650, 100))
        self.select_compare_id.setTitle("비교 기준 선택")
        
        self.select_compare_id_Vbox = QVBoxLayout(self.select_compare_id) # QVBoxLayout() 수직박스 레이아웃
        self.select_compare_id_Hbox1 = QHBoxLayout() # QHBoxLayout() 수평박스 레이아웃
        self.select_compare_id_Hbox2 = QHBoxLayout()
        self.select_compare_id_Vbox.addLayout(self.select_compare_id_Hbox1)
        self.select_compare_id_Vbox.addLayout(self.select_compare_id_Hbox2)
        #self.select_compare_id_Vbox.addStretch() # 윈도우 크기 조절에 따라 자동으로 늘려짐 .addStretch()
        
        # 1번째 줄 select_compare_id_Hbox1 - combobox, button
        self.lineid_combobox = QComboBox()
        self.roadname_combobox = QComboBox()
        self.heading_combobox = QComboBox()
        self.track_combobox = QComboBox()
        self.select_compare_id_Hbox1.addWidget(self.lineid_combobox)
        self.select_compare_id_Hbox1.addWidget(self.roadname_combobox)
        self.select_compare_id_Hbox1.addWidget(self.heading_combobox)
        self.select_compare_id_Hbox1.addWidget(self.track_combobox)

        lineid_list = monitor.find({"job_id": "2022년_서울시"}).distinct("line_id")
        self.lineid_combobox.addItems(lineid_list)


        # 2번째 줄 select_compare_id_Hbox2 - label, combobox
        self.select_compare_label = QLabel()
        self.monitorid_combobox = QComboBox()
        self.select_button = QPushButton("선택 완료") 
        self.select_compare_id_Hbox2.addWidget(self.select_compare_label)
        self.select_compare_id_Hbox2.addWidget(self.monitorid_combobox)
        self.select_compare_id_Hbox2.addStretch(1)
        self.select_compare_id_Hbox2.addWidget(self.select_button)
        self.select_compare_label.setText("monitor_id : ")
        self.select_compare_label.setAlignment(Qt.AlignLeft)
        self.select_compare_id_Hbox2.setStretchFactor(self.select_compare_label, 0.5)
        self.select_compare_id_Hbox2.setStretchFactor(self.monitorid_combobox, 2)
        self.select_compare_id_Hbox2.setStretchFactor(self.select_button, 1.5)
        
        
        #### 마지막 정보 박스 ####
        self.info_group = QGroupBox(window)
        self.info_group.setGeometry(QRect(10, 520, 650, 100))
        self.info_box = QGridLayout(self.info_group)
              
        self.compareid_label = QLabel()
        self.monitorid_label = QLabel()
        self.station_start_label = QLabel()
        self.station_end_label = QLabel()
        
        self.compareid_label.setText("비교 기준 : ")
        self.monitorid_label.setText("선택한 monitor_id : ")
        self.station_start_label.setText("- station_start : 0 m")
        self.station_end_label.setText("- station_end : 0 m")
        self.compareid_label.setAlignment(Qt.AlignLeft)
        self.monitorid_label.setAlignment(Qt.AlignLeft)
        self.station_start_label.setAlignment(Qt.AlignLeft)
        self.station_end_label.setAlignment(Qt.AlignLeft)

        self.info_box.addWidget(self.compareid_label, 0, 0, 1, 3)
        self.info_box.addWidget(self.monitorid_label, 1, 0, 1, 2) 
        self.info_box.addWidget(self.station_start_label, 2, 0, -1, 2) 
        self.info_box.addWidget(self.station_end_label, 3, 0, -1, 2)

        self.station2122title = QLabel()
        self.station21 = QLabel()
        self.station22 = QLabel()
        
        self.station2122title.setText("<< station(20m단위) ( 시작, 끝 ) >>")
        self.station22.setText("2022 : ( 0 , 0 )")
        self.station21.setText("2021 : ( 0 , 0 )")
        self.station2122title.setAlignment(Qt.AlignLeft)
        self.station22.setAlignment(Qt.AlignLeft)
        self.station21.setAlignment(Qt.AlignLeft)
        self.info_box.addWidget(self.station2122title, 1, 2)
        self.info_box.addWidget(self.station22, 2, 2)
        self.info_box.addWidget(self.station21, 3, 2)
        
        
        #### 그래프 ####
        self.showGraph = QGroupBox(window)
        self.showGraph.setGeometry(QRect(10, 110, 650, 400))
        self.showGraph.setTitle("그래프")
        self.graph_box = QHBoxLayout(self.showGraph)
              
        # 그래프layout
        self.fig = plt.Figure()
        self.canvas = FigureCanvas(self.fig)
        self.graph_box.addWidget(self.canvas)

        #### 최종 이미지, pdf 변환 버튼 ####
        # csv 저장 버튼
        self.pdf_save_button = QPushButton(window)
        self.pdf_save_button.setGeometry(QRect(485, 630, 80, 30))
        self.pdf_save_button.setText("csv변환")
        self.pdf_save_button.setDisabled(True) #최종버튼 클릭 후 버튼 활성화

        # 이미지 저장 버튼 
        self.png_save_button = QPushButton(window)
        self.png_save_button.setGeometry(QRect(575, 630, 80, 30))
        self.png_save_button.setText("PNG변환")
        self.png_save_button.setDisabled(True) #최종버튼 클릭 후 버튼 활성화



        client.close()
