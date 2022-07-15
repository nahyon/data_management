from PySide6 import QtGui
from PySide6.QtCore import Qt
from PySide6.QtWidgets import *
from matplotlib import pyplot as plt

import config 
import numpy as np
import pandas as pd # csv저장

# 한글 폰트 사용을 위해서 세팅
from matplotlib import font_manager, rc
font_path = r"C:\Users\alba3\Desktop\temp_graph\NanumGothic.ttf"
font = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font)

from main_menu.main_menu_ui import MainMenuUI
from add_monitor.add_monitor import AddStatus # 과업 현황 입력
from view_monitor.view_monitor import ViewMonitor # 과업 현황 보기
from add_result.add_result_seoul import AddResultSeoul # 분석보고서 csv업로드
#from get_assess_report.get_assess_report_seoul import GetAssessReportSeoul # 변환보고서 추출
from get_file.get_file import GetFile #그래프 추출


class MainMenu(QMainWindow, MainMenuUI):
    def __init__(self):
        QMainWindow.__init__(self, None, Qt.Window)
        self.setupUi(self)
        
        #DB연결
        self.client = config.get_client()
        self.database = self.client[config.database_name] 

        ###############################버튼 연결###############################
        self.job_status_add_button.clicked.connect(self.open_add_status) #과업 현황 입력
        self.job_status_button.clicked.connect(self.open_job_status) # 과업 현황 보기
        self.result_seoul_add_button.clicked.connect(self.open_add_result_seoul) # 분석보고서 csv업로드
        #self.result_seoul20_add_button.clicked.connect(self.open_add_result_seoul20)
        self.get_file_button.clicked.connect(self.open_get_file)
        
        
        ########################################################################





        # 콤보박스 변경될 때
        self.lineid_combobox.currentTextChanged.connect(self.updateRoadnameCombo)
        self.roadname_combobox.currentTextChanged.connect(self.updateHeadingCombo)
        self.heading_combobox.currentTextChanged.connect(self.updateTrackCombo)
        self.track_combobox.currentTextChanged.connect(self.find_monitorid)
        #self.monitorid_combobox.currentTextChanged.connect(self.update_info)
        
        
        # 최종 버튼 클릭 시     
        self.select_button.clicked.connect(self.update_info) #정보 업데이트 (df까지) (-> show graph&table , 버튼 활성화) 

        self.pdf_save_button.clicked.connect(self.convert_csv)
        self.png_save_button.clicked.connect(self.png_save)
        
        self.updateHeadingCombo()
        self.updateRoadnameCombo()
        self.updateTrackCombo()
        self.find_monitorid()
        
        self.update_monitor()
    

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
        self.monitor_id = self.monitorid_combobox.currentText()
        
        lineid = self.lineid_combobox.currentText()
        heading = self.heading_combobox.currentText()
        road = self.roadname_combobox.currentText()
        track = self.track_combobox.currentText()
        
        #print(road, lineid, heading, track)
        monitorid_info = list(monitor.find(
            {"job_id": "2022년_서울시", "monitor_id": self.monitor_id},
            {"job_id": 1,"monitor_id": 1, "compare_id" : 1,  "monitor_start_station": 1, "monitor_end_station":1}
        ))
        self.monitor_start_station = monitorid_info[0]['monitor_start_station']
        self.monitor_end_station = monitorid_info[0]['monitor_end_station']
        
        compare_id = monitorid_info[0]['compare_id']
        #print("compare_id : ", compare_id)
        #monitor_id = monitorid_info[0]['monitor_id']

        # 22년, 21년 정보 (result)
        seoul22 = list(result.find(
            {"job_name": "2022년_서울시", "compare_id": compare_id},
            {"job_id": 1,"compare_id" : 1, "station": 1, "old_score":1,  "photo_surface":1},
        ).sort("station"))
        seoul21 = list(result.find(
            {"job_name": "2021년_서울시", "compare_id": compare_id},
            {"job_id": 1,"compare_id" : 1, "station": 1, "old_score":1, "photo_surface":1}
        ).sort("station"))

        station22start, crack_percent22, photo22 =[], [], []
        for a_station in seoul22 :
            station22start.append(int(a_station['station']['start']))
            crack_percent22.append(float(a_station['old_score']['crack']))
            #photo = (a_station['photo_surface']['front'].split("_")[-1]).split(".")[0]
            #photo22.append(int(photo[1:])/1000000)
            photo = (a_station['photo_surface']['front'])
            photo22.append(photo)
        station21start, crack_percent21, photo21 =[], [], []
        for a_station in seoul21 :
            station21start.append(int(a_station['station']['start']))
            crack_percent21.append(float(a_station['old_score']['crack']))
            #photo = (a_station['photo_surface']['front'].split("_")[-1]).split(".")[0]
            #photo21.append(int(photo[1:])/1000000)
            photo = (a_station['photo_surface']['front'])
            photo21.append(photo)

        # data slicing (monitor id에 따른 주어진 범위에 따라)
        self.newstation22start, self.newcrack_percent22, self.newstation21start, self.newcrack_percent21, self.newphoto21, self.newphoto22 = [], [], [], [], [], []
        for idx, value in enumerate(station22start) :
            if value > self.monitor_end_station : 
                break
            if self.monitor_start_station <= value :
                self.newstation22start.append(value)
                self.newcrack_percent22.append(crack_percent22[idx])
                self.newphoto22.append(photo22[idx])
        for idx, value in enumerate(station21start) :
            if value > self.monitor_end_station :
                break
            if self.monitor_start_station <= value :
                self.newstation21start.append(value)
                self.newcrack_percent21.append(crack_percent21[idx])
                self.newphoto21.append(photo21[idx])
        
        # 최종 데이터프레임 만들기
        self.make_df() 
        
        ## 정보 박스 업데이트
        self.compareid_label.setText(f"비교 기준 : {road}({lineid})_{heading}_{track}차선")
        self.monitorid_label.setText(f"선택한 monitor_id : {self.monitor_id}")
        self.station_start_label.setText(f"- station_start : {self.monitor_start_station} m")
        self.station_end_label.setText(f"- station_end : {self.monitor_end_station} m")        
        self.station21.setText(f"2021 : ( {int(self.newstation21start[0])} , {int(self.newstation21start[-1])} )") if len(self.newstation21start)!=0 else self.station21.setText(f"2021 : ( 0 , 0 )")
        self.station22.setText(f"2022 : ( {int(self.newstation22start[0])} , {int(self.newstation22start[-1])} )") if len(self.newstation22start)!=0 else self.station22.setText(f"2022 : ( 0 , 0 )")
        
        self.show_graph() # 그래프 보여주는 함수
        self.show_table() # 표 보여주는 함수
       
        self.png_save_button.setEnabled(True) #이미지 저장 버튼 활성화
        self.pdf_save_button.setEnabled(True) #PDF저장 버튼 활성화
        
    def make_df(self) :
        dict22 = {'22station': self.newstation22start, '22crack': [round(float(percent) ,2 ) for percent in self.newcrack_percent22], '22photo': self.newphoto22}
        dict21 = {'21station': self.newstation21start, '21crack': [round(float(percent) ,2 ) for percent in self.newcrack_percent21], '21photo': self.newphoto21}  

        # 21년도 데이터를 22년도 station에 맞춰서 자르기 #
        startstation = self.newstation22start[0]
        endstation= self.newstation22start[-1]
        #print(startstation, endstation)
        #newdict21 = self.convert_dict21(dict21, startstation, endstation)

        df22 = pd.DataFrame(dict22)
        df21 = pd.DataFrame(dict21) #(newdict21)
        self.df = pd.merge(df22, df21, left_on='22station', right_on='21station', how='left')
        
        # 필요없는 컬럼 drop
        self.df.drop(['21photo', '21station'], axis=1, inplace=True)
        #rename
        self.df = self.df.rename(columns={'22station': 'station', '22photo': 'photo'})
        #컬럼 순서 변경
        self.df = self.df[['station', '21crack', '22crack', 'photo']]   


    
    def show_table(self) :  
       
        col = len(self.df.keys()) #col개수 4 
        row = len(self.df.index)  #row개수
        
                
        # 테이블 채우기
        self.monitor_table.setRowCount(row) #len(df.index)
        self.monitor_table.setColumnCount(col) #len(df.keys())
        self.monitor_table.setHorizontalHeaderLabels(self.df.keys()) #df.keys()
        
        for r in range(row):
            for c in range(col):
                
                if str(self.df.iloc[r][c]) == "nan" :
                    self.monitor_table.setItem(r, c, QTableWidgetItem(""))
                    continue
                if c == 0:
                    self.monitor_table.setItem(r, c, QTableWidgetItem(str(self.df.iloc[r][c].astype(np.int64))))
                    self.monitor_table.item(r, c).setBackground(QtGui.QColor(208, 206, 206))
                    continue                  
                item = QTableWidgetItem(str(self.df.iloc[r][c]))
                self.monitor_table.setItem(r, c, item)
                if c == 3 :
                    self.monitor_table.item(r, c).setBackground(QtGui.QColor(226, 239, 218)) # (226, 239, 218)  연회색(234, 234, 234)
        self.monitor_table.resizeColumnsToContents()     
        

    def show_graph(self) : #그래프 보여주는 함수
        plt.rcdefaults()
        rc('font', family=font)
        #fig = plt.figure(figsize=(27.64/2.54,6.68/2.54)) 
        # data
        x1 = self.newstation22start
        y1 = self.newcrack_percent22
        x2 = self.newstation21start
        y2 = self.newcrack_percent21
        
        self.fig.clear()
        ax = self.fig.subplots()
        
        ax.plot(x1, y1, label="2022", color='red', linewidth=1.5)
        ax.plot(x2, y2, label="2021", color='green', linewidth=1.5)
        #ax.grid(True)
        
        ax.set_ylim([0, 100]) #y축 0~100으로고정
        interval = 200 if self.monitor_end_station - self.monitor_start_station >=7000 else 100
        ax.set_xticks(list((range(self.monitor_start_station, self.monitor_end_station+20, interval)))) #눈금
        
        
        ax.set_ylabel("crack_percent")
        ax.set_xlabel("start_station")

        plt.setp(ax.get_xticklabels(), rotation =90, fontsize =7)
        ax.set_title(self.monitor_id)
        ax.legend()
        #ax = self.fig.subplots_adjust(left=None, bottom=None, right=None, top=None,wspace=0, hspace=0)
        self.canvas.draw()



    def convert_csv(self, ) :
        self.df.to_csv(f"{self.monitorid_combobox.currentText()}.csv", index = False)
    

    def png_save(self) :
        
        fig = plt.figure(figsize=(27.64,6.68)) # cm->inch ? (27.64/2.54,6.68/2.54) (27.64,6.68)
        #폰트 사이즈
        plt.rcdefaults()
        rc('font', family=font)
        params = {'axes.labelsize': 25,'axes.titlesize':30, 'font.size': 20, 'legend.fontsize': 20, 'xtick.labelsize': 18, 'ytick.labelsize': 20}
        plt.rcParams.update(params)
        
        # data
        x1 = self.newstation22start
        y1 = self.newcrack_percent22
        x2 = self.newstation21start
        y2 = self.newcrack_percent21
        plt.plot(x1, y1, label="2022", color='red', linewidth=1.75)
        plt.plot(x2, y2, label="2021", color='green', linewidth=1.75)
        #ax.grid(True)
        
        plt.ylim([0, 100]) #y축 0~100으로고정
        interval = 200 if self.monitor_end_station - self.monitor_start_station >=7000 else 100
        plt.xticks(list((range(self.monitor_start_station, self.monitor_end_station+20, interval))),rotation=90) #눈금
        
        plt.ylabel("crack_percent")
        plt.xlabel("start_station")
        
        
        plt.title(self.monitor_id)
        plt.legend()
        

        fig.savefig(f"{self.monitorid_combobox.currentText()}.png", bbox_inches = 'tight')
    

        
    ## 현황 메뉴 ## #####################################################
    # 과업 현황 추가 [과업 현황 입력]
    def open_add_status(self):
        dialog = AddStatus("2022년_서울시")
        dialog.exec()
        self.update_monitor() #조사 개소, 연장, 결과연장 칸 업데이트

    # 과업 현황 보기 [과업 현황 보기]
    def open_job_status(self):
        dialog = ViewMonitor("2022년_서울시")
        dialog.exec()

    
    ## 결과파일 메뉴 ## #####################################################
    # [분석보고서 csv업로드] -> result, result20테이블
    def open_add_result_seoul(self): 
        dialog = AddResultSeoul("2022년_서울시")
        dialog.exec()
        self.update_monitor() 

    # [변환보고서 추출]
    def open_assess_report_seoul(self):
        pass
    # [그래프 추출]
    def open_get_file(self):
        dialog = GetFile()
        dialog.exec()
    
    # 과업 정보 업데이트
    def update_monitor(self):
        
        # monitor 테이블
        monitor = self.database["monitor"]
        query_result = monitor.aggregate(
            [
                {"$match": {"job_id": "2022년_서울시"}},
                {"$group": {
                    "_id": "$job_id",
                    "length": {"$sum": {"$subtract": ["$monitor_end_station", "$monitor_start_station"]}},
                    "count": {"$sum": 1}
                }}
            ]
        )
        monitor_result = {"count": 0, "length": 0}
        for x in query_result:
            monitor_result = x
            break
        self.job_monitor_count.setText(f"  조사 개소: {monitor_result['count']} 개소")
        self.job_monitor_length.setText(f"  조사 연장: {monitor_result['length'] / 1000}km")
        
        # result 테이블
        result = self.database["result"]
        query_result = result.aggregate(
            [
                {"$match": {"job_name": "2022년_서울시"}},
                {"$group": {
                    "_id": "job_name",
                    "count": {"$sum": 1}
                }}
            ]
        )
        result = {"count": 0}
        for x in query_result:
            result = x
            break
        self.job_result_length.setText(f"결과 연장: {result['count'] / 100}km")
