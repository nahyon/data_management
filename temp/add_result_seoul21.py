# 2021 통판 자료.xlsx에서 입력 
from tracemalloc import start
import openpyxl
#import config
import os
import re

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


client = get_client()
database = client[database_name]

monitor = database["monitor"]
result = database["result20"]

# monitor
'''
info_file =  'Z:\\## DBMS 전체자료\\####2022서울시작업\\분석보고서 서식.xlsx'
info_sheet = '참조.시도노선'

#info file
seoulinfo_list = dict()
seoul21_workbook = openpyxl.load_workbook(seoul21_file)
seoul21_worksheet = seoul21_workbook[seoul21_sheet]
seoul21all_list = dict()
for row_index, row in enumerate(seoul21_worksheet.rows):
    if row_index >= 1:
        line_id, road_level, heading, track = row[5].value, row[7].value, row[9].value, row[10].value, row[11].value,
'''


# result20
#seoul21_file = 'Z:\\## DBMS 전체자료\\####2022서울시작업\\2021년 서울시 20m 통판.xlsx'

file1 = 'Z:\\## DBMS 전체자료\\####2022서울시작업\\2021년 서울시 20m 통판-1.xlsx'
file2 = 'Z:\\## DBMS 전체자료\\####2022서울시작업\\2021년 서울시 20m 통판-2.xlsx'
file3 = 'Z:\\## DBMS 전체자료\\####2022서울시작업\\2021년 서울시 20m 통판-3.xlsx'
file4 = 'Z:\\## DBMS 전체자료\\####2022서울시작업\\2021년 서울시 20m 통판-4.xlsx'
file5 = 'Z:\\## DBMS 전체자료\\####2022서울시작업\\2021년 서울시 20m 통판-5.xlsx'
file6 = 'Z:\\## DBMS 전체자료\\####2022서울시작업\\2021년 서울시 20m 통판-6.xlsx'
file7 = 'Z:\\## DBMS 전체자료\\####2022서울시작업\\2021년 서울시 20m 통판-7.xlsx'





