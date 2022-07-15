import csv
import os
from decimal import Decimal

import pymongo
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox

import config
from add_result.add_result_ui import AddResultSeoulUI
from file_manager import get_files_in_dir_with_ext


class AddResultSeoul(QDialog, AddResultSeoulUI):
    def __init__(self, job_name: str):
        QDialog.__init__(self, None, Qt.Dialog)

        # 화면 구성
        self.setupUi(self, job_name)

        # 버튼 연결
        self.file_path_select_button.clicked.connect(self.select_file_path) #[파일 선택] 버튼
        self.folder_path_select_button.clicked.connect(self.select_folder_path) #[폴더 선택] 버튼
        self.upload_result_button.clicked.connect(self.upload_result) #[업로드] 버튼
        self.upload_result20_button.clicked.connect(self.upload_result20) #[20m변환] 버튼

    # 파일 선택
    def select_file_path(self): #[파일 선택] 
        file_path = QFileDialog.getOpenFileName(filter="분석 결과 파일 (*.csv)")[0] #선택파일형식 csv만
        if file_path:
            self.file_path.setText(file_path)
            self.file_path.setEnabled(True) #파일경로 칸 set
            self.folder_path.setDisabled(True)
            self.upload_result_button.setEnabled(True) #업로드버튼 활성화

    # 폴더 선택
    def select_folder_path(self):  #[폴더 선택] 
        folder_path = QFileDialog.getExistingDirectory() #선택폴더주소
        if folder_path:
            self.folder_path.setText(folder_path)
            self.folder_path.setEnabled(True) #폴더경로 칸 set
            self.file_path.setDisabled(True)
            self.upload_result_button.setEnabled(True) #업로드버튼 활성화

    # 업로드
    def upload_result(self):  #[업로드]
        file_list = []
        if self.file_path.isEnabled():
            file_list.append(self.file_path.text())
        elif self.folder_path.isEnabled():
            file_list.extend(get_files_in_dir_with_ext(self.folder_path.text(), "csv"))
        print("분석보고서 개수 : ", len(file_list))
        
        ##DB연결
        client = config.get_client()
        database = client[config.database_name]
        monitor = database["monitor"] # monitor : "monitor" 테이블
        if "result" not in database.list_collection_names():
            database.create_collection("result")
            result = database["result"]
            result.create_index([("job_name", 1), ("monitor_id", 1), ("station", 1)], unique=True)
        else:
            result = database["result"]  # result : "result" 테이블
        insert_rows = []
        for file_index, file_name in enumerate(file_list):
            raw_data = []
            with open(file_name, newline='', encoding='cp949') as csv_file:
                print("입력한 분석 보고서 : ", file_name) #파일경로 출력
                csv_reader = csv.reader(csv_file)

                for row_index, row in enumerate(csv_reader):
                    # 9번째 줄에서 연도 추출
                    if row_index == 8:
                        year = row[1].split("-")[0]
                        month = row[1].split("-")[1]
                        date = row[1].split("-")[2]
                    # 14번째 줄부터 데이터 추출
                    elif row_index >= 13:
                        if not row[0] : #문자열이 비어있는애면
                            continue
                        row[0] = round(int(Decimal(row[0]) * 1000), -1) # km-> m
                        raw_data.append(row) #csv파일의 모든 찐 데이터 row들 추가된 배열 (시/종점 반영안됨)

            source_id = os.path.basename(file_name).split("_분석_보고서")[0].split("\\")[-1] #"monitor" 의 source_id컬럼 데이터와 일치
            
            monitor_list = list(monitor.find(
                {"job_id": self.job_name.text(), "source_id": source_id},
                {"job_id": 1,"monitor_id": 1, "monitor_start_station": 1, "source_start_station": 1, "source_end_station": 1, "road_level":1}
            ))

            for a_monitor in monitor_list: # "monitor" 테이블에서 job_id, monitor_id, monitor시점, source시점, source종점 빼온다. -> 한 줄씩 본다. 
                job_id = a_monitor["job_id"]
                monitor_id = a_monitor["monitor_id"]
                start_station = a_monitor["monitor_start_station"]
                source_start_station = a_monitor["source_start_station"]
                source_end_station = a_monitor["source_end_station"]
                road_level = a_monitor["road_level"] #도로등급 
                if start_station is None or source_start_station is None or source_end_station is None:
                    continue
                if source_start_station < source_end_station:
                    sorted_data = sorted([row for row in raw_data if source_start_station < row[0] <= source_end_station],
                                         key=lambda x: x[0])
                else:
                    sorted_data = sorted([row for row in raw_data if source_end_station < row[0] <= source_start_station],
                                         key=lambda x: x[0], reverse=True)
                station = start_station
                for data in sorted_data: #csv파일 변경된 시/종점 범위 한 줄씩 본다
                    #서울시
                    # 각 줄의 32번째 칸까지 데이터에서 각 항목을 추출 (서울시 분석보고서에 해당)
                    _, photo_front, photo_surface, rutting, iri, latitude, longitude, crack_amount, _, _, _, _, \
                        longitudinal_low, longitudinal_med, longitudinal_high, \
                        transverse_low, transverse_med, transverse_high, \
                        cold_joint_low, cold_joint_med, cold_joint_high, \
                        fatigue_low, fatigue_med, fatigue_high, \
                        patching_low, patching_med, patching_high, \
                        pothole_low, pothole_med, pothole_high, more_info, width = data[:32]
                    if len(data) != 32:
                        print(a_monitor, len(data))
                            
                    if width == '':
                        print(a_monitor)
                    width = round(float(width), 2)  # 분석폭을 소숫점 두자리로 반올림

                    crack_percent = ((float(longitudinal_low) + float(longitudinal_med) + float(longitudinal_high) + float(transverse_low) +
                                    float(transverse_med) + float(transverse_high) + float(cold_joint_low) + float(cold_joint_med) + float(cold_joint_high)) * 0.3 +
                                    (float(fatigue_low)+ float(fatigue_med) + float(fatigue_high) + float(patching_low) + float(patching_med) + float(patching_high)
                                    + float(pothole_low) + float(pothole_med) + float(pothole_high))) / (float(width) * 10 if float(width) != 0 else 0.001) * 100.0
                    
                    # string -> float
                    rutting, iri, latitude, longitude,\
                    longitudinal_low, longitudinal_med, longitudinal_high, \
                    transverse_low, transverse_med, transverse_high, \
                    cold_joint_low, cold_joint_med, cold_joint_high, \
                    fatigue_low, fatigue_med, fatigue_high, \
                    patching_low, patching_med, patching_high, \
                    pothole_low, pothole_med, pothole_high, width, crack_amount = float(rutting), float(iri), float(latitude), float(longitude), float(longitudinal_low), float(longitudinal_med), float(longitudinal_high), float(transverse_low), float(transverse_med), float(transverse_high), float(cold_joint_low), float(cold_joint_med), float(cold_joint_high), float(fatigue_low), float(fatigue_med), float(fatigue_high), float(patching_low), float(patching_med), float(patching_high), float(pothole_low), float(pothole_med), float(pothole_high), float(width), float(crack_amount)
                    
                    spi_1 = 10 - 1.667 * (crack_percent ** 0.38) if 10 - 1.667 * (crack_percent ** 0.38) > 0 else 0
                    spi_2 = 10 - 0.267 * float(rutting) if 10 - 0.267 * float(rutting) else 0

                    #spi값 road_level에 따라 넣기
                    if road_level == "도시고속도로" :
                        spi_3 = 10 - 0.8 * float(iri) if 10 - 0.8 * float(iri) >= 0 else 0
                    elif road_level == "주간선도로" :
                        spi_3 = 10 - 0.727 * float(iri) if 10 - 0.727 * float(iri) >= 0 else 0
                    elif road_level == "보조간선도로" :
                        spi_3 = 10 - 0.667 * float(iri) if 10 - 0.667 * float(iri) >= 0 else 0
                    
                    spi = 10 - ((10 - spi_1) ** 5 + (10 - spi_2) ** 5 + (10 - spi_3) ** 5) ** 0.2 if 10 - ((10 - spi_1) ** 5 + (10 - spi_2) ** 5 + (10 - spi_3) ** 5) ** 0.2 >= 0 else 0
            
                                        
                    insert_data = {"_id": f"{self.job_name.text()}_{monitor_id}_{station}",
                                "job_name": self.job_name.text(), "monitor_id": monitor_id,
                                "station": station, "width": width,
                                "location": {"latitude": latitude, "longitude": longitude},
                                "crack_amount" : crack_amount,
                                "spi" : {
                                    "spi" : spi,
                                    "spi_1" : spi_1,
                                    "spi_2" : spi_2,
                                    "spi_3" : spi_3 ,
                                },
                                "crack": {
                                    "longitudinal": {"low": longitudinal_low, "med": longitudinal_med,
                                                        "high": longitudinal_high},
                                    "transverse": {"low": transverse_low, "med": transverse_med,
                                                    "high": transverse_high},
                                    "fatigue": {"low": fatigue_low, "med": fatigue_med, "high": fatigue_high},
                                    "cold_joint": {"low": cold_joint_low, "med": cold_joint_med,
                                                    "high": cold_joint_high},
                                    "patching": {"low": patching_low, "med": patching_med, "high": patching_high},
                                    "pothole": {"low": pothole_low, "med": pothole_med, "high": pothole_high},
                                },
                                "score": {"crack": crack_percent,"rutting": rutting, "iri": iri},
                                "photo": {"front": photo_front, "surface": photo_surface},
                                "more_info": more_info
                                }
                    insert_rows.append(insert_data)
                    station += 10
        print("insert row 수 : " , len(insert_rows))
        
        for doc in insert_rows:     
            check_exist = list(result.find({"_id" : doc['_id']}))
            if not check_exist: #없으면 새로 inset (check_exist리스트가 empty일 경우)
                #print("data inserted : ", doc['_id'], " - insert")
                result.insert_one(doc)
                
            else: #이미 저장한 값이면 
                #print("data inserted : ", doc['_id'], " - replace")    
                result.replace_one({'_id': doc['_id']}, doc)

        client.close()
        self.upload_result20_button.setEnabled(True) #20m변환버튼 활성화
        QMessageBox.about(self, "업로드 성공", f"분석 결과 업로드({len(insert_rows)} 항목)에 성공하였습니다.")

    def upload_result20(self):  #[업로드]
        file_list = []
        if self.file_path.isEnabled():
            file_list.append(self.file_path.text())
        elif self.folder_path.isEnabled():
            file_list.extend(get_files_in_dir_with_ext(self.folder_path.text(), "csv"))
        if self.file_path.isEnabled() or self.folder_path.isEnabled():
            print("분석보고서 개수 : ", len(file_list))
        
        ##DB연결
        client = config.get_client()
        database = client[config.database_name]
        monitor = database["monitor"] # monitor : "monitor" 테이블
        result = database["result"] # result : "result" 테이블
        if "result20" not in database.list_collection_names():
            database.create_collection("result20")
            result20 = database["result20"]
            result20.create_index([("job_name", 1), ("station", 1)], unique=True)
        else:
            result20 = database["result20"]  # result20 : "result20" 테이블
        
        monitor_list = result.aggregate(
            [
                {"$match": {"job_name": self.job_name.text()}},
                {"$group": {
                    "_id":  "$monitor_id",
                    "count" : {"$sum" : 1}
                }},
                {"$sort" : {"monitor_id" : 1}},
            ]
        )
        
        insert_rows = []
        for a_monitor in monitor_list :
            monitor_id = a_monitor['_id']
            origin_cnt = a_monitor['count']
            
            monitor_10station_list = list(result.find(
                filter ={"job_name": self.job_name.text(), "monitor_id": monitor_id}, 
                sort = [("station", 1 )]
            ))
            #monitor_start_10station = monitor_10station_list[0]['station']
            #monitor_end_10station = monitor_10station_list[-1]['station']
            
            a = list(monitor.find(
                {"job_id": self.job_name.text(), "monitor_id": monitor_id},
                {"job_id": 1,"monitor_id": 1, "compare_id" : 1, "monitor_start_station": 1, "monitor_end_station": 1, "road_level":1}
            ))
            monitor_start_10station = a[0]['monitor_start_station']
            monitor_end_10station = a[0]['monitor_end_station']
            road_level = a[0]['road_level']
            compare_id = a[0]['compare_id']
            
            origin_dict = {}
            for a_station in monitor_10station_list:
                station10 = a_station['station'] #10m단위
                origin_dict[station10] = a_station  
                
            after_cnt = 0
            for row_index, station in enumerate(range(monitor_start_10station, monitor_end_10station, 20)):
                photo_surface, more_info, rutting, iri, width, crack_avg_percent, \
                crack_longitudinal_low, crack_longitudinal_med, crack_longitudinal_high, \
                crack_transverse_low, crack_transverse_med, crack_transverse_high, \
                crack_cold_joint_low, crack_cold_joint_med, crack_cold_joint_high, \
                crack_fatigue_low, crack_fatigue_med, crack_fatigue_high, \
                crack_patching_low, crack_patching_med, crack_patching_high, \
                crack_pothole_low, crack_pothole_med, crack_pothole_high, count, \
                spi_1, spi_2, spi_3, spi_30 , crack_amount  , latitude, longitude = \
                [], [], 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,0.0, 0.0, 0.0,0.0, 0.0, 0.0,0.0, 0.0, 0.0,0.0, 0.0, 0.0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
                
                
                for temp_station in range(station, station + 20, 10):
                    if temp_station in origin_dict.keys():
                        item = origin_dict[temp_station]
                        
                        photo_surface.append(item["photo"]["surface"])
                        more_info.append(item["more_info"])
                        rutting += item["score"]["rutting"]
                        iri += item["score"]["iri"]
                        crack_avg_percent += item["score"]["crack"]
                        crack_amount += item["crack_amount"]
                        width += item["width"]
                        latitude += item['location']['latitude']
                        longitude += item['location']['longitude']

                        spi_1 += item['spi']['spi_1']
                        spi_2 += item['spi']['spi_2']
                        spi_3 += item['spi']['spi_3']
                        spi_30 += item['spi']['spi']           
                        
                        crack_longitudinal_low += item["crack"]["longitudinal"]["low"]
                        crack_longitudinal_med += item["crack"]["longitudinal"]["med"]
                        crack_longitudinal_high += item["crack"]["longitudinal"]["high"]
                        
                        crack_transverse_low += item["crack"]["transverse"]["low"]
                        crack_transverse_med += item["crack"]["transverse"]["med"]
                        crack_transverse_high += item["crack"]["transverse"]["high"]
                        
                        crack_cold_joint_low += item["crack"]["cold_joint"]["low"]
                        crack_cold_joint_med += item["crack"]["cold_joint"]["med"]
                        crack_cold_joint_high += item["crack"]["cold_joint"]["high"]
                        
                        crack_fatigue_low += item["crack"]["fatigue"]["low"]
                        crack_fatigue_med += item["crack"]["fatigue"]["med"]
                        crack_fatigue_high += item["crack"]["fatigue"]["high"]       
                                            
                        crack_patching_low += item["crack"]["patching"]["low"]
                        crack_patching_med += item["crack"]["patching"]["med"]
                        crack_patching_high += item["crack"]["patching"]["high"]
                        
                        crack_pothole_low += item["crack"]["pothole"]["low"]
                        crack_pothole_med += item["crack"]["pothole"]["med"]
                        crack_pothole_high += item["crack"]["pothole"]["high"] 
                        
                        count += 1
                        
                after_cnt += 1
                
                try : 
                    crack_percent = (crack_avg_percent / count) if crack_avg_percent > 0 else 0
                    
                    rutting = (rutting / count )  if rutting > 0 else 0
                    iri = (iri/count)  if iri > 0 else 0
                    crack_amount = (crack_amount/count)  if crack_amount > 0 else 0
                    area = width * 10
                    width = (width/count)  if width > 0 else 0
                    latitude= (latitude/count) if latitude > 0 else 0
                    longitude = (longitude/count) if longitude > 0 else 0
                    
                    aci = 10-40*((crack_fatigue_low/(area))*100/700+(crack_fatigue_med/(area))*100/300+(crack_fatigue_high/(area))*100/100) if 10-40*((crack_fatigue_low/(area))*100/700+(crack_fatigue_med/(area))*100/300+(crack_fatigue_high/(area))*100/100) >= 0 else 0
                    lci = 10-4*(((crack_longitudinal_low/20)*100)/350+((crack_longitudinal_med/20)*100)/200+((crack_longitudinal_high/20)*100)/75) if 10-4*(((crack_longitudinal_low/20)*100)/350+((crack_longitudinal_med/20)*100)/200+((crack_longitudinal_high/20)*100)/75) >= 0 else 0
                    tci = 10-4*(((crack_transverse_low/(width))*100)/350+((crack_transverse_med/(width))*100)/200+((crack_transverse_high/(width))*100)/75) if 10-4*(((crack_transverse_low/(width))*100)/350+((crack_transverse_med/(width))*100)/200+((crack_transverse_high/(width))*100)/75) >= 0 else 0
                    pati = 10-10*((crack_patching_low + crack_patching_med + crack_patching_high + crack_pothole_low + crack_pothole_med + crack_pothole_high)/(area)) if 10-10*((crack_patching_low + crack_patching_med + crack_patching_high + crack_pothole_low + crack_pothole_med + crack_pothole_high)/(area)) >= 0 else 0
                    ruti = 10 - 0.267 * (rutting) if 10 - 0.267 * (rutting) >= 0 else 0
                    
                    cri = 10-(3*((10-aci)**0.5)+2.5*((10-lci)**0.5)+1*((10-tci)**0.5)+3*((10-pati)**0.5)) if 10-(3*((10-aci)**0.5)+2.5*((10-lci)**0.5)+1*((10-tci)**0.5)+3*((10-pati)**0.5)) >= 0 else 0
                    sci = 10-((10-cri)**5+(10-ruti)**5)**0.2 if 10-((10-cri)**5+(10-ruti)**5)**0.2 >= 0 else 0
                    #rci값 road_level에 따라 넣기
                    if road_level == "도시고속도로" :
                        rci = 10 - 0.8 * float(iri) if 10 - 0.8 * float(iri) >= 0 else 0
                    elif road_level == "주간선도로" :
                        rci = 10 - 0.727 * float(iri) if 10 - 0.727 * float(iri) >= 0 else 0
                    elif road_level == "보조간선도로" :
                        rci = 10 - 0.667 * float(iri) if 10 - 0.667 * float(iri) >= 0 else 0
                    spi = 10-((10-sci)**5+(10-rci)**5)**0.2 if 10-((10-sci)**5+(10-rci)**5)**0.2 >= 0 else 0
                    road_note = more_info[0]
                except ZeroDivisionError :
                    continue
                
                
                
                insert_data = {"_id": f"{self.job_name.text()}_{monitor_id}_{station}",
                        "job_name": self.job_name.text(), "monitor_id": monitor_id,  "compare_id" :compare_id,
                        "station": {"start": station, "end": station+20}, "width": width, "area" : area,
                        "location": {"latitude": latitude, "longitude": longitude},
                        "crack_amount" : crack_amount,
                        "crack": {
                            "longitudinal": {"low": crack_longitudinal_low, "med": crack_longitudinal_med, "high": crack_longitudinal_high, "sum" : crack_longitudinal_low + crack_longitudinal_med + crack_longitudinal_high},
                            "transverse": {"low": crack_transverse_low, "med": crack_transverse_med, "high": crack_transverse_high, "sum" : crack_transverse_low + crack_transverse_med + crack_transverse_high},
                            "cold_joint": {"low": crack_cold_joint_low, "med": crack_cold_joint_med, "high": crack_cold_joint_high , "sum" :crack_cold_joint_low + crack_cold_joint_med + crack_cold_joint_high },
                            "fatigue": {"low": crack_fatigue_low, "med": crack_fatigue_med,  "high": crack_fatigue_high, "sum" :  crack_fatigue_low + crack_fatigue_med + crack_fatigue_high},
                            "patching": {"low": crack_patching_low, "med": crack_patching_med, "high": crack_patching_high, "sum" : crack_patching_low + crack_patching_med + crack_patching_high},
                            "pothole": {"low": crack_pothole_low, "med": crack_pothole_med, "high": crack_pothole_high, "sum" : crack_pothole_low + crack_pothole_med + crack_pothole_high },
                        },
                        "old_score": {"crack": crack_percent,"rutting": rutting, "iri": iri},
                        "old_spi" : {
                            "spi_30" : spi_30 / count,
                            "spi_1" : spi_1/ count,
                            "spi_2" : spi_2/ count,
                            "spi_3" : spi_3 / count,
                        },
                        "new_spi" : { "aci": aci, "lci": lci, "tci": tci, "pati": pati, "ruti": ruti, "cri": cri, "sci": sci, "rci": rci, "spi": spi},
                        "photo_surface": {"surface1": photo_surface[0], "surface2": photo_surface[1] if len(photo_surface) >= 2 else None},
                        "more_info": road_note
                    }
                insert_rows.append(insert_data)
                station += 20
        
            print(f"monitor_id : {monitor_id} | {origin_cnt}개 -> {after_cnt}개 변환")
        
        #print("insert row 수 : " , len(insert_rows))
        
        for doc in insert_rows:     
            check_exist = list(result20.find({"_id" : doc['_id']}))
            if not check_exist: #없으면 새로 inset (check_exist리스트가 empty일 경우)
                result20.insert_one(doc)
                
            else: #이미 저장한 값이면 
                result20.replace_one({'_id': doc['_id']}, doc)

        client.close()
        QMessageBox.about(self, "변환 성공", f"변환 결과 : 총{len(insert_rows)} 항목 변환에 성공하였습니다.")
