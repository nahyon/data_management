from PySide6.QtCore import QRect, Qt
from PySide6.QtWidgets import *
       
####서울시####
class AddResultSeoulUI(object):
    def setupUi(self, window: QDialog, job_name: str):
        window.setWindowTitle("분석 결과 등록 메뉴")  # 창 제목
        window.setFixedSize(470, 160)  # 창 크기
        window.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # 창 크기 고정

        # 과업 이름 표시 - [과업 이름] 칸 ####################
        self.job_name_label = QLabel(window)
        self.job_name_label.setGeometry(QRect(10, 10, 180, 20))
        self.job_name_label.setText("과업 이름")
        self.job_name_label.setAlignment(Qt.AlignCenter)

        self.job_name = QLineEdit(window)
        self.job_name.setGeometry(QRect(200, 10, 180, 20))
        self.job_name.setText(job_name) #job_name : 과업명
        self.job_name.setAlignment(Qt.AlignCenter)
        self.job_name.setDisabled(True)

        # 파일 업로드  - [입력할 분석 보고서 경로(파일)] 칸 ####################
        # 분석 보고서 파일경로 선택 - [입력할 분석 보고서 경로(파일)] 칸 <= [파일 선택]버튼
        self.file_path_label = QLabel(window)
        self.file_path_label.setGeometry(QRect(10, 40, 180, 20))
        self.file_path_label.setText("입력할 분석 보고서 경로(파일)")
        self.file_path_label.setAlignment(Qt.AlignCenter)

        self.file_path = QLineEdit(window)
        self.file_path.setGeometry(QRect(200, 40, 180, 20))
        self.file_path.setAlignment(Qt.AlignCenter)
        self.file_path.setDisabled(True)
        self.file_path.setReadOnly(True)

        # 분석 보고서(파일) 선택 버튼 - [파일 선택] 버튼
        self.file_path_select_button = QPushButton(window)
        self.file_path_select_button.setText("파일 선택")
        self.file_path_select_button.setGeometry(QRect(390, 40, 70, 20))


        # 폴더 업로드  - [입력할 분석 보고서 경로(폴더)] 칸 ####################
        # 분석 보고서 폴더경로 선택 - [입력할 분석 보고서 경로(폴더)] 칸 <= [폴더 선택]버튼
        self.folder_path_label = QLabel(window)
        self.folder_path_label.setGeometry(QRect(10, 70, 180, 20))
        self.folder_path_label.setText("입력할 분석 보고서 경로(폴더)")
        self.folder_path_label.setAlignment(Qt.AlignCenter)

        self.folder_path = QLineEdit(window)
        self.folder_path.setGeometry(QRect(200, 70, 180, 20))
        self.folder_path.setAlignment(Qt.AlignCenter)
        self.folder_path.setDisabled(True)
        self.folder_path.setReadOnly(True)

        # 분석 보고서(폴더) 선택 버튼 - [폴더 선택] 버튼
        self.folder_path_select_button = QPushButton(window)
        self.folder_path_select_button.setText("폴더 선택")
        self.folder_path_select_button.setGeometry(QRect(390, 70, 70, 20))


        # [업로드] 버튼 ####################
        self.upload_result_button = QPushButton(window)
        self.upload_result_button.setText("업로드")
        self.upload_result_button.setGeometry(QRect(390, 100, 70, 20))
        self.upload_result_button.setDisabled(True)

        # [20m변환] 버튼 ####################
        self.upload_result20_button = QPushButton(window)
        self.upload_result20_button.setText("20m변환")
        self.upload_result20_button.setGeometry(QRect(390, 130, 70, 20))
        self.upload_result20_button.setDisabled(True) #