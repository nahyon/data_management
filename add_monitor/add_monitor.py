import json
import re
from datetime import datetime
from decimal import Decimal
from tokenize import Double

import openpyxl
import pymongo
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox
from openpyxl.utils import column_index_from_string

import config
from add_monitor.add_monitor_ui import AddStatusUI


class AddStatus(QDialog, AddStatusUI):
    def __init__(self, job_name):
        QDialog.__init__(self, None, Qt.Dialog)

        with open("monitor_file_config.json", encoding='utf-8', errors='ignore') as f:
            job_kind = json.load(f, strict=False)["form"] #job_kind = 리스트 안 2개 객체 {}, {}
            job_list = [job["name"] for job in job_kind] #job 객체{} 하나씩 -> job_list = "로드텍 현황" , "지역도로 현황"
        # 화면 구성
        self.setupUi(self, job_name, job_list) ##add_monitor_ui.py

        # 버튼 및 동작
        self.find_button.clicked.connect(self.select_path) #[파일 찾기] 버튼
        self.sheet_find_button.clicked.connect(self.find_sheet) #[시트 찾기] 버튼
        self.add_button.clicked.connect(self.add_monitor) #[업로드] 버튼

    def select_path(self): #[파일 찾기]
        report_path = QFileDialog.getOpenFileName()[0] # report_path : 선택한 파일의 전체 절대경로
        if str(report_path).strip(): #(좌우 공백있으면 다 지우고)
            self.report_path.setText(str(report_path).strip()) #[입력할 현황 파일 칸]에 텍스트 set
            #self.add_button.setEnabled(True) #[업로드] 버튼 enable #시트찾기버튼 후로 옮김
            self.sheet_find_button.setEnabled(True) #[시트 찾기] 버튼 enable  #추가함

    def find_sheet(self): #[시트 찾기]
        workbook = openpyxl.load_workbook(self.report_path.text()) # workbook : [파일 찾기]로 세팅한 파일 불러오기
        sheet_names = workbook.get_sheet_names() #모든 시트의 이름이 담긴 리스트 불러옴 (Sheet1, Sheet2같은)
        self.sheet_name.addItems(sheet_names) # sheet_name : 시트 이름들로 목록 채움
        workbook.close()
        self.add_button.setEnabled(True) #[업로드] 버튼 enable 

    def add_monitor(self): #[업로드]
        # 현황 파일(엑셀) 불러옴
        workbook = openpyxl.load_workbook(self.report_path.text()) # workbook : [파일 찾기]로 선택한 현황 파일(엑셀)
        with open("monitor_file_config.json", encoding='utf-8', errors='ignore') as f:
            job_kind = json.load(f, strict=False)["form"]
            for job in job_kind:
                if job["name"] == self.job_kind.currentText(): # 선택한 형식에 따라 start_row, row_content 설정
                    start_row = job["start_row"] # start_row : 실제데이터는 6번재 row부터 존재
                    row_content = job["row"] # row_content : 컬럼들 (필요x컬럼은 None으로 표기됨)
        worksheet = workbook[self.sheet_name.currentText()] # worksheet : 선택한 현황파일(workbook) - 선택한 시트
        monitor_list = []
        for row_index, row in enumerate(worksheet.rows):
            if row_index >= start_row - 1: #(실제데이터 있는 부분부터)
                #print("현재 읽는 줄 : ", row_index+1, " ----------------")
                row_data = self.get_monitor_row_value_local(row, row_content) #시트 한 줄씩 필요컬럼들 읽기
                if row_data == "continue" : # monitor_id가 '-'로 되어있는 경우, 담당업체 '아이리스'인 경우
                    #print("continue")
                    continue #monitor_list에 추가하지않고 다음 row읽으러 continue
                if row_data is None or row_data[4] is None: #([4] 노선번호?인듯)
                    break
                monitor_list.append(row_data)
                #print("len(monitor_list) : ",len(monitor_list))
        workbook.close()
        # 엑셀 파일 닫음 

        # DB업로드 ########################
        client = config.get_client()
        database = client[config.database_name] #[Roadtechh]DB의 : database
        collection = database["monitor"]        #"monitor" table : collection
        for monitor in monitor_list:
            line_id, section_id, province_id, city_id, road_level, road_name, heading, track, monitor_id, start_location, \
                end_location, monitor_start_station, monitor_end_station, source_id, monitor_date, \
                source_start_station, source_end_station = monitor
            
            if isinstance(monitor_start_station,float) : #변환 시 3.02 -> (3020,0)과 같이 튜플로 변함. length=1 
                monitor_start_station = int(round(float(monitor_start_station * 1000), -1))
                if isinstance(monitor_start_station,tuple) : # 0(원래 int)도 tuple로 변하는 현상 발생..
                    monitor_start_station = monitor_start_station[0]
            if isinstance(monitor_end_station,float) : 
                monitor_end_station = int(round(float(monitor_end_station * 1000), -1))
                if isinstance(monitor_end_station,tuple) : 
                    monitor_end_station = monitor_end_station[0]
            if isinstance(source_start_station,float) : 
                source_start_station = int(round(float(source_start_station * 1000), -1))
                if isinstance(source_start_station,tuple) : 
                    source_start_station = source_start_station[0]
            if isinstance(source_end_station,float) :
                source_end_station = int(round(float(source_end_station * 1000), -1))
                if isinstance(source_end_station,tuple) : 
                    source_end_station = source_end_station[0]


            if section_id:
                monitor_dict = {
                    "_id": f"{self.job_name.text()}_{monitor_id}_{source_id}_{monitor_start_station}_{monitor_end_station}",
                    "job_id": self.job_name.text(), "line_id": line_id, "section_id": section_id,
                    "province_id": province_id, "city_id": city_id,
                    "road_level": road_level,
                    "road_name": road_name, "heading": heading,
                    "track": track, "monitor_id": monitor_id, "start_location": start_location,
                    "end_location": end_location,
                    "monitor_start_station": monitor_start_station, "monitor_end_station": monitor_end_station,
                    "source_id": source_id, "monitor_date": monitor_date,
                    "source_start_station": source_start_station, "source_end_station": source_end_station
                }
            else:
                if self.job_name.text() == '2022년_서울시' :
                    monitor_dict = {
                        "_id": f"{self.job_name.text()}_{monitor_id}_{source_id}_{monitor_start_station}_{monitor_end_station}",
                        "compare_id" : f"{road_name}({line_id})_{heading[0]}_{track}",
                        "job_id": self.job_name.text(), "line_id": line_id, "road_level": road_level,  "road_name": road_name, "heading": heading,
                        "track": track, "monitor_id": monitor_id, "start_location": start_location, "end_location": end_location,
                        "monitor_start_station": monitor_start_station, "monitor_end_station": monitor_end_station,
                        "source_id": source_id, "monitor_date": monitor_date,
                        "source_start_station": source_start_station, "source_end_station": source_end_station
                    }
                else :
                    monitor_dict = {
                        "_id": f"{self.job_name.text()}_{monitor_id}_{source_id}_{monitor_start_station}_{monitor_end_station}",
                        "job_id": self.job_name.text(), "line_id": line_id, "road_level": road_level,  "road_name": road_name, "heading": heading,
                        "track": track, "monitor_id": monitor_id, "start_location": start_location, "end_location": end_location,
                        "monitor_start_station": monitor_start_station, "monitor_end_station": monitor_end_station,
                        "source_id": source_id, "monitor_date": monitor_date,
                        "source_start_station": source_start_station, "source_end_station": source_end_station
                    }
            
            check_exist = list(collection.find({"_id" : monitor_dict['_id']}))
            if not check_exist: #없으면 새로 inset (check_exist리스트가 empty일 경우)
                collection.insert_one(monitor_dict)
            else: #이미 저장한 값이면 
                collection.replace_one({'_id': monitor_dict['_id']}, monitor_dict)

        client.close()
        QMessageBox.about(self, "현황 등록 성공", f"{len(monitor_list)}개의 현황을 성공적으로 입력했습니다.")

    # 현황 시트 줄 읽는 함수
    @staticmethod
    def get_monitor_row_value_local(row, row_content: list):
        row_data = [cell.value for cell in row[:len(row_content)]]
        #변수들 None으로 초기화
        line_id, section_id, province_id, city_id, road_level, road_name, heading, track, monitor_id, start_location, \
            end_location, monitor_start_station, monitor_end_station, source_id, monitor_date, \
            source_start_station, source_end_station = None, None, None, None, \
            None, None, None, None, None, None, None, None, None, None, None, None, None
        for cell_index, cell_value in enumerate(row_content):
            if cell_value == "None":
                continue
            elif cell_value == "line_id":
                line_id = row_data[cell_index]
            elif cell_value == "road_level":
                road_level = row_data[cell_index]
            elif cell_value == "road_name":
                road_name = row_data[cell_index]
            elif cell_value == "heading":
                heading = row_data[cell_index]
            elif cell_value == "track":
                track = row_data[cell_index]
            elif cell_value == "monitor_id":
                monitor_id = row_data[cell_index]
            elif cell_value == "start_location":
                start_location = row_data[cell_index]
            elif cell_value == "end_location":
                end_location = row_data[cell_index]
            elif cell_value == "monitor_start_station":
                monitor_start_station = row_data[cell_index]
            elif cell_value == "monitor_end_station":
                monitor_end_station = row_data[cell_index]
            elif cell_value == "source_id":
                source_id = row_data[cell_index]
            elif cell_value == "monitor_date":
                monitor_date = row_data[cell_index]
            elif cell_value == "source_start_station":
                source_start_station = row_data[cell_index]
                # source 시/종 station 이 "-"으로 되어있는 경우 None으로 DB저장
                # if source_start_station == "-" :
                #     source_start_station = None
            elif cell_value == "source_end_station":
                source_end_station = row_data[cell_index]
                # source 시/종 station 이 "-"으로 되어있는 경우 None으로 DB저장
                # if source_end_station == "-" :
                #     source_end_station = None
            elif cell_value == "section_id":
                section_id = row_data[cell_index]
            elif cell_value == "province_id":
                province_id = row_data[cell_index]
            elif cell_value == "city_id":
                city_id = row_data[cell_index]
        if monitor_id is None:
            return None
        
        # 현황에 ID가 "-"로 되어있는 경우 : 사용X
        if monitor_id == "-" :
            return "continue" #밑에 식으로 더 이상 가지x
        # source_시/종_ station이 "-"으로 되어있는 경우 DB에 저장x / None인 경우도 DB저장x
        if source_start_station == "-" or source_end_station == "-" or source_start_station is None and source_end_station is None :
            return "continue"
        # 담당업체가 '아이리스'인 경우 DB에 저장x 
        if row_data[0] == "아이리스" :
            return "continue"
        
        #STA시점, 종점 km -> m단위 변경
        if source_start_station is not None and source_end_station is not None:
            source_start_station = round(int(Decimal(source_start_station) * 1000), -1)
            source_end_station = round(int(Decimal(source_end_station) * 1000), -1)
            
        if monitor_start_station is not None and monitor_end_station is not None:
            monitor_start_station = round(int(Decimal(monitor_start_station) * 1000), -1)
            monitor_end_station = round(int(Decimal(monitor_end_station) * 1000), -1)
        elif source_start_station is not None and source_end_station is not None:
            monitor_start_station = 0
            monitor_end_station = source_end_station - source_start_station

        # 조사일자가 표시되어 있다면
        if str(monitor_date).isdigit():
            monitor_date = str(monitor_date)
            monitor_date = datetime.strptime(f"20{monitor_date[:2]}-{monitor_date[2:4]}-{monitor_date[4:]}", "%Y-%m-%d")

        # 차선에 _ 있는 경우
        if "_" in str(track):
            track = str(track)[0]
            
        # 현황에 조사자가 없네요 ㅠㅠ
        if monitor_id is None:
            monitor_id = f"{line_id}_{heading}{track}"
            
        return line_id, section_id, province_id, city_id, road_level, road_name, heading, str(track), monitor_id, start_location, \
            end_location, monitor_start_station, monitor_end_station, source_id, monitor_date, \
            source_start_station, source_end_station
