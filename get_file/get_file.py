import configparser
import json
from unittest import result
import config

import sys
import os
import openpyxl
from PySide6.QtCore import Qt
from PySide6.QtWidgets import *
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from get_file.get_file_ui import GetFileUI

# 한글 폰트 사용을 위해서 세팅
from matplotlib import font_manager, rc
#font_path = r"C:\Users\alba3\Desktop\seoul_data_management\NanumGothic.ttf"
font_path = os.path.join( os.getcwd(), "NanumGothic.ttf")
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
        self.report_save_button.clicked.connect(self.report_save)
        

    def select_save_path(self):
        report_path = QFileDialog.getExistingDirectory()
        if report_path:
            self.report_path.setText(report_path)
            self.pdf_save_button.setEnabled(True) #pdf 저장 버튼 활성화
            self.csv_save_button.setEnabled(True) #csv 저장 버튼 활성화
            self.graph_save_button.setEnabled(True) #그래프 저장 버튼 활성화
            self.report_save_button.setEnabled(True) 

        else:
            self.pdf_save_button.setDisabled(True)
            self.csv_save_button.setDisabled(True) #csv 저장 버튼 활성화
            self.graph_save_button.setDisabled(True) #그래프 저장 버튼 활성화  
            self.report_save_button.setDisabled(True)  

        
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
        #print(heading_idx ,road_idx ,track_idx)
        #print((heading_idx ,road_idx ,track_idx).count(0))
        self.monitor_list=[]
        if (heading_idx ,road_idx ,track_idx).count(0) == 3 : #3개 다 선택안함 (0, 0, 0)=False
            self.monitor_list = list(monitor.find(
                    {"job_id": "2022년_서울시", "line_id" :lineid,},
                    {"monitor_id":1, "line_id" :  1, "road_name":1, "heading":1 , "track":1, "monitor_start_station": 1, "monitor_end_station":1, "compare_id" : 1, "line_id":1, "monitor_date" : 1}
                ))
            self.compareid_list = monitor.find({"job_id": "2022년_서울시", "line_id" :lineid,}).distinct('compare_id')
        
        elif all((heading_idx ,road_idx ,track_idx)) : #3개 다 선택함 (0아님, 0아님, 0아님) = True
            self.monitor_list = list(monitor.find(
                    {"job_id": "2022년_서울시", "line_id" :lineid, "heading" : heading, "road_name" : road, "track" : track},
                    {"monitor_id":1, "line_id" :  1, "road_name":1, "heading":1 , "track":1, "monitor_start_station": 1, "monitor_end_station":1, "compare_id" : 1, "line_id":1, "monitor_date" : 1}
                ))
            self.compareid_list = monitor.find({"job_id": "2022년_서울시", "line_id" :lineid, "heading" : heading, "road_name" : road, "track" : track}).distinct('compare_id')
        
        elif (heading_idx ,road_idx ,track_idx).count(0) == 2 : #1개만 선택 (2개가 0인경우)
            if heading_idx != 0 : #행선 선택 (heading0아님, 0, 0)
                self.monitor_list = list(monitor.find(
                    {"job_id": "2022년_서울시", "line_id" :lineid, "heading" : heading},
                    {"monitor_id":1, "line_id" :  1, "road_name":1, "heading":1 , "track":1, "monitor_start_station": 1, "monitor_end_station":1, "compare_id" : 1, "line_id":1, "monitor_date" : 1}
                ))
                self.compareid_list = monitor.find({"job_id": "2022년_서울시", "line_id" :lineid, "heading" : heading}).distinct('compare_id')
                
                
            elif road_idx != 0 : #도로명 선택 (0, roadname0아님, 0)
                self.monitor_list = list(monitor.find(
                    {"job_id": "2022년_서울시", "line_id" :lineid, "road_name" : road},
                    {"monitor_id":1, "line_id" :  1, "road_name":1, "heading":1 , "track":1, "monitor_start_station": 1, "monitor_end_station":1, "compare_id" : 1, "line_id":1, "monitor_date" : 1}
                ))
                self.compareid_list = monitor.find({"job_id": "2022년_서울시", "line_id" :lineid, "road_name" : road}).distinct('compare_id')
                
            else : # 차로 선택 (0, 0, track0아님)
                self.monitor_list = list(monitor.find(
                    {"job_id": "2022년_서울시", "line_id" :lineid, "track" : track},
                    {"monitor_id":1, "line_id" :  1, "road_name":1, "heading":1 , "track":1, "monitor_start_station": 1, "monitor_end_station":1, "compare_id" : 1, "line_id":1, "monitor_date" : 1}
                ))
                self.compareid_list = monitor.find({"job_id": "2022년_서울시", "line_id" :lineid, "track" : track}).distinct('compare_id')
                
        else : #2개 선택 (1개만 0)
            if heading_idx == 0 : #도로명, 차로 선택
                self.monitor_list = list(monitor.find(
                    {"job_id": "2022년_서울시", "line_id" :lineid, "road_name" : road, "track" : track},
                    {"monitor_id":1, "line_id" :  1, "road_name":1, "heading":1 , "track":1, "monitor_start_station": 1, "monitor_end_station":1, "compare_id" : 1, "line_id":1, "monitor_date" : 1}
                ))
                self.compareid_list = monitor.find({"job_id": "2022년_서울시", "line_id" :lineid, "road_name" : road, "track" : track}).distinct('compare_id')
            elif road_idx == 0 : #행선, 차로 선택
                self.monitor_list = list(monitor.find(
                    {"job_id": "2022년_서울시", "line_id" :lineid, "heading" : heading, "track" : track},
                    {"monitor_id":1, "line_id" :  1, "road_name":1, "heading":1 , "track":1, "monitor_start_station": 1, "monitor_end_station":1, "compare_id" : 1, "line_id":1, "monitor_date" : 1}
                ))
                self.compareid_list = monitor.find({"job_id": "2022년_서울시", "line_id" :lineid, "heading" : heading, "track" : track}).distinct('compare_id')
            else : # 행선, 도로명 선택
                self.monitor_list = list(monitor.find(
                    {"job_id": "2022년_서울시", "line_id" :lineid, "road_name" : road, "heading" : heading},
                    {"monitor_id":1, "line_id" :  1, "road_name":1, "heading":1 , "track":1, "monitor_start_station": 1, "monitor_end_station":1, "compare_id" : 1, "line_id":1, "monitor_date" : 1}
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
        #self.pdf_save_button.setEnabled(True) #pdf변환 버튼 활성화 
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
        date = a_monitor['monitor_date']
        y = date.year
        m = date.month if date.month >=10 else "0" + str(date.month)
        d = date.day if date.day >=10 else "0" + str(date.day)
        monitor_date = f"{y}-{m}-{d}" 
        
        
        #21년도 compare_id : f"{road_name}({line_id})_{heading[0]}_{track}" 에서 line_id부분이 01이아닌 1로 저장되어있음
        lineid_str = a_monitor['line_id']
        lineid_int = int(lineid_str)
        compareid_21 = compareid.split("(")[0] + "(" + str(lineid_int) + ")" + compareid.split(")")[1]

        
        ###
        seoul22 = list(result.find(
            {"job_name": "2022년_서울시", "compare_id": compareid},
            {"job_id": 1,"compare_id" : 1, "station": 1, "old_score":1,  "photo_surface":1},
        ).sort("station"))
        seoul21 = list(result.find(
            {"job_name": "2021년_서울시", "compare_id": compareid_21},
            {"job_id": 1,"compare_id" : 1, "station": 1, "old_score":1, "photo_surface":1}
        ).sort("station"))

        station22start, crack_percent22, photo22 =[], [], []
        for a_station in seoul22 :
            station22start.append(int(a_station['station']['start']))
            crack_percent22.append(float(a_station['old_score']['crack']))
            #photo = (a_station['photo_surface']['surface1'].split("_")[-1]).split(".")[0]
            #photo22.append(int(photo[1:])/1000000)
            photo = (a_station['photo_surface']['surface1'])
            photo22.append(photo)
        station21start, crack_percent21, photo21 =[], [], []
        for a_station in seoul21 :
            station21start.append(int(a_station['station']['start']))
            crack_percent21.append(float(a_station['old_score']['crack']))
            #photo = (a_station['photo_surface']['surface1'].split("_")[-1]).split(".")[0]
            #photo21.append(int(photo[1:])/1000000)
            photo = (a_station['photo_surface']['surface1'])
            photo21.append(photo)

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
        df = pd.merge(df22, df21, left_on='22station', right_on='21station', how='left')
        # 필요없는 컬럼 drop
        df.drop(['21photo', '21station'], axis=1, inplace=True)
        #rename
        df = df.rename(columns={'22station': 'station', '22photo': 'photo'})
        #컬럼 순서 변경
        df = df[['station', '21crack', '22crack', 'photo']] 
        return df

        
    def one_png_save(self, one_monitorid_dict, monitorid) :

        fig = plt.figure(figsize=(27.64,6.68)) # cm->inch ? (27.64/2.54,6.68/2.54) (27.64,6.68)
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
        interval = 200 if monitor_end_station - monitor_start_station >=7000 else 100
        plt.xticks(list((range(monitor_start_station, monitor_end_station+20, interval))),rotation=90) #눈금
        plt.minorticks_on()

        
        plt.ylabel("crack_percent")
        plt.xlabel("start_station")
        
        plt.title(monitorid)
        plt.legend()
        
        #fig.savefig(f"{monitorid}.png", bbox_inches = 'tight')
        return fig
    
    def csv_save(self) :
        monitor = self.database["monitor"]
        cnt = 0
        for monitorid in self.monitorid_dict.keys() :
            monitorid_csv = self.one_csv_save(self.monitorid_dict[monitorid], monitorid)
            
            #날짜 추가
            monitordate_info = list(monitor.find(
                {"job_id": "2022년_서울시", "monitor_id": monitorid},
                {"monitor_date" : 1}
            ))
            date = monitordate_info[0]['monitor_date']
            y = date.year
            m = date.month if date.month >=10 else "0" + str(date.month)
            d = date.day if date.day >=10 else "0" + str(date.day)
            monitor_date = f"{y}-{m}-{d}" 
            monitor_date_df = pd.DataFrame({'monitor_date': monitor_date}, index = ['monitor_date'])
            monitor_date_df.to_csv(os.path.join(self.report_path.text(), f"{monitorid}.csv") , header = False, index = False, encoding='utf-8-sig')
            
            monitorid_csv.to_csv(os.path.join(self.report_path.text(), f"{monitorid}.csv"), mode='a', index = False, encoding='utf-8-sig')
            cnt+=1
        QMessageBox.about(self, "csv파일 생성완료", f"csv파일 총 {cnt}개 저장 완료")
    
    def graph_save(self) :
        cnt = 0
        for monitorid in self.monitorid_dict.keys() :
            monitorid_fig = self.one_png_save(self.monitorid_dict[monitorid], monitorid)
            monitorid_fig.savefig(os.path.join(self.report_path.text(), f"{monitorid}.png"), bbox_inches = 'tight')
            cnt+=1
        QMessageBox.about(self, "그래프 생성완료", f"그래프 이미지 총 {cnt}개 저장 완료")
    
    def pdf_save(self) :
        filename = self.lineid_combobox.currentText() #lineid 필수
        for combo in [self.heading_combobox,  self.roadname_combobox, self.track_combobox] :
            if combo.currentIndex() != 0 :
                filename += combo.currentText()
        filename += ".pdf"
        pdfsave  = PdfPages(os.path.join(self.report_path.text(), filename))
        cnt = 0
        for monitorid in self.monitorid_dict.keys() :
            monitorid_fig = self.one_png_save(self.monitorid_dict[monitorid], monitorid)
            pdfsave.savefig(monitorid_fig, bbox_inches = 'tight')
            cnt+=1
        pdfsave.close()
        QMessageBox.about(self, "PDF 생성완료", f"({filename} 이미지 총{cnt}개)")
    
    def pdf_save2(self) :
        return
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
                interval = 200 if self.monitor_end_station - self.monitor_start_station >=7000 else 100
                plt.xticks(list((range(monitor_start_station, monitor_end_station+20, interval))),rotation=90) #눈금
                
                
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
       
    def report_save(self) :
        return_value = execute_job("2022년_서울시", "서울시 분석보고서", self.report_path.text(), self.monitorid_dict)
        QMessageBox.about(self, "보고서 저장 성공",
                          f"분석보고서 산출({return_value[0]} 항목)에 성공하였습니다.")
        #execute_job("2022년_서울시", "서울시 분석보고서", self.report_path.text(), self.monitorid_dict.keys())



# 과업명, 선택한 보고서 형식, 저장 경로
def execute_job(job_name, job_type, report_path, monitorid_dict, job=None, suffix="변환_보고서"):
    client = config.get_client()
    database = client[config.database_name]
    monitor = database["monitor"] # 사용 DB : 'monitor' 테이블 
    result = database["result"] 
    result20 = database["result20"]
    destination_workbook = []

    if job is None:
        with open("assess_file_config.json", encoding='utf-8', errors='ignore') as json_data:
            forms = json.load(json_data, strict=False)["form"]
            job = None
            for form in forms:
                if form["name"] == job_type: #선택한 보고서 형식
                    job = form # job : 선택한 보고서 형식 form
        if job is None:
            return
    #now = datetime.datetime.now()
    #date_suffix = f"{now.year % 100}{str(now.month).zfill(2)}{str(now.day).zfill(2)}"
    
    for monitor_id in monitorid_dict.keys():

        worksheet_length = 0
        source_workbook = openpyxl.load_workbook(job["source_workbook"])
        for sheet in job["sheets"]: # [분석자료] => [보고서] 순서
            source_worksheet = source_workbook[sheet["source_worksheet"]]
            source_worksheet_str = str(source_worksheet).split(" ")[1][1:-2]
            # 현재 진행 중 프린트
            print("monitor_id : " , monitor_id, " | sheet : ", source_worksheet)
            

            if source_worksheet_str == "분석자료" :
                query_result_by_track = monitor.aggregate([
                    {"$match": {"job_id": job_name, "monitor_id": monitor_id}},
                    {
                        "$lookup": {
                            "from": 'result',
                            "let": { "monitor_name": '$monitor_id' },
                            "pipeline": [
                            {
                                "$match": {
                                "$expr": {
                                    "$and": [
                                    { "$eq": ['$monitor_id', '$$monitor_name'] },
                                    { "$eq": ['$job_name', job_name ] },
                                    ]
                                }
                                }
                            }
                            ],
                            "as": 'result_monitor_join'
                        }
                    },
                    {"$sort": {"line_id": 1, "heading": 1, "track": 1}}
                ])
            
            elif source_worksheet_str == "보고서" :
                query_result_by_track = monitor.aggregate([
                    {"$match": {"job_id": job_name,  "monitor_id": monitor_id}},
                    {
                        "$lookup": {
                            "from": 'result20',
                            "let": { "monitor_name": '$monitor_id' },
                            "pipeline": [
                            {
                                "$match": {
                                "$expr": {
                                    "$and": [
                                    { "$eq": ['$monitor_id', '$$monitor_name'] },
                                    { "$eq": ['$job_name', job_name ] },
                                    ]
                                }
                                }
                            }
                            ],
                            "as": 'result_monitor_join'
                        }
                    },
                    {"$sort": {"line_id": 1, "heading": 1, "track": 1}}
                ])
                
               
            if source_worksheet_str == "분석자료" :
                for a_monitor in query_result_by_track:

                    result_per_monitor = {}
                    for a_result in list({item['station']: item for item in a_monitor['result_monitor_join']}.values()):
                        result_per_monitor[a_result["station"]] = a_result
                            
                    
                    station_list = [x["station"] for x in a_monitor['result_monitor_join']]
                    start_station = min(station_list)
                    last_checked = start_station - 10
                    monitor_date = a_monitor["monitor_date"]
                                
                    
                    for a_result in sorted(a_monitor['result_monitor_join'],
                                            key=lambda result_item: result_item["station"]):
                        row_content = []
                        if a_result["station"] != last_checked + 10:
                            start_station = a_result["station"]
                        last_checked = a_result["station"]
                        for content in sheet["contents"]:
                            #행선코드 : str(a_monitor["heading"]).replace("상", "S").replace("하", "E")
                            if content == "station": 
                                row_content.append(a_result["station"] / 1000)
                            elif content == "photo_surface": 
                                row_content.append(a_result["photo"]["surface"])
                            elif content == "photo_front": 
                                row_content.append(a_result["photo"]["front"])
                            elif content == "rutting": 
                                value = float(a_result["score"]["rutting"])
                                row_content.append(value)
                            elif content == "iri": 
                                value = float(a_result["score"]["iri"])
                                row_content.append(value)
                            elif content == "latitude":
                                row_content.append(a_result["location"]["latitude"])
                            elif content == "longitude": 
                                row_content.append(a_result["location"]["longitude"])
                            elif content == "crack_amount":
                                row_content.append(a_result["crack_amount"])
                            elif content == "crack_percent": 
                                row_content.append(a_result["score"]["crack"])#######
                            ## road_level에 따른 spi
                            elif content ==  "spi_roadlevel":
                                if a_monitor["road_level"] == "도시고속도로" :
                                    row_content += [a_result["spi"]["spi"],  "", "" ]
                                elif a_monitor["road_level"] == "주간선도로" :
                                    row_content += ["",a_result["spi"]["spi"], "" ]
                                elif a_monitor["road_level"] == "보조간선도로" :
                                    row_content += ["", "", a_result["spi"]["spi"]]                    
                            ##
                            elif content == "longitudinal_low": # longitudinal
                                row_content.append(a_result["crack"]["longitudinal"]["low"])
                            elif content == "longitudinal_med":
                                row_content.append(a_result["crack"]["longitudinal"]["med"])
                            elif content == "longitudinal_high":
                                row_content.append(a_result["crack"]["longitudinal"]["high"])
                            elif content == "longitudinal_sum":
                                row_content.append(a_result["crack"]["longitudinal"]["sum"])
                            elif content == "transverse_low": # transverse
                                row_content.append(a_result["crack"]["transverse"]["low"])
                            elif content == "transverse_med":
                                row_content.append(a_result["crack"]["transverse"]["med"])
                            elif content == "transverse_high":
                                row_content.append(a_result["crack"]["transverse"]["high"])
                            elif content == "transverse_sum":
                                row_content.append(a_result["crack"]["transverse"]["sum"])
                            elif content == "cold_joint_low": # cold_joint
                                row_content.append(a_result["crack"]["cold_joint"]["low"])
                            elif content == "cold_joint_med":
                                row_content.append(a_result["crack"]["cold_joint"]["med"])
                            elif content == "cold_joint_high":
                                row_content.append(a_result["crack"]["cold_joint"]["high"])
                            elif content == "cold_joint_sum":
                                row_content.append(a_result["crack"]["cold_joint"]["sum"])
                            elif content == "fatigue_low": # fatigue
                                row_content.append(a_result["crack"]["fatigue"]["low"])
                            elif content == "fatigue_med":
                                row_content.append(a_result["crack"]["fatigue"]["med"])
                            elif content == "fatigue_high":
                                row_content.append(a_result["crack"]["fatigue"]["high"])
                            elif content == "fatigue_sum":
                                row_content.append(a_result["crack"]["fatigue"]["sum"])
                            elif content == "patching_low": # patching
                                row_content.append(a_result["crack"]["patching"]["low"])
                            elif content == "patching_med":
                                row_content.append(a_result["crack"]["patching"]["med"])
                            elif content == "patching_high":
                                row_content.append(a_result["crack"]["patching"]["high"])
                            elif content == "patching_sum":
                                row_content.append(a_result["crack"]["patching"]["sum"])
                            elif content == "pothole_low": # pothole
                                row_content.append(a_result["crack"]["pothole"]["low"])
                            elif content == "pothole_med":
                                row_content.append(a_result["crack"]["pothole"]["med"])
                            elif content == "pothole_high":
                                row_content.append(a_result["crack"]["pothole"]["high"])
                            elif content == "pothole_sum":
                                row_content.append(a_result["crack"]["pothole"]["sum"])
                            ##
                            elif content == "width":
                                value = float(a_result["width"])
                                row_content.append(value)
                            elif content == "area":
                                if source_worksheet_str == "분석자료" :
                                    value = float(a_result["width"]) * 10
                                elif source_worksheet_str == "보고서" :
                                    value = float(a_result["area"]) 
                                row_content.append(value)
                            elif content == "intersection_boolean" :
                                row_content.append("Y" if "교차로" in a_result["more_info"] else "")
                            elif content == "more_info": #분석자료
                                row_content.append(a_result["more_info"])

                            ####
                            elif content == "year":
                                row_content.append(monitor_date.year)
                            elif content == "month":
                                row_content.append(monitor_date.month)
                            elif content == "line_id":
                                row_content.append(a_monitor["line_id"])
                            elif content == "line_name": ##추가필요
                                row_content.append('=VLOOKUP(분석자료!D6,참조.시도노선!$A$2:$E$180,3,FALSE)')
                            elif content == "road_name":
                                row_content.append(a_monitor["road_name"])
                            elif content == "road_level":
                                row_content.append(a_monitor["road_level"])
                            elif content == "heading":
                                row_content.append(str(a_monitor["heading"]))
                            elif content == "track":
                                row_content.append(a_monitor["track"])
                            elif content == "start_station":
                                row_content.append(a_result["station"]["start"])
                            elif content == "end_station":
                                row_content.append(a_result["station"]["end"])

        
                            elif content == "old_crack":
                                row_content.append(a_result["old_score"]["crack"])
                            elif content == "old_rutting":
                                row_content.append(a_result["old_score"]["rutting"])
                            elif content == "old_iri":
                                row_content.append(a_result["old_score"]["iri"])

                            elif content == "old_spi_1":
                                row_content.append(a_result["old_spi"]["spi_1"])
                            elif content == "old_spi_2":
                                row_content.append(a_result["old_spi"]["spi_2"])
                            elif content == "old_spi_3":
                                row_content.append(a_result["old_spi"]["spi_3"])
                            elif content == "old_spi_30":
                                row_content.append(a_result["old_spi"]["spi_30"])   
                            
                            elif content == "aci" or content == "lci" or content == "tci" or content == "pati" or content == "ruti" or content ==  "cri" or content == "sci" or content == "rci" or content ==  "spi" :
                                row_content.append(a_result["new_spi"][content])  
                            
                            elif content == "photo_surface1": 
                                row_content.append(a_result["photo_surface"]["surface1"])
                            elif content == "photo_surface2": 
                                row_content.append(a_result["photo_surface"]["surface2"])
                                
                            else:
                                row_content.append(None)
                        
                        if len(row_content) == 0 or all([x is None for x in row_content]):
                            continue
                        
                        source_worksheet.append(row_content)
                        worksheet_length += 1
                    
                    break 
            
            elif source_worksheet_str == "보고서" :
                for a_monitor in query_result_by_track:

                    result_per_monitor = {}
                    for a_result in list({item['station']['start']: item for item in a_monitor['result_monitor_join']}.values()):
                        result_per_monitor[a_result["station"]['start']] = a_result
                            
                    
                    station_list = [x["station"]['start'] for x in a_monitor['result_monitor_join']]
                    start_station = min(station_list)
                    last_checked = start_station - 20
                    monitor_date = a_monitor["monitor_date"]
                                
                    
                    for a_result in sorted(a_monitor['result_monitor_join'],
                                            key=lambda result_item: result_item["station"]['start']):
                        row_content = []
                        if a_result["station"]['start'] != last_checked + 20:
                            start_station = a_result["station"]['start']
                        last_checked = a_result["station"]['start']
                        for content in sheet["contents"]:
                            #행선코드 : str(a_monitor["heading"]).replace("상", "S").replace("하", "E")
                            if content == "station": 
                                row_content.append(a_result["station"] / 1000)
                            elif content == "photo_surface": 
                                row_content.append(a_result["photo"]["surface"])
                            elif content == "photo_front": 
                                row_content.append(a_result["photo"]["front"])
                            elif content == "rutting": 
                                value = float(a_result["score"]["rutting"])
                                row_content.append(value)
                            elif content == "iri": 
                                value = float(a_result["score"]["iri"])
                                row_content.append(value)
                            elif content == "latitude":
                                row_content.append(a_result["location"]["latitude"])
                            elif content == "longitude": 
                                row_content.append(a_result["location"]["longitude"])
                            elif content == "crack_amount":
                                row_content.append(a_result["crack_amount"])
                            elif content == "crack_percent": 
                                row_content.append(a_result["score"]["crack"])
                            ## road_level에 따른 spi
                            elif content ==  "spi_roadlevel":
                                if a_monitor["road_level"] == "도시고속도로" :
                                    row_content += [a_result["spi"]["spi"],  "", "" ]
                                elif a_monitor["road_level"] == "주간선도로" :
                                    row_content += ["",a_result["spi"]["spi"], "" ]
                                elif a_monitor["road_level"] == "보조간선도로" :
                                    row_content += ["", "", a_result["spi"]["spi"]]                    
                            ##
                            elif content == "longitudinal_low": # longitudinal
                                row_content.append(a_result["crack"]["longitudinal"]["low"])
                            elif content == "longitudinal_med":
                                row_content.append(a_result["crack"]["longitudinal"]["med"])
                            elif content == "longitudinal_high":
                                row_content.append(a_result["crack"]["longitudinal"]["high"])
                            elif content == "longitudinal_sum":
                                row_content.append(a_result["crack"]["longitudinal"]["sum"])
                            elif content == "transverse_low": # transverse
                                row_content.append(a_result["crack"]["transverse"]["low"])
                            elif content == "transverse_med":
                                row_content.append(a_result["crack"]["transverse"]["med"])
                            elif content == "transverse_high":
                                row_content.append(a_result["crack"]["transverse"]["high"])
                            elif content == "transverse_sum":
                                row_content.append(a_result["crack"]["transverse"]["sum"])
                            elif content == "cold_joint_low": # cold_joint
                                row_content.append(a_result["crack"]["cold_joint"]["low"])
                            elif content == "cold_joint_med":
                                row_content.append(a_result["crack"]["cold_joint"]["med"])
                            elif content == "cold_joint_high":
                                row_content.append(a_result["crack"]["cold_joint"]["high"])
                            elif content == "cold_joint_sum":
                                row_content.append(a_result["crack"]["cold_joint"]["sum"])
                            elif content == "fatigue_low": # fatigue
                                row_content.append(a_result["crack"]["fatigue"]["low"])
                            elif content == "fatigue_med":
                                row_content.append(a_result["crack"]["fatigue"]["med"])
                            elif content == "fatigue_high":
                                row_content.append(a_result["crack"]["fatigue"]["high"])
                            elif content == "fatigue_sum":
                                row_content.append(a_result["crack"]["fatigue"]["sum"])
                            elif content == "patching_low": # patching
                                row_content.append(a_result["crack"]["patching"]["low"])
                            elif content == "patching_med":
                                row_content.append(a_result["crack"]["patching"]["med"])
                            elif content == "patching_high":
                                row_content.append(a_result["crack"]["patching"]["high"])
                            elif content == "patching_sum":
                                row_content.append(a_result["crack"]["patching"]["sum"])
                            elif content == "pothole_low": # pothole
                                row_content.append(a_result["crack"]["pothole"]["low"])
                            elif content == "pothole_med":
                                row_content.append(a_result["crack"]["pothole"]["med"])
                            elif content == "pothole_high":
                                row_content.append(a_result["crack"]["pothole"]["high"])
                            elif content == "pothole_sum":
                                row_content.append(a_result["crack"]["pothole"]["sum"])
                            ##
                            elif content == "width":
                                value = float(a_result["width"])
                                row_content.append(value)
                            elif content == "area":
                                if source_worksheet_str == "분석자료" :
                                    value = float(a_result["width"]) * 10
                                elif source_worksheet_str == "보고서" :
                                    value = float(a_result["area"]) 
                                row_content.append(value)
                            elif content == "intersection_boolean" :
                                row_content.append("Y" if "교차로" in a_result["more_info"] else "")
                            elif content == "more_info": #분석자료
                                row_content.append(a_result["more_info"])

                            ####
                            elif content == "year":
                                row_content.append(monitor_date.year)
                            elif content == "month":
                                row_content.append(monitor_date.month)
                            elif content == "line_id":
                                row_content.append(a_monitor["line_id"])
                            elif content == "line_name": ##추가필요
                                row_content.append('=VLOOKUP(분석자료!D6,참조.시도노선!$A$2:$E$180,3,FALSE)')
                            elif content == "road_name":
                                row_content.append(a_monitor["road_name"])
                            elif content == "road_level":
                                row_content.append(a_monitor["road_level"])
                            elif content == "heading":
                                row_content.append(str(a_monitor["heading"]))
                            elif content == "track":
                                row_content.append(a_monitor["track"])
                            elif content == "start_station":
                                row_content.append(a_result["station"]["start"])
                            elif content == "end_station":
                                row_content.append(a_result["station"]["end"])

        
                            elif content == "old_crack":
                                row_content.append(a_result["old_score"]["crack"])
                            elif content == "old_rutting":
                                row_content.append(a_result["old_score"]["rutting"])
                            elif content == "old_iri":
                                row_content.append(a_result["old_score"]["iri"])

                            elif content == "old_spi_1":
                                row_content.append(a_result["old_spi"]["spi_1"])
                            elif content == "old_spi_2":
                                row_content.append(a_result["old_spi"]["spi_2"])
                            elif content == "old_spi_3":
                                row_content.append(a_result["old_spi"]["spi_3"])
                            elif content == "old_spi_30":
                                row_content.append(a_result["old_spi"]["spi_30"])   
                            
                            elif content == "aci" or content == "lci" or content == "tci" or content == "pati" or content == "ruti" or content ==  "cri" or content == "sci" or content == "rci" or content ==  "spi" :
                                row_content.append(a_result["new_spi"][content])  
                            
                            elif content == "photo_surface1": 
                                row_content.append(a_result["photo_surface"]["surface1"])
                            elif content == "photo_surface2": 
                                row_content.append(a_result["photo_surface"]["surface2"])
                                
                            else:
                                row_content.append(None)
                        
                        if len(row_content) == 0 or all([x is None for x in row_content]):
                            continue
                        
                        source_worksheet.append(row_content)
                        worksheet_length += 1
                    
                    break 
            
            
        
        
        if worksheet_length > 0:
            source_workbook.save(
                os.path.join(report_path, f"{monitor_id}_{suffix}.xlsx"))
            destination_workbook.append(
                os.path.join(report_path, f"{monitor_id}_{suffix}.xlsx"))
        else:
            source_workbook.close()



    return len(destination_workbook) , destination_workbook,





