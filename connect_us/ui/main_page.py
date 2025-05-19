import os
import json
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
        self.awaiting_location_input = False  # ✅ 지도 클릭 대기 상태

        self.init_ui()
        self.load_friends()     # 친구 목록 불러오기
        self.map_viewer.set_click_callback(self.handle_map_click)

    def init_ui(self):
        layout = QHBoxLayout()

        # ✅ 왼쪽 지도 영역
        self.map_viewer = MapViewer(self.friends)
        layout.addWidget(self.map_viewer, 4)  # 지도는 3 비율

        # ✅ 오른쪽 친구 목록 및 제어 UI
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

        delete_btn = QPushButton("Delete Friend")
        delete_btn.clicked.connect(self.delete_selected_friend)
        right_panel.addWidget(delete_btn)



        upload_btn = QPushButton("Upload KakaoTalk Chat")
        upload_btn.clicked.connect(self.upload_chat)
        right_panel.addWidget(upload_btn)


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


    def closeEvent(self, event):    #종료전에 저장
        self.save_friends()
        event.accept()

    def save_friends(self):
        file_path = os.path.join("users", f"{self.user_info['id']}.json")
        # 파일이 있던 여부에 관계없이 무작위 전체 구조 재정의
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
        # 예시: 바로 친구 추가
        new_friend = Friend("-", "-", "-")
        self.friends.append(new_friend)
        self.update_list()

############

    def start_location_input(self):
        if self.friend_list_widget.currentRow() < 0:
            QMessageBox.warning(self, "경고", "먼저 친구를 선택하세요!")
            return
        self.awaiting_location_input = True
        QMessageBox.information(self, "안내", "지도에서 위치를 클릭하세요 (1회만)")

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

        # ✅ reverse geocode는 약간 지연시켜서 실행 (GUI 끊김 방지)
        def update_country():
            try:
                geolocator = Nominatim(user_agent="friend_map_app")
                location = geolocator.reverse((lat, lng), language='en')
                if location and 'country' in location.raw['address']:
                    friend.country = location.raw['address']['country']
                    print(f"🌍 국가 자동 설정됨: {friend.country}")
            except Exception as e:
                print(f"❌ Reverse geocoding 오류: {e}")
            finally:
                self.update_list()
                QMessageBox.information(self, "입력 완료", f"{friend.name}의 위치가 등록되었습니다!")

        QTimer.singleShot(50, update_country)  # 100ms 후 실행 (메인 루프 잠깐 비우기)


    def rename_selected_friend(self):
        row = self.friend_list_widget.currentRow()
        if row < 0:
            return
        friend = self.friends[row]
        new_name, ok = QInputDialog.getText(self, "이름 변경", "새 이름:", text=friend.name)
        if ok and new_name.strip():
            friend.name = new_name.strip()
            self.update_list()



##############






    def delete_selected_friend(self):
        current = self.friend_list_widget.currentRow()
        if current >= 0:
            del self.friends[current]
            self.update_list()


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
        # ✅ 지도 갱신
        self.map_viewer.update_map()


    def upload_chat(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open KakaoTalk Text", "", "Text Files (*.txt)")
        if path:
            # ✅ 텍스트 분석기 연결
            parse_kakao_txt(path)

            # ✅ 친구별 대화 수 반영
            for friend in self.friends:
                if friend.name in all_conversations:
                    friend.intimacy += all_conversations[friend.name]

            # ✅ 분석 결과 저장
            save_analysis()

            self.update_list()