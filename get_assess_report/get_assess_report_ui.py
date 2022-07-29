import json
import os.path

from PySide6.QtCore import QRect, Qt
from PySide6.QtWidgets import *

class GetAssessReportSeoulUI(object):
    def setupUi(self, window: QDialog, job_name: str):

        window.setWindowTitle("평가자료 산출")  # 창 제목
        window.setFixedSize(460, 130)  # 창 크기
        window.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # 창 크기 고정

        # 과업 명
        self.job_name_label = QLabel(window)
        self.job_name_label.setGeometry(QRect(10, 10, 120, 20))
        self.job_name_label.setText("과업")
        self.job_name_label.setAlignment(Qt.AlignCenter)

        
        self.job_name = QLineEdit(window)
        self.job_name.setGeometry(QRect(140, 10, 240, 20))
        self.job_name.setDisabled(True)
        self.job_name.setText(job_name)
        self.job_name.setAlignment(Qt.AlignCenter)

        # 보고서 형식 선택
        self.job_kind_label = QLabel(window)
        self.job_kind_label.setGeometry(QRect(10, 40, 120, 20))
        self.job_kind_label.setText("분석보고서 형식")
        self.job_kind_label.setAlignment(Qt.AlignCenter)

        ## 보고서 형식 이름
        self.job_kind = QComboBox(window)
        
        ## 설정 파일 불러오기
        with open("assess_file_config.json", encoding='utf-8', errors='ignore') as json_data:
            config_file = json.load(json_data, strict=False)["form"]
        self.job_kind.addItems([x["name"] for x in config_file])
        self.job_kind.setGeometry(QRect(140, 40, 240, 20))
        self.job_kind.setEditable(True)
        line_edit = self.job_kind.lineEdit()
        line_edit.setAlignment(Qt.AlignCenter)
        line_edit.setReadOnly(True)

        # 저장 경로
        self.report_path_label = QLabel(window)
        self.report_path_label.setGeometry(QRect(10, 70, 120, 20))
        self.report_path_label.setText("분석보고서 저장 경로")
        self.report_path_label.setAlignment(Qt.AlignCenter)

        self.report_path = QLineEdit(window)
        self.report_path.setAlignment(Qt.AlignCenter)
        self.report_path.setGeometry(QRect(140, 70, 240, 20))
        self.report_path.setDisabled(True)

        self.find_button = QPushButton(window)
        self.find_button.setGeometry(QRect(390, 70, 60, 20))
        self.find_button.setText("찾기")

        self.execute_button = QPushButton(window)
        self.execute_button.setGeometry(QRect(390, 100, 60, 20))
        self.execute_button.setText("실행")
        self.execute_button.setDisabled(True)
