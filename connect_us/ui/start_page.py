from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton

class StartPage(QWidget):
    def __init__(self, switch_to_main):
        super().__init__()
        self.switch_to_main = switch_to_main
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("ID")
        layout.addWidget(QLabel("Connect Us"))
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

        self.setLayout(layout)

    def connect(self):
        # 나중에 검증 추가 가능
        self.switch_to_main(self.id_input.text(), self.country_input.text(), self.city_input.text())