# start_page

import os
import json
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class StartPage(QWidget):
    def __init__(self, switch_to_main):
        super().__init__()
        self.switch_to_main = switch_to_main
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()


        # connect-us 표지 이미지 추가 
        image_label = QLabel()
        image_label.setPixmap(QPixmap("assets/connect-us_image.png"))
        image_label.setScaledContents(True)
        image_label.setFixedHeight(300)  # 적절한 높이로 조절
        layout.addWidget(image_label)

        layout.addSpacing(15)   #공백 띄우기

        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("ID")

        layout.addWidget(self.id_input)

        self.country_input = QLineEdit()
        self.country_input.setPlaceholderText("Country")
        layout.addWidget(self.country_input)

        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("City")
        layout.addWidget(self.city_input)

        connect_btn = QPushButton("Connect")
        connect_btn.clicked.connect(self.connect)
        layout.addWidget(connect_btn)

        ###

        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    def connect(self):
        user_id = self.id_input.text().strip()  
        if not user_id:    #사용자 ID 입력이 공백이면 종료
            return

        os.makedirs("users", exist_ok=True)
        file_path = os.path.join("users", f"{user_id}.json")        #users/ 디렉토리 생성 (이미 있으면 넘어감)

        # 🟨 저장된 유저가 있다면 → 불러오기
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                user_info = data["user"]  # 배열: [id, country, city]
        else:
            # 🟩 없다면 → 새로 저장
            user_info = [
                user_id,
                self.country_input.text().strip(),
                self.city_input.text().strip()
            ]
            with open(file_path, "w", encoding="utf-8") as f:       #저장장
                json.dump({ "user": user_info }, f, ensure_ascii=False, indent=2)

        # → 다음 페이지로 넘어감
        self.switch_to_main(*user_info)