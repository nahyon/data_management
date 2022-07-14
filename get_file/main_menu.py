import configparser
from unittest import result

import config 
import pymongo
from PySide6 import QtGui
from PySide6.QtCore import Qt
from PySide6.QtWidgets import *
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

# 한글 폰트 사용을 위해서 세팅
from matplotlib import font_manager, rc
font_path = r"C:\Users\alba3\Desktop\temp_graph\NanumGothic.ttf"
font = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font)

# csv저장
import pandas as pd  


from PySide6.QtWidgets import QApplication
from main_menu_ui import MainMenuUI


def returnfig(x,y):
    fig = plt.figure()
    a = plt.plot(x,y)
    return fig
class MainMenu(QMainWindow, MainMenuUI):
    def __init__(self):
        QMainWindow.__init__(self, None, Qt.Window)
        self.setupUi(self)
        
        #DB연결
        self.client = config.get_client()
        self.database = self.client[config.database_name] 

        # 콤보박스 변경될 때
        self.lineid_combobox.currentTextChanged.connect(self.updateRoadnameCombo)
        self.roadname_combobox.currentTextChanged.connect(self.updateHeadingCombo)
        self.heading_combobox.currentTextChanged.connect(self.updateTrackCombo)
        self.track_combobox.currentTextChanged.connect(self.find_monitorid)
        #self.monitorid_combobox.currentTextChanged.connect(self.update_info)
        
        
        # 최종 버튼 클릭 시        
        self.select_button.clicked.connect(self.show_graph) #그래프 보여주는 함수
        self.select_button.clicked.connect(self.update_info) #정보 박스 업데이트
        self.select_button.clicked.connect(self.update_table)

        self.updateHeadingCombo()
        self.updateRoadnameCombo()
        self.updateTrackCombo()
        self.find_monitorid()
        #self.update_info()
        

        self.pdf_save_button.clicked.connect(self.convert_csv)
        self.png_save_button.clicked.connect(self.png_save)
    
    def update_table(self) :  
        dict22 = {'22station': self.newstation22start, '22crack': [round(float(percent) ,2 ) for percent in self.newcrack_percent22], '22photo': self.newphoto22}
        dict21 = {'21crack': [round(float(percent) ,2 ) for percent in self.newcrack_percent21], '21photo': self.newphoto21, '21station': self.newstation21start}  

        df22 = pd.DataFrame(dict22)
        df21 = pd.DataFrame(dict21)
        # saving the dataframe 
        df = pd.concat([df22,df21],axis=1)
        
        col = len(df.keys()) #col개수 6 
        row = len(df.index)  #row개수
        
                
        # 테이블 채우기
        self.monitor_table.setRowCount(row) #len(df.index)
        self.monitor_table.setColumnCount(6) #len(df.keys())
        self.monitor_table.setHorizontalHeaderLabels(["22station", "crack", "photo", "crack", "photo", "21station"]) #df.keys()
        
        for r in range(row):
            for c in range(col):
                
                if str(df.iloc[r][c]) == "nan" :
                    self.monitor_table.setItem(r, c, QTableWidgetItem(""))
                    continue
                if c == 0 or c == 5 :
                    self.monitor_table.setItem(r, c, QTableWidgetItem(str(df.iloc[r][c].astype(np.int64))))
                    self.monitor_table.item(r, c).setBackground(QtGui.QColor(221, 221, 221))
                    continue
                item = QTableWidgetItem(str(df.iloc[r][c]))
                self.monitor_table.setItem(r, c, item)
                
                
        self.monitor_table.resizeColumnsToContents()    
        
    def updateRoadnameCombo(self) : # lineid -> 도로명 선택
        monitor = self.database["monitor"]
        self.roadname_combobox.clear()
        roadnames = monitor.find({"job_id": "2022년_서울시", "line_id" : self.lineid_combobox.currentText()}).distinct("road_name")
        if roadnames :
            self.roadname_combobox.addItems(roadnames)
        self.find_monitorid()
    
    def updateHeadingCombo(self): # lineid, roadname -> 상/하행 선택
        monitor = self.database["monitor"]
        self.heading_combobox.clear()
        headings = monitor.find({"job_id": "2022년_서울시", "line_id" :  self.lineid_combobox.currentText(), "road_name" : self.roadname_combobox.currentText()}).distinct("heading")
        if headings:
            self.heading_combobox.addItems(headings)
        self.find_monitorid() 

    def updateTrackCombo(self) : # lineid, roadname, heading -> 차로 선택
        monitor = self.database["monitor"]
        self.track_combobox.clear()
        tracks = monitor.find({"job_id": "2022년_서울시", "line_id" : self.lineid_combobox.currentText(), "road_name" : self.roadname_combobox.currentText(), "heading" : self.heading_combobox.currentText()}).distinct("track")
        for idx, value in enumerate(tracks) :
            tracks[idx] = value 
        if tracks :
            self.track_combobox.addItems(tracks)
        self.find_monitorid()
        

    def find_monitorid(self) :
        monitor = self.database["monitor"]
        self.monitorid_combobox.clear()
        lineid = self.lineid_combobox.currentText()
        heading = self.heading_combobox.currentText()
        road = self.roadname_combobox.currentText()
        track = self.track_combobox.currentText()
        monitor_list = monitor.find({"job_id": "2022년_서울시", "line_id" :lineid, "heading" : heading, "road_name" : road, "track" : track}).distinct("monitor_id")
        if monitor_list :
            self.monitorid_combobox.addItems(monitor_list)
        
    
    def update_info(self) :
        monitor = self.database["monitor"]
        result = self.database["result20"]
        monitor_id = self.monitorid_combobox.currentText()
        
        lineid = self.lineid_combobox.currentText()
        heading = self.heading_combobox.currentText()
        road = self.roadname_combobox.currentText()
        track = self.track_combobox.currentText()
        
        #print(road, lineid, heading, track)
        monitorid_info = list(monitor.find(
            {"job_id": "2022년_서울시", "monitor_id": monitor_id},
            {"job_id": 1,"monitor_id": 1, "compare_id" : 1,  "monitor_start_station": 1, "monitor_end_station":1}
        ))
        monitor_start_station = monitorid_info[0]['monitor_start_station']
        monitor_end_station = monitorid_info[0]['monitor_end_station']
        
        compare_id = monitorid_info[0]['compare_id']
        #print("compare_id : ", compare_id)
        #monitor_id = monitorid_info[0]['monitor_id']
        
        self.compareid_label.setText(f"비교 기준 : {road}({lineid})_{heading}_{track}차선")
        self.monitorid_label.setText(f"선택한 monitor_id : {monitor_id}")
        self.station_start_label.setText(f"- station_start : {monitor_start_station} m")
        self.station_end_label.setText(f"- station_end : {monitor_end_station} m")

        ###
        seoul22 = list(result.find(
            {"job_name": "2022년_서울시", "compare_id": compare_id},
            {"job_id": 1,"compare_id" : 1, "station": 1, "old_score":1}
        ).sort("station"))
        seoul21 = list(result.find(
            {"job_name": "2021년_서울시", "compare_id": compare_id},
            {"job_id": 1,"compare_id" : 1, "station": 1, "old_score":1}
        ).sort("station"))

        station22start =[]
        crack_percent22=[]
        for a_station in seoul22 :
            station22start.append(int(a_station['station']['start']))
            #station10end = a_station['station']['end'] 
            crack_percent22.append(float(a_station['old_score']['crack']))
        station21start =[]
        crack_percent21=[]
        for a_station in seoul21 :
            station21start.append(int(a_station['station']['start']))
            #station10end = a_station['station']['end']
            crack_percent21.append(float(a_station['old_score']['crack']))  


        # data slicing (monitor id에 따른 주어진 범위에 따라)
        newstation22start, newcrack_percent22, newstation21start, newcrack_percent21 = [], [], [], []
        for idx, value in enumerate(station22start) :
            if value > monitor_end_station : #대소 비교 등호 넣고 안넣고?
                break
            if monitor_start_station <= value :
                newstation22start.append(value)
                newcrack_percent22.append(crack_percent22[idx])
        
    
        for idx, value in enumerate(station21start) :
            if value > monitor_end_station :
                break
            if monitor_start_station <= value :
                newstation21start.append(value)
                newcrack_percent21.append(crack_percent21[idx])

        self.station21.setText(f"2021 : ( {int(newstation21start[0])} , {int(newstation21start[-1])} )") if len(newstation21start)!=0 else self.station21.setText(f"2021 : ( 0 , 0 )")
        self.station22.setText(f"2022 : ( {int(newstation22start[0])} , {int(newstation22start[-1])} )") if len(newstation22start)!=0 else self.station22.setText(f"2022 : ( 0 , 0 )")
                

        
    def show_graph(self) : #그래프 보여주는 함수
        
        monitor = self.database["monitor"]
        result = self.database["result20"]
        monitor_id = self.monitorid_combobox.currentText()
        lineid = self.lineid_combobox.currentText()
        heading = self.heading_combobox.currentText()
        road = self.roadname_combobox.currentText()
        track = self.track_combobox.currentText()
        #print(road, lineid, heading, track)
        
        # 선택한 monitor_id에 따른 시/종점 범위 설정
        monitorid_info = list(monitor.find(
            {"job_id": "2022년_서울시", "monitor_id": monitor_id},
            {"job_id": 1,"monitor_id": 1, "compare_id" : 1,  "monitor_start_station": 1, "monitor_end_station":1}
        ))
        print("monitor_info : ", monitorid_info)
        monitor_start_station = monitorid_info[0]['monitor_start_station']
        monitor_end_station = monitorid_info[0]['monitor_end_station']
        compare_id = monitorid_info[0]['compare_id']
        
        seoul22 = list(result.find(
            {"job_name": "2022년_서울시", "compare_id": compare_id},
            {"job_id": 1,"compare_id" : 1, "station": 1, "old_score":1,  "photo_surface":1},
        ).sort("station"))
        seoul21 = list(result.find(
            {"job_name": "2021년_서울시", "compare_id": compare_id},
            {"job_id": 1,"compare_id" : 1, "station": 1, "old_score":1, "photo_surface":1}
        ).sort("station"))

        station22start =[]
        crack_percent22=[]
        photo22 = []
        for a_station in seoul22 :
            station22start.append(int(a_station['station']['start']))
            crack_percent22.append(float(a_station['old_score']['crack']))
            photo = (a_station['photo_surface']['front'].split("_")[-1]).split(".")[0]
            photo22.append(int(photo[1:])/1000000)
        station21start =[]
        crack_percent21=[]
        photo21=[]
        for a_station in seoul21 :
            station21start.append(int(a_station['station']['start']))
            crack_percent21.append(float(a_station['old_score']['crack']))
            photo = (a_station['photo_surface']['front'].split("_")[-1]).split(".")[0]
            photo21.append(int(photo[1:])/1000000)

        # data slicing (monitor id에 따른 주어진 범위에 따라)
        self.newstation22start, self.newcrack_percent22, self.newstation21start, self.newcrack_percent21, self.newphoto21, self.newphoto22 = [], [], [], [], [], []
        for idx, value in enumerate(station22start) :
            if value > monitor_end_station : 
                break
            if monitor_start_station <= value :
                self.newstation22start.append(value)
                self.newcrack_percent22.append(crack_percent22[idx])
                self.newphoto22.append(photo22[idx])
                

        for idx, value in enumerate(station21start) :
            if value > monitor_end_station :
                break
            if monitor_start_station <= value :
                self.newstation21start.append(value)
                self.newcrack_percent21.append(crack_percent21[idx])
                self.newphoto21.append(photo21[idx])
        
        
        # data
        self.x1 = self.newstation22start
        self.y1 = self.newcrack_percent22
        self.x2 = self.newstation21start
        self.y2 = self.newcrack_percent21


        self.fig.clear()
        ax = self.fig.subplots()
        
        ax.plot(self.x1, self.y1, label="2022", color='red', linewidth=1.75)
        ax.plot(self.x2, self.y2, label="2021", color='green', linewidth=1.75)
        #ax.grid(True)
        
        ax.set_ylim([0, 100]) #y축 0~100으로고정
        ax.set_xticks(list((range(monitor_start_station, monitor_end_station+20, 40)))) #눈금
        
        
        ax.set_ylabel("crack_percent")
        ax.set_xlabel("start_station")
        plt.setp(ax.get_xticklabels(), rotation =90, fontsize =7)
        
        ax.set_title(monitor_id)
        ax.legend()
        #ax = self.fig.subplots_adjust(left=None, bottom=None, right=None, top=None,wspace=0, hspace=0) 
        self.canvas.draw()

        self.png_save_button.setEnabled(True) #이미지 저장 버튼 활성화
        self.pdf_save_button.setEnabled(True) #PDF저장 버튼 활성화
    def convert_dict21(self, old_dict21, start, end) :
        newdict21 = {}
        print(start, end)
        old_dict21_stations = old_dict21["21station"] #station모아둔 list

        
        start_idx = [i for i,x in enumerate(old_dict21_stations) if x == start] #대소비교로바꿔야할듯
        end_idx = [i for i,x in enumerate(old_dict21_stations) if x == end] #대소비교로바꿔야할듯 
        
        print(start_idx, end_idx)
        
    def convert_csv(self, ) :
        # dictionary of lists  
        dict22 = {'22station': self.newstation22start, '22crack': self.newcrack_percent22, '22photo': self.newphoto22}
        dict21 = {'21station': self.newstation21start, '21crack': self.newcrack_percent21, '21photo': self.newphoto21}  
        newdict21 = {}
        
        
        # 21년도 데이터를 22년도 station에 맞춰서 자르기 #
        startstation = self.newstation22start[0]
        endstation= self.newstation22start[-1]
        #print(startstation, endstation)
        newdict21 = self.convert_dict21(dict21, startstation, endstation)
        
        # for idx, value in enumerate(dict21) :
        #(idx, alue, dict21[value])
        #(0, 21station, [0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240])
        #(1, 21crack, [0.0, 0.0, 0.0, 22.444, 0.0, 0.0])
        #(2, 21photo, [1.7, 1.68, 1.66, 1.64, 1.62, 1.6, 1.58, 1.56, 1.54, 1.52, 1.5, 1.48])
        #for idx, value in enumerate(dict21) :
        #    print(idx)
        #    print(value)
        #    print(dict21[value])
        
        df22 = pd.DataFrame(dict22)
        df21 = pd.DataFrame(dict21)
        
        # saving the dataframe 
        #pd.concat([df22,newdict21],axis=1).to_csv(f"{self.monitorid_combobox.currentText()}.csv", index = False)
            
     

    def png_save(self) :
        monitor_id = self.monitorid_combobox.currentText()
        monitor = self.database["monitor"]
        # 선택한 monitor_id에 따른 시/종점 범위 설정
        monitorid_info = list(monitor.find(
            {"job_id": "2022년_서울시", "monitor_id": monitor_id},
            {"job_id": 1,"monitor_id": 1, "compare_id" : 1,  "monitor_start_station": 1, "monitor_end_station":1}
        ))
        print("monitor_info : ", monitorid_info)
        monitor_start_station = monitorid_info[0]['monitor_start_station']
        monitor_end_station = monitorid_info[0]['monitor_end_station']
        
        fig = plt.figure(figsize=(27.64,6.68)) # cm->inch ? (27.64/2.54,6.68/2.54)
        
        plt.plot(self.x1, self.y1, label="2022", color='red', linewidth=1.75)
        plt.plot(self.x2, self.y2, label="2021", color='green', linewidth=1.75)
        #ax.grid(True)
        
        plt.ylim([0, 100]) #y축 0~100으로고정
        plt.xticks(list((range(monitor_start_station, monitor_end_station+20, 40))),rotation=90) #눈금
        
        plt.ylabel("crack_percent")
        plt.xlabel("start_station")
        
        
        plt.title(monitor_id)
        plt.legend()
        
        fig.savefig(f"{self.monitorid_combobox.currentText()}.png", bbox_inches = 'tight')
        
        
  
if __name__ == '__main__':
    app = QApplication()
    window = MainMenu()
    window.show()
    app.exec()
