import configparser
from unittest import result
import config

import sys
import os
import pymongo
from PySide6.QtCore import Qt
from PySide6.QtWidgets import *
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from get_file.get_file_ui import GetFileUI

# 한글 폰트 사용을 위해서 세팅
from matplotlib import font_manager, rc
font_path = r"C:\Users\alba3\Desktop\temp_graph\NanumGothic.ttf"
font = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font)


# csv저장
import pandas as pd  
# pdf 저장
from itertools import islice


class GetFile(QDialog, GetFileUI): #GetFile(QMainWindow, GetFileUI):
    def __init__(self):
        QDialog.__init__(self, None, Qt.Dialog) #QMainWindow.__init__(self, None, Qt.Window)
        self.setupUi(self)
        
        #DB연결
        self.client = config.get_client()
        self.database = self.client[config.database_name] 
        
        # 콤보박스 변경될 때
        self.lineid_combobox.currentTextChanged.connect(self.updateRoadnameCombo)
        self.roadname_combobox.currentTextChanged.connect(self.updateHeadingCombo)
        self.roadname_combobox.currentTextChanged.connect(self.updateTrackCombo)
        self.heading_combobox.currentTextChanged.connect(self.updateTrackCombo)
        #self.track_combobox.currentTextChanged.connect(self.find_monitorid)
        #self.monitorid_combobox.currentTextChanged.connect(self.update_info)
        
        # [검색] 버튼 클릭 시        
        self.search_button.clicked.connect(self.update_monitorid) #정보 박스 업데이트

        self.updateHeadingCombo()
        self.updateRoadnameCombo()
        self.updateTrackCombo()
        #self.find_monitorid()
        #self.update_info()
        
        self.find_button.clicked.connect(self.select_save_path)

        self.csv_save_button.clicked.connect(self.csv_save)
        self.graph_save_button.clicked.connect(self.graph_save)
        self.pdf_save_button.clicked.connect(self.pdf_save)
        

    def select_save_path(self):
        report_path = QFileDialog.getExistingDirectory()
        if report_path:
            self.report_path.setText(report_path)
            self.csv_save_button.setEnabled(True) #csv 저장 버튼 활성화
            self.graph_save_button.setEnabled(True) #그래프 저장 버튼 활성화
        else:
            self.csv_save_button.setDisabled(True) #csv 저장 버튼 활성화
            self.graph_save_button.setDisabled(True) #그래프 저장 버튼 활성화   
        
    def updateRoadnameCombo(self) : # lineid -> 도로명 선택
        monitor = self.database["monitor"]
        self.roadname_combobox.clear()
        roadnames = ['--도로명--', ]
        roadnames += monitor.find({"job_id": "2022년_서울시", "line_id" : self.lineid_combobox.currentText()}).distinct("road_name")
        if roadnames :
            self.roadname_combobox.addItems(roadnames)
        
    
    def updateHeadingCombo(self): # lineid, roadname -> 상/하행 선택
        monitor = self.database["monitor"]
        self.heading_combobox.clear()
        
        if self.track_combobox.currentIndex() != 0 :
            headings = ['--행선--', ]
            headings += monitor.find({"job_id": "2022년_서울시", "line_id" :  self.lineid_combobox.currentText(), "road_name" : self.roadname_combobox.currentText(), "track": self.track_combobox.currentText()}).distinct("heading")
        else :
            headings = ['--행선--', '상행', '하행']
        if headings:
            self.heading_combobox.addItems(headings)
         

    def updateTrackCombo(self) : # lineid, roadname, heading -> 차로 선택
        monitor = self.database["monitor"]
        self.track_combobox.clear()
        
        if self.heading_combobox.currentIndex() == 0 : # lineid, roadname으로 
            tracks = ['--차로--', ]
            tracks += monitor.find({"job_id": "2022년_서울시", "line_id" : self.lineid_combobox.currentText(), "road_name" : self.roadname_combobox.currentText()}).distinct("track")
        else : 
            tracks = ['--차로--', ]
            tracks += monitor.find({"job_id": "2022년_서울시", "line_id" : self.lineid_combobox.currentText(), "road_name" : self.roadname_combobox.currentText(), "heading" : self.heading_combobox.currentText()}).distinct("track")
        for idx, value in enumerate(tracks) :
            tracks[idx] = value 
        if tracks :
            self.track_combobox.addItems(tracks)
        
    def update_monitorid(self) :
        monitor = self.database["monitor"]
        
        #self.monitor_table.clear()
        
        lineid = self.lineid_combobox.currentText() #필수
        heading = self.heading_combobox.currentText()
        road = self.roadname_combobox.currentText()
        track = self.track_combobox.currentText()
        
        heading_idx = self.heading_combobox.currentIndex()
        road_idx = self.roadname_combobox.currentIndex()
        track_idx = self.track_combobox.currentIndex()
        print(heading_idx ,road_idx ,track_idx)
        #print((heading_idx ,road_idx ,track_idx).count(0))
        self.monitor_list=[]
        if (heading_idx ,road_idx ,track_idx).count(0) == 3 : #3개 다 선택안함 (0, 0, 0)=False
            self.monitor_list = list(monitor.find(
                    {"job_id": "2022년_서울시", "line_id" :lineid,},
                    {"monitor_id":1, "line_id" :  1, "road_name":1, "heading":1 , "track":1, "monitor_start_station": 1, "monitor_end_station":1, "compare_id" : 1}
                ))
            self.compareid_list = monitor.find({"job_id": "2022년_서울시", "line_id" :lineid,}).distinct('compare_id')
        
        elif all((heading_idx ,road_idx ,track_idx)) : #3개 다 선택함 (0아님, 0아님, 0아님) = True
            self.monitor_list = list(monitor.find(
                    {"job_id": "2022년_서울시", "line_id" :lineid, "heading" : heading, "road_name" : road, "track" : track},
                    {"monitor_id":1, "line_id" :  1, "road_name":1, "heading":1 , "track":1, "monitor_start_station": 1, "monitor_end_station":1, "compare_id" : 1}
                ))
            self.compareid_list = monitor.find({"job_id": "2022년_서울시", "line_id" :lineid, "heading" : heading, "road_name" : road, "track" : track}).distinct('compare_id')
        
        elif (heading_idx ,road_idx ,track_idx).count(0) == 2 : #1개만 선택 (2개가 0인경우)
            if heading_idx != 0 : #행선 선택 (heading0아님, 0, 0)
                self.monitor_list = list(monitor.find(
                    {"job_id": "2022년_서울시", "line_id" :lineid, "heading" : heading},
                    {"monitor_id":1, "line_id" :  1, "road_name":1, "heading":1 , "track":1, "monitor_start_station": 1, "monitor_end_station":1, "compare_id" : 1}
                ))
                self.compareid_list = monitor.find({"job_id": "2022년_서울시", "line_id" :lineid, "heading" : heading}).distinct('compare_id')
                
                
            elif road_idx != 0 : #도로명 선택 (0, roadname0아님, 0)
                self.monitor_list = list(monitor.find(
                    {"job_id": "2022년_서울시", "line_id" :lineid, "road_name" : road},
                    {"monitor_id":1, "line_id" :  1, "road_name":1, "heading":1 , "track":1, "monitor_start_station": 1, "monitor_end_station":1, "compare_id" : 1}
                ))
                self.compareid_list = monitor.find({"job_id": "2022년_서울시", "line_id" :lineid, "road_name" : road}).distinct('compare_id')
                
            else : # 차로 선택 (0, 0, track0아님)
                self.monitor_list = list(monitor.find(
                    {"job_id": "2022년_서울시", "line_id" :lineid, "track" : track},
                    {"monitor_id":1, "line_id" :  1, "road_name":1, "heading":1 , "track":1, "monitor_start_station": 1, "monitor_end_station":1, "compare_id" : 1}
                ))
                self.compareid_list = monitor.find({"job_id": "2022년_서울시", "line_id" :lineid, "track" : track}).distinct('compare_id')
                
        else : #2개 선택 (1개만 0)
            if heading_idx == 0 : #도로명, 차로 선택
                self.monitor_list = list(monitor.find(
                    {"job_id": "2022년_서울시", "line_id" :lineid, "road_name" : road, "track" : track},
                    {"monitor_id":1, "line_id" :  1, "road_name":1, "heading":1 , "track":1, "monitor_start_station": 1, "monitor_end_station":1, "compare_id" : 1}
                ))
                self.compareid_list = monitor.find({"job_id": "2022년_서울시", "line_id" :lineid, "road_name" : road, "track" : track}).distinct('compare_id')
            elif road_idx == 0 : #행선, 차로 선택
                self.monitor_list = list(monitor.find(
                    {"job_id": "2022년_서울시", "line_id" :lineid, "heading" : heading, "track" : track},
                    {"monitor_id":1, "line_id" :  1, "road_name":1, "heading":1 , "track":1, "monitor_start_station": 1, "monitor_end_station":1, "compare_id" : 1}
                ))
                self.compareid_list = monitor.find({"job_id": "2022년_서울시", "line_id" :lineid, "heading" : heading, "track" : track}).distinct('compare_id')
            else : # 행선, 도로명 선택
                self.monitor_list = list(monitor.find(
                    {"job_id": "2022년_서울시", "line_id" :lineid, "road_name" : road, "heading" : heading},
                    {"monitor_id":1, "line_id" :  1, "road_name":1, "heading":1 , "track":1, "monitor_start_station": 1, "monitor_end_station":1, "compare_id" : 1}
                ))
                self.compareid_list = monitor.find({"job_id": "2022년_서울시", "line_id" :lineid, "road_name" : road, "heading" : heading}).distinct('compare_id')     
        
        
        # 테이블 채우기
        self.monitor_table.setRowCount(len(self.monitor_list))
        self.monitor_table.setColumnCount(7)
        self.monitor_table.setHorizontalHeaderLabels(["monitor_id", "노선번호", "도로명", "행선", "차선", "STA시점", "STA종점"])
        
        for index, monitor_item in enumerate(self.monitor_list):
            #print(index , monitor_item)
            #index = self.monitor_table.rowCount()
            #self.monitor_table.insertRow(index)
            self.monitor_table.setItem(index, 0, QTableWidgetItem(monitor_item["monitor_id"]))
            self.monitor_table.setItem(index, 1, QTableWidgetItem(str(monitor_item["line_id"])))
            self.monitor_table.setItem(index, 2, QTableWidgetItem(monitor_item["road_name"]))
            self.monitor_table.setItem(index, 3, QTableWidgetItem(monitor_item["heading"]))
            self.monitor_table.setItem(index, 4, QTableWidgetItem(str(monitor_item["track"])))
            self.monitor_table.setItem(index, 5, QTableWidgetItem(str(float(monitor_item["monitor_start_station"])/ 1000)))
            self.monitor_table.setItem(index, 6, QTableWidgetItem(str(float(monitor_item["monitor_end_station"])/ 1000)))
        
        self.monitor_table.resizeColumnsToContents()
        #self.csv_save_button.setEnabled(True) #csv 저장 버튼 활성화
        #self.graph_save_button.setEnabled(True) #그래프 저장 버튼 활성화
        self.pdf_save_button.setEnabled(True) #pdf변환 버튼 활성화 
        self.find_button.setEnabled(True)

    
        self.update_info()
    
    # for a_monitor in self.monitor_list ->
    def update_info_one(self, a_monitor) : #monitorid 하나에 대한 정보 업데이트(시/종점, crack, photo)
        result = self.database["result20"]
        
        lineid = self.lineid_combobox.currentText()
        heading = self.heading_combobox.currentText()
        road = self.roadname_combobox.currentText()
        track = self.track_combobox.currentText()
        
        # 하나의 monitorid에 대한 시/종점 
        monitorid = a_monitor['monitor_id']
        compareid = a_monitor['compare_id']
        monitor_start_station = a_monitor['monitor_start_station']
        monitor_end_station = a_monitor['monitor_end_station']
        
        ###
        seoul22 = list(result.find(
            {"job_name": "2022년_서울시", "compare_id": compareid},
            {"job_id": 1,"compare_id" : 1, "station": 1, "old_score":1,  "photo_surface":1},
        ).sort("station"))
        seoul21 = list(result.find(
            {"job_name": "2021년_서울시", "compare_id": compareid},
            {"job_id": 1,"compare_id" : 1, "station": 1, "old_score":1, "photo_surface":1}
        ).sort("station"))

        station22start, crack_percent22, photo22 =[], [], []
        for a_station in seoul22 :
            station22start.append(int(a_station['station']['start']))
            crack_percent22.append(float(a_station['old_score']['crack']))
            photo = (a_station['photo_surface']['surface1'].split("_")[-1]).split(".")[0]
            photo22.append(int(photo[1:])/1000000)
        station21start, crack_percent21, photo21 =[], [], []
        for a_station in seoul21 :
            station21start.append(int(a_station['station']['start']))
            crack_percent21.append(float(a_station['old_score']['crack']))
            photo = (a_station['photo_surface']['surface1'].split("_")[-1]).split(".")[0]
            photo21.append(int(photo[1:])/1000000)

        # data slicing (monitor id에 따른 주어진 범위에 따라)
        newstation22start, newcrack_percent22, newstation21start, newcrack_percent21, newphoto21, newphoto22 = [], [], [], [], [], []
        for idx, value in enumerate(station22start) :
            if value > monitor_end_station : 
                break
            if monitor_start_station <= value :
                newstation22start.append(value)
                newcrack_percent22.append(crack_percent22[idx])
                newphoto22.append(photo22[idx])
    
        for idx, value in enumerate(station21start) :
            if value > monitor_end_station :
                break
            if monitor_start_station <= value :
                newstation21start.append(value)
                newcrack_percent21.append(crack_percent21[idx])
                newphoto21.append(photo21[idx])
        
        return {"newstation22start" : newstation22start, "newcrack_percent22": newcrack_percent22, "newphoto22" : newphoto22,
                "newstation21start" : newstation21start, "newcrack_percent21": newcrack_percent21, "newphoto21" : newphoto21,
                "monitor_start_station": monitor_start_station, "monitor_end_station":monitor_end_station}    
    
    def update_info(self) :
        self.monitorid_dict = {}
        for a_monitor in self.monitor_list :
            monitorid = a_monitor['monitor_id']
            self.monitorid_dict[monitorid] = self.update_info_one(a_monitor)
        print(self.monitorid_dict.keys())

    def one_csv_save(self, one_monitorid_dict, monitorid) :
        # dictionary of lists  
        dict22 = {'22station': one_monitorid_dict["newstation22start"], '22crack': one_monitorid_dict["newcrack_percent22"], '22photo': one_monitorid_dict["newphoto22"]}
        dict21 = {'21station': one_monitorid_dict["newstation21start"], '21crack': one_monitorid_dict["newcrack_percent21"], '21photo': one_monitorid_dict["newphoto21"]}

        df22 = pd.DataFrame(dict22)
        df21 = pd.DataFrame(dict21)
        # saving the dataframe 
        return pd.concat([df22,df21],axis=1)

        
    def one_png_save(self, one_monitorid_dict, monitorid) :

        fig = plt.figure(figsize=(27.64/2.54,6.68/2.54)) # cm->inch ? (27.64/2.54,6.68/2.54) (27.64,6.68)
        #폰트 사이즈
        plt.rcdefaults()
        rc('font', family=font)
        params = {'axes.labelsize': 25,'axes.titlesize':30, 'font.size': 20, 'legend.fontsize': 20, 'xtick.labelsize': 18, 'ytick.labelsize': 20}
        plt.rcParams.update(params)
        
        x1= one_monitorid_dict["newstation22start"]
        y1= one_monitorid_dict["newcrack_percent22"]
        x2= one_monitorid_dict["newstation21start"]
        y2= one_monitorid_dict["newcrack_percent21"]
        
        monitor_start_station = one_monitorid_dict["monitor_start_station"]
        monitor_end_station = one_monitorid_dict["monitor_end_station"]
        
        plt.plot(x1, y1, label="2022", color='red', linewidth=1.75)
        plt.plot(x2, y2, label="2021", color='green', linewidth=1.75)
        #ax.grid(True)  
        
        plt.ylim([0, 100]) #y축 0~100으로고정
        plt.xticks(list((range(monitor_start_station, monitor_end_station+20, 100))),rotation=90) #눈금
        
        plt.ylabel("crack_percent")
        plt.xlabel("start_station")
        
        plt.title(monitorid)
        plt.legend()
        
        #fig.savefig(f"{monitorid}.png", bbox_inches = 'tight')
        return fig
    
    def csv_save(self) :
        cnt = 0
        for monitorid in self.monitorid_dict.keys() :
            monitorid_csv = self.one_csv_save(self.monitorid_dict[monitorid], monitorid)
            monitorid_csv.to_csv(os.path.join(self.report_path.text(), f"{monitorid}.csv"), index = False)
            cnt+=1
        QMessageBox.about(self, "csv파일 총", f"{cnt}개 저장 완료")
    
    def graph_save(self) :
        cnt = 0
        for monitorid in self.monitorid_dict.keys() :
            monitorid_fig = self.one_png_save(self.monitorid_dict[monitorid], monitorid)
            monitorid_fig.savefig(os.path.join(self.report_path.text(), f"{monitorid}.png"), bbox_inches = 'tight')
            cnt+=1
        QMessageBox.about(self, "그래프 이미지 총", f"{cnt}개 저장 완료")
    
    def pdf_save(self) :
        filename = self.lineid_combobox.currentText() #lineid 필수
        for combo in [self.heading_combobox,  self.roadname_combobox, self.track_combobox] :
            if combo.currentIndex() != 0 :
                filename += combo.currentText()
        filename += ".pdf"
        pdfsave  = PdfPages(filename)
        cnt = 0
        for monitorid in self.monitorid_dict.keys() :
            monitorid_fig = self.one_png_save(self.monitorid_dict[monitorid], monitorid)
            pdfsave.savefig(monitorid_fig, bbox_inches = 'tight')
            cnt+=1
        pdfsave.close()
        QMessageBox.about(self, f"PDF 생성완료 - {filename} (csv파일 총{cnt}개)")
    
    def pdf_save2(self) :
        #한페이지에 그래프 6개씩
        filename = "test.pdf"
        pdf = PdfPages(filename)
        figs = plt.figure()
        cnt = 0
        for monitorid_dict6 in self.chunks(self.monitorid_dict, 6):
            #print(type(monitorid_dict6), print(len(monitorid_dict6)))
            plot_num = 411
            fig = plt.figure(figsize=(27.64/2.54,6.68/2.54) ) 
            for idx, monitor_id in enumerate(monitorid_dict6) :
                monitorid = monitorid_dict6[monitor_id]
                #print("idx : ", idx, "  value : ", value)
                #print("dict[value] : ", monitorid_dict6[value])
                x1= monitorid["newstation22start"]
                y1= monitorid["newcrack_percent22"]
                x2= monitorid["newstation21start"]
                y2= monitorid["newcrack_percent21"]
                monitor_start_station = monitorid["monitor_start_station"]
                monitor_end_station = monitorid["monitor_end_station"]
                
                #plt.subplots(plot_num)
                ax10 = fig.add_subplot(4,1,idx+1)
                plt.plot(x1, y1, label="2022", color='red', linewidth=1.75)
                plt.plot(x2, y2, label="2021", color='green', linewidth=1.75)
                #ax.grid(True)  
                
                plt.ylim([0, 100]) #y축 0~100으로고정
                plt.xticks(list((range(monitor_start_station, monitor_end_station+20, 40))),rotation=90) #눈금
                
                plt.ylabel("crack_percent")
                plt.xlabel("start_station")
                
                #폰트 사이즈
                #plt.rcdefaults()
                #rc('font', family=font)
                #params = {'axes.labelsize': 25,'axes.titlesize':30, 'font.size': 20, 'legend.fontsize': 20, 'xtick.labelsize': 18, 'ytick.labelsize': 20}
                #plt.rcParams.update(params)
                plt.rcParams.update({'font.size': 8})
                
                plt.title(monitor_id)
                plt.legend()
                
                plot_num += 1
                cnt+=1
            
            
            pdf.savefig(fig) #페이지 하나 저장
        pdf.close()
        print("그래프", cnt, "개 변환")

    def chunks(self, data, SIZE=6): #dictionary를 6개씩 잘라서 리스트로 변환 [{}, {}, {}, {}, {} ,{}]
        it = iter(data)
        for i in range(0, len(data), SIZE):
            yield { k: data[k] for k in islice(it, SIZE)}
       
        