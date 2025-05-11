# main.py
import sys
from PyQt5.QtWidgets import QApplication, QStackedWidget
from ui.start_page import StartPage
from ui.main_page import MainPage


class MainApp(QStackedWidget):
    def __init__(self):
        super().__init__()

        # StartPage에서 MainPage로 전환하기 위한 콜백 전달
        self.start_page = StartPage(self.switch_to_main)
        self.addWidget(self.start_page)  # index 0

        # MainPage는 로그인 후 생성됨
        self.main_page = None

        self.setWindowTitle("Friend Map Project")
        self.setFixedSize(500, 450)
        self.setCurrentIndex(0)

    def switch_to_main(self, user_id, country, city):
        user_info = {
            "id": user_id,
            "country": country,
            "city": city
        }

        current_center = self.frameGeometry().center()
        self.setFixedSize(700, 500)
        qr = self.frameGeometry()
        qr.moveCenter(current_center)
        self.move(qr.topLeft())

        self.main_page = MainPage(user_info)
        self.addWidget(self.main_page)  # index 1
        self.setCurrentIndex(1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
