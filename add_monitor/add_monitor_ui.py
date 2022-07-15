from PySide6.QtCore import QRect, Qt
from PySide6.QtWidgets import *

##과업 현황 입력##
class AddStatusUI(object):
    def setupUi(self, window: QDialog, job_name: str, job_kind=None):

        if job_kind is None:
            job_kind = []
        window.setWindowTitle("현황 등록 메뉴")  # 창 제목
        window.setFixedSize(470, 160)  # 창 크기
        window.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # 창 크기 고정

        # [과업 선택] 칸 ####################
        self.job_name_label = QLabel(window)
        self.job_name_label.setGeometry(QRect(10, 10, 120, 20))
        self.job_name_label.setText("과업 선택")
        self.job_name_label.setAlignment(Qt.AlignCenter)

        self.job_name = QLineEdit(window)
        self.job_name.setGeometry(QRect(140, 10, 240, 20))
        self.job_name.setDisabled(True)
        self.job_name.setText(job_name) #job_name : 과업명

        # 현황 종류
        self.job_kind_label = QLabel(window)
        self.job_kind_label.setGeometry(QRect(10, 40, 120, 20))
        self.job_kind_label.setText("입력할 현황의 형식")
        self.job_kind_label.setAlignment(Qt.AlignCenter)

        # 과업 선택 - [입력할 현황의 형식] 칸 ####################
        self.job_kind = QComboBox(window)
        self.job_kind.setGeometry(QRect(140, 40, 240, 20))
        self.job_kind.addItems(job_kind) #job_kind : "로드텍 현황" , "지역도로 현황"

        # [입력할 현황 파일] 칸 ####################
        # 보고서 경로 선택 - [입력할 현황 파일] 칸 <= [파일 찾기]버튼
        self.report_path_label = QLabel(window)
        self.report_path_label.setGeometry(QRect(10, 70, 120, 20))
        self.report_path_label.setText("입력할 현황 파일")
        self.report_path_label.setAlignment(Qt.AlignCenter)

        self.report_path = QLineEdit(window)
        self.report_path.setGeometry(QRect(140, 70, 240, 20))
        self.report_path.setDisabled(True)

        # 현황 파일 선택 버튼 - [파일 찾기] 버튼
        self.find_button = QPushButton(window)
        self.find_button.setGeometry(QRect(400, 70, 60, 20))
        self.find_button.setText("파일 찾기")

        # [입력할 시트 이름] 칸 ####################
        # 시트 이름 선택 - [입력할 시트 이름] 칸 <= [시트 찾기]버튼
        self.sheet_name_label = QLabel(window)
        self.sheet_name_label.setGeometry(QRect(10, 100, 120, 20))
        self.sheet_name_label.setText("입력할 시트 이름")
        self.sheet_name_label.setAlignment(Qt.AlignCenter)

        self.sheet_name = QComboBox(window) #엑셀파일의 시트 이름들
        self.sheet_name.setGeometry(QRect(140, 100, 240, 20))

        # 현황 파일 선택 버튼 - [시트 찾기] 버튼
        self.sheet_find_button = QPushButton(window)
        self.sheet_find_button.setGeometry(QRect(400, 100, 60, 20))
        self.sheet_find_button.setText("시트 찾기")
        self.sheet_find_button.setDisabled(True) #파일찾기 버튼 후 활성화하기

        
        # [업로드] 버튼 ####################
        # 업로드 버튼 - [업로드] 버튼
        self.add_button = QPushButton(window)
        self.add_button.setGeometry(QRect(400, 130, 60, 20))
        self.add_button.setText("업로드")
        self.add_button.setDisabled(True)
