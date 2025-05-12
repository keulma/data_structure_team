# main.py
import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
<<<<<<< HEAD
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
=======

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

>>>>>>> 9ffa10a601b3d916fc219b60c77a3f2644bb23c7
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
        self.setFixedSize(1600, 1200)
        self.setCurrentIndex(0)


    def switch_to_main(self, user_id, country, city):
        user_info = {
            "id": user_id,
            "country": country,
            "city": city
        }

        current_center = self.frameGeometry().center()      #창 전환 부드럽게게
        self.setFixedSize(1800, 1200)
        qr = self.frameGeometry()
        qr.moveCenter(current_center)
        self.move(qr.topLeft())

        self.main_page = MainPage(user_info)
        self.addWidget(self.main_page)  # index 1
        self.setCurrentIndex(1)





    def closeEvent(self, event):    # 종료 시(X누름) 친구 저장
        if self.main_page:  # 메인페이지까지 진입했을 때만 저장
            self.main_page.save_friends()
        event.accept()








if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