seoul21_sheet = '20mDATA'
def read_file() :
    line_list = monitor.aggregate(
        [
            {"$match": {"job_id": '2022년_서울시'}},
            {"$group": {
                "_id":  "$line_id",
                "count" : {"$sum" : 1}
            }},
            {"$sort" : {"line_id" : 1}},
        ]
    )
    
    lines = []
    for a_line in line_list :
        line_id = a_line['_id']
        lines.append(line_id)
    lines = sorted(lines, key=lambda x: int(x))
    print("lines : ", lines)
    print()

    #엑셀 파일 읽기
    seoul21_workbook = openpyxl.load_workbook(file7) #file22 file46  #file51
    seoul21_worksheet = seoul21_workbook[seoul21_sheet]
    seoul21all_list = dict()
    insert_rows = []
    
    
    
    pass_cnt = 0
    for row_index, row in enumerate(seoul21_worksheet.rows):
        if row_index <3 :
            continue
        else : # row_index >= 3
            #job_name = "2021년_서울시"
            id, monitor_date, line_id, road_name, road_level, heading, track = row[0].value, row[5].value, row[7].value, row[9].value, row[10].value, row[11].value, row[12].value
            #line_id가 str이 아닌 int로 나온다.
            #lines배열에는 모두 str형태
            
            #if str(line_id) not in lines :  #2022_서울시에 존재하는 line_id에 대해서만 데이터 가져옴 
            #    pass_cnt += 1
            #    continue
            print("현재 읽고있는 노선 id  : " , str(line_id))
            
            road_level = road_level+'도로'
            station = id.split("_")[3] # == row[13].value # start station
            station = int(station)
            compare_id = f"{road_name}({line_id})_{heading[0]}_{track}"
            
            #초기화
            crack_longitudinal_low, crack_longitudinal_med, crack_longitudinal_high, crack_longitudinal_sum,\
            crack_transverse_low, crack_transverse_med, crack_transverse_high, crack_transverse_sum,\
            crack_cold_joint_low, crack_cold_joint_med, crack_cold_joint_high, crack_cold_joint_sum,\
            crack_fatigue_low, crack_fatigue_med, crack_fatigue_high, crack_fatigue_sum, \
            crack_patching_sum,\
            crack_pothole_sum, \
            width, area, crack_percent, rutting, iri,\
            spi_1, spi_2, spi_3, spi_30 , \
            aci, lci, tci, pati, ruti, cri, sci, rci, spi, \
            road_note, photo_surface1, photo_surface2= \
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,0.0, 0.0, 0.0,0.0, 0.0, 0.0,0.0, 0.0,\
            0.0,0.0, 0.0, 0.0, 0,\
            0.0, 0.0, 0.0, 0.0, \
            0.0, 0.0, 0.0,0.0, 0.0, 0.0,0.0, 0.0, 0.0, "", "", ""
            
            #info : 총 39개
            '''
            info = [crack_longitudinal_low, crack_longitudinal_med, crack_longitudinal_high, crack_longitudinal_sum,
            crack_transverse_low, crack_transverse_med, crack_transverse_high, crack_transverse_sum,
            crack_cold_joint_low, crack_cold_joint_med, crack_cold_joint_high, crack_cold_joint_sum,
            crack_fatigue_low, crack_fatigue_med, crack_fatigue_high, crack_fatigue_sum, 
            crack_patching_sum,
            crack_pothole_sum, 
            width, area, crack_percent, rutting, iri,
            spi_1, spi_2, spi_3, spi_30 , 
            aci, lci, tci, pati, ruti, cri, sci, rci, spi, 
            road_note, photo_surface1, photo_surface2]
            '''            
            
            
            data = []
            for idx in range(39) :
                value = row[idx+15].value
                if idx <= 35 : #road_note 인덱스 = 36 (36+15 = 51 (엑셀))
                    if not isinstance(value,float) : #float형 아니면
                        value = float(value)
                data.append(value)
            
            crack_longitudinal_low, crack_longitudinal_med, crack_longitudinal_high, crack_longitudinal_sum,\
            crack_transverse_low, crack_transverse_med, crack_transverse_high, crack_transverse_sum,\
            crack_cold_joint_low, crack_cold_joint_med, crack_cold_joint_high, crack_cold_joint_sum,\
            crack_fatigue_low, crack_fatigue_med, crack_fatigue_high, crack_fatigue_sum, \
            crack_patching_sum,\
            crack_pothole_sum, \
            width, area, crack_percent, rutting, iri,\
            spi_1, spi_2, spi_3, spi_30 , \
            aci, lci, tci, pati, ruti, cri, sci, rci, spi, \
            road_note, photo_surface1, photo_surface2 = data
            
            
            

        job_name = "2021년_서울시"
        insert_data = {"_id": f"{job_name}_{compare_id}_{station}",
                "job_name": job_name, "compare_id" : compare_id,
                "station": {"start": station, "end": station+20}, "width": width, "area" : area,
                "crack": {
                    "longitudinal": {"low": crack_longitudinal_low, "med": crack_longitudinal_med, "high": crack_longitudinal_high, "sum" : crack_longitudinal_sum},
                    "transverse": {"low": crack_transverse_low, "med": crack_transverse_med, "high": crack_transverse_high, "sum" :crack_transverse_sum},
                    "cold_joint": {"low": crack_cold_joint_low, "med": crack_cold_joint_med, "high": crack_cold_joint_high , "sum" :crack_cold_joint_sum },
                    "fatigue": {"low": crack_fatigue_low, "med": crack_fatigue_med,  "high": crack_fatigue_high, "sum" :  crack_fatigue_sum},
                    "patching": {"sum" : crack_patching_sum},
                    "pothole": {"sum" : crack_pothole_sum },
                },
                "old_score": {"crack": crack_percent,"rutting": rutting, "iri": iri},
                "old_spi" : {
                    "spi_30" : spi_30,
                    "spi_1" : spi_1,
                    "spi_2" : spi_2,
                    "spi_3" : spi_3,
                },
                "new_spi" : { "aci": aci, "lci": lci, "tci": tci, "pati": pati, "ruti": ruti, "cri": cri, "sci": sci, "rci": rci, "spi": spi},
                "photo_surface": {"surface1":photo_surface1, "surface2": photo_surface2},
                "more_info": road_note
            }
        insert_rows.append(insert_data)
    
    seoul21_workbook.close()
    
    for doc in insert_rows:     
        check_exist = list(result.find({"_id" : doc['_id']}))
        if not check_exist: #없으면 새로 inset (check_exist리스트가 empty일 경우)
            result.insert_one(doc)
            
        else: #이미 저장한 값이면   
            result.replace_one({'_id': doc['_id']}, doc)

    print("DB에 저장된 row 수 (=엑셀에서 읽은 row 수): ",len(insert_rows))
    print("넘어간 노선 횟수: ", pass_cnt)
    client.close()

read_file()