import datetime
import json
import os
from collections import defaultdict

import openpyxl
from openpyxl.utils import get_column_letter
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox

import config
from get_assess_report.get_assess_report_ui import GetAssessReportSeoulUI
from calculate_value.spi import calculate_spi_cri, calculate_LrPCI_cri, calculate_LrPCI_cri_with_score


class GetAssessReportSeoul(QDialog, GetAssessReportSeoulUI):
    def __init__(self, job_name):
        QDialog.__init__(self, None, Qt.Dialog)

        # 화면 구성
        self.setupUi(self, job_name)

        # 버튼 구성
        self.find_button.clicked.connect(self.select_save_path)
        self.execute_button.clicked.connect(self.execute_job)

    def select_save_path(self):
        report_path = QFileDialog.getExistingDirectory()
        if report_path:
            self.report_path.setText(report_path)
            self.execute_button.setEnabled(True)
        else:
            self.execute_button.setDisabled(True)

    def execute_job(self):
        return_value = execute_job("2022년_서울시", "서울시 분석보고서", self.report_path.text())
        QMessageBox.about(self, "보고서 저장 성공",
                          f"분석보고서 산출({return_value[0]} 항목)에 성공하였습니다.")

# 과업명, 선택한 보고서 형식, 저장 경로
def execute_job(job_name, job_type, report_path, job=None, suffix="변환_보고서"):
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
    
    #monitor_list = monitor.distinct("monitor_id", {"job_id": job_name}) #아직 안올린 csv파일들있어서 밑에서 오류뜸
    monitor_list = result.distinct("monitor_id", {"job_name": job_name}) #저장된 monitor_id만

    for monitor_id in monitor_list:
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

