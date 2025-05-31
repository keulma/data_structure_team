#main_page.py

import os, json, datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QComboBox, QFileDialog, QLabel, QMessageBox, QInputDialog
)
from PyQt5.QtCore import QTimer
from geopy.geocoders import Nominatim

from data.friend import Friend
from map_viewer import MapViewer

from kakaotalk.text_analyze import parse_kakao_txt, all_conversations, save_analysis



class MainPage(QWidget):
    def __init__(self, user_info):
        super().__init__()
        self.user_info = user_info
        self.friends = []
        self.awaiting_location_input = False  # 지도 클릭 대기 상태

        self.init_ui()
        self.load_friends()     # 친구 목록 불러오기
        self.map_viewer.set_click_callback(self.handle_map_click)
        self.save_friends()     # 데이터 저장

    def init_ui(self):
        layout = QHBoxLayout()

        # 지도
        self.map_viewer = MapViewer(self.friends, self.user_info)
        layout.addWidget(self.map_viewer, 4)  # 지도 3 비율

        # 친구 목록, UI
        right_panel = QVBoxLayout()

        self.friend_list_widget = QListWidget()
        right_panel.addWidget(QLabel("Friend List"))
        right_panel.addWidget(self.friend_list_widget)

        self.sort_box = QComboBox()
        self.sort_box.addItems(["Alphabet", "Registration", "Intimacy"])
        self.sort_box.currentTextChanged.connect(self.sort_friends)
        right_panel.addWidget(self.sort_box)

        add_btn = QPushButton("Add Friend")
        add_btn.clicked.connect(self.add_friend_dialog)
        right_panel.addWidget(add_btn)

        rename_btn = QPushButton("이름 설정(변경)")
        rename_btn.clicked.connect(self.rename_selected_friend)
        right_panel.addWidget(rename_btn)

        location_btn = QPushButton("위치 입력")
        location_btn.clicked.connect(self.start_location_input)
        right_panel.addWidget(location_btn)


        self.period_box = QComboBox()
        self.period_box.addItems(["오늘", "1일", "1주일", "1개월", "1년"])
        self.period_box.currentTextChanged.connect(self.apply_period)
        right_panel.addWidget(QLabel("분석 기간"))
        right_panel.addWidget(self.period_box)
        self.selected_period = "오늘"  # 기본값 - 오늘로 설정

        upload_btn = QPushButton("Upload KakaoTalk Chat")
        upload_btn.clicked.connect(self.upload_chat)
        right_panel.addWidget(upload_btn)


        delete_btn = QPushButton("Delete Friend")
        delete_btn.clicked.connect(self.delete_selected_friend)
        right_panel.addWidget(delete_btn)


        layout.addLayout(right_panel, 1)
        self.setLayout(layout)


    def load_friends(self):
        file_path = os.path.join("users", f"{self.user_info['id']}.json")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                friends_data = data.get("friends", [])
                self.friends = [Friend.from_dict(fd) for fd in friends_data]
                self.update_list()
        self.map_viewer.friends = self.friends
        self.map_viewer.update_map()


    def closeEvent(self, event):    
        self.save_friends()
        event.accept()

    def save_friends(self):
        file_path = os.path.join("users", f"{self.user_info['id']}.json")
        # 재정의
        data = {
            "user": [
                self.user_info["id"],
                self.user_info["country"],
                self.user_info["city"]
            ],
            "friends": [f.to_dict() for f in self.friends]
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


    def add_friend_dialog(self):
        # 친구 추가
        new_friend = Friend("-", "-", "-")
        self.friends.append(new_friend)
        self.update_list()
        self.save_friends()     # 데이터 저장

    def start_location_input(self):
        if self.friend_list_widget.currentRow() < 0:
            QMessageBox.warning(self, "경고", "먼저 친구를 선택하세요!")
            return
        self.awaiting_location_input = True
        QMessageBox.information(self, "안내", "지도에서 위치를 클릭하세요 (1회만)")
        self.save_friends()     # 데이터 저장


    def handle_map_click(self, lat, lng):
        if not self.awaiting_location_input:
            return

        current_row = self.friend_list_widget.currentRow()
        if current_row < 0:
            return

        friend = self.friends[current_row]
        friend.x = lat
        friend.y = lng
        self.awaiting_location_input = False
        self.map_viewer.friends = self.friends

        # reverse geocode 지연 실행 (GUI 끊김 이슈)
        def update_country():
            try:
                geolocator = Nominatim(user_agent="friend_map_app")
                location = geolocator.reverse((lat, lng), language='en', timeout = 1)
                if location and 'country' in location.raw['address']:
                    friend.country = location.raw['address']['country']
                    print(f"Country select: {friend.country}")
            except Exception as e:
                print(f"Reverse geocoding error: {e}")
            finally:
                self.update_list()
                QMessageBox.information(self, "input finish", f"{friend.name} location set")
        
        QTimer.singleShot(50, update_country)  # 100ms 후 실행
        self.save_friends()     # 데이터 저장


    def rename_selected_friend(self):
        row = self.friend_list_widget.currentRow()
        if row < 0:
            return
        friend = self.friends[row]
        new_name, ok = QInputDialog.getText(self, "이름 변경", "새 이름:", text=friend.name)
        if ok and new_name.strip():
            friend.name = new_name.strip()
            self.update_list()
        self.save_friends()     # 데이터 저장

    def delete_selected_friend(self):
        current = self.friend_list_widget.currentRow()
        if current >= 0:
            del self.friends[current]
            self.update_list()
        self.save_friends()     # 데이터 저장


    def sort_friends(self, mode):
        if mode == "Alphabet":
            self.friends.sort(key=lambda f: f.name)
        elif mode == "Registration":
            self.friends.sort(key=lambda f: f.registered_at)
        elif mode == "Intimacy":
            self.friends.sort(key=lambda f: -f.intimacy)
        self.update_list()


    def update_list(self):
        self.friend_list_widget.clear()
        for i, f in enumerate(self.friends, 1):
            self.friend_list_widget.addItem(f"{i}. {f.country}, {f.name}, ❤️{f.intimacy}")
        # 지도 갱신
        self.map_viewer.update_map()


    def upload_chat(self):
        row = self.friend_list_widget.currentRow()
        if row < 0:
            QMessageBox.warning(self, "경고", "먼저 친구를 선택하세요!")
            return

        path, _ = QFileDialog.getOpenFileName(self, "Open KakaoTalk Text", "", "Text Files (*.txt)")
        if path:
            parse_kakao_txt(path)
            friend = self.friends[row]
            friend.chat_history = dict(all_conversations)  # 날짜별 메시지 수 저장

            # intimacy 계산
            today = datetime.date.today()
            period = self.selected_period
            count = 0

            for date_str, num in friend.chat_history.items():
                date_obj = datetime.date.fromisoformat(date_str)
                delta = (today - date_obj).days

                if period == "오늘" and delta == 0:
                    count += num
                elif period == "1일" and delta <= 1:
                    count += num
                elif period == "1주일" and delta <= 7:
                    count += num
                elif period == "1개월" and delta <= 30:
                    count += num
                elif period == "1년" and delta <= 365:
                    count += num

            friend.intimacy = count  # 선택된 분석 기간 기준으로 반영

            self.save_friends()
            self.update_list()



    def apply_period(self, period):
        self.selected_period = period
        self.map_viewer.selected_period = period  
        self.map_viewer.update_map()
        
        today = datetime.date.today()

        for friend in self.friends:
            if not hasattr(friend, "chat_history") or not friend.chat_history:
                continue  # 대화 기록이 없는 경우 패스

            count = 0
            for date_str, num in friend.chat_history.items():
                date_obj = datetime.date.fromisoformat(date_str)
                delta = (today - date_obj).days

                if period == "오늘" and delta == 0:
                    count += num
                elif period == "1일" and delta <= 1:
                    count += num
                elif period == "1주일" and delta <= 7:
                    count += num
                elif period == "1개월" and delta <= 30:
                    count += num
                elif period == "1년" and delta <= 365:
                    count += num

            friend.intimacy = count  # 기존 친밀도 재계산

        self.save_friends()
        self.update_list()