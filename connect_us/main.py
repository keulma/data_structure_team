# main.py
import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from PyQt5.QtWidgets import QApplication, QStackedWidget, QDesktopWidget
from PyQt5.QtGui import QIcon

from ui.start_page import StartPage
from ui.main_page import MainPage


class MainApp(QStackedWidget):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon("assets/program_icon.png")) # 프로그램 아이콘 설정 출처 : https://www.flaticon.com/free-icon/social-media_4132666?term=sns&page=3&position=91&origin=search&related_id=4132666

        # 사용자 모니터 해상도 정보 가져오기
        screen_rect = QDesktopWidget().availableGeometry()
        self.screen_width = screen_rect.width()
        self.screen_height = screen_rect.height()

        # start page 크기 설정
        start_width = int(self.screen_width * 0.3)
        start_height = int(self.screen_height * 0.5)

        self.setWindowTitle("CONNECT_US")
        self.setFixedSize(start_width, start_height)
        self.move(
            (self.screen_width - start_width) // 2,
            (self.screen_height - start_height) // 2
        )

        self.start_page = StartPage(self.switch_to_main)
        self.addWidget(self.start_page)  # index 0

        self.main_page = None
        self.setCurrentIndex(0)


    def switch_to_main(self, user_id, country, city):
        user_info = {
            "id": user_id,
            "country": country,
            "city": city
        }


        self.main_page = MainPage(user_info)
        self.addWidget(self.main_page)  # index 1
        self.setCurrentIndex(1)         

        # main page 크기 설정
        main_width = int(self.screen_width * 0.7)
        main_height = int(self.screen_height * 0.7)  

        current_center = self.frameGeometry().center()
        self.setFixedSize(main_width, main_height)
        qr = self.frameGeometry()
        qr.moveCenter(current_center)
        self.move(qr.topLeft())   


    def closeEvent(self, event):    # 종료 시 친구 저장
        if self.main_page:  # 메인페이지까지 진입했을 때만 저장
            self.main_page.save_friends()
        event.accept()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
