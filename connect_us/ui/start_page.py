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

        layout.addSpacing(15)

        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("ID")
        #self.id_input.setFixedWidth(300)
        # layout.addWidget(QLabel("Connect Us"))
        layout.addWidget(self.id_input)

        self.country_input = QLineEdit()
        self.country_input.setPlaceholderText("Country")
        #self.country_input.setFixedWidth(300)
        layout.addWidget(self.country_input)

        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("City")
        #self.city_input.setFixedWidth(300)
        layout.addWidget(self.city_input)

        connect_btn = QPushButton("Connect")
        connect_btn.clicked.connect(self.connect)
        #connect_btn.setFixedWidth(300)
        layout.addWidget(connect_btn)

        ###

        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    def connect(self):
        # 나중에 검증 추가 가능
        self.switch_to_main(self.id_input.text(), self.country_input.text(), self.city_input.text())