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
        self.interaction_sort()
        self.all_calculate_intimacy()

    def init_ui(self):
        layout = QHBoxLayout()

        # 지도
        self.map_viewer = MapViewer(self.friends, self.user_info)
        layout.addWidget(self.map_viewer, 4)  # 지도 4 비율

        # 친구 목록, UI
        right_panel = QVBoxLayout()

        self.friend_list_widget = QListWidget()
        self.friend_list_widget.setStyleSheet("font-size: 15px;")
        right_panel.addWidget(QLabel("Friend List"))
        right_panel.addWidget(self.friend_list_widget)

        self.sort_box = QComboBox()
        self.sort_box.addItems(["이름순", "등록순", "친밀도순"])
        self.sort_box.currentTextChanged.connect(self.sort_friends)
        right_panel.addWidget(self.sort_box)

        add_btn = QPushButton("친구 추가")
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
        self.period_box.currentTextChanged.connect(self.select_period)
        right_panel.addWidget(QLabel("분석 기간"))
        right_panel.addWidget(self.period_box)
        self.selected_period = "오늘"  # 기본값 - 오늘로 설정

        upload_btn = QPushButton("Upload KakaoTalk Chat")
        upload_btn.clicked.connect(self.upload_chat)
        right_panel.addWidget(upload_btn)


        delete_btn = QPushButton("친구 삭제")
        delete_btn.clicked.connect(self.delete_selected_friend)
        right_panel.addWidget(delete_btn)


        help_btn = QPushButton("도움말")  
        help_btn.clicked.connect(self.show_help_dialog)
        right_panel.addWidget(help_btn)

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




    #버튼들
    def add_friend_dialog(self):
        # 친구 추가
        new_friend = Friend("-", "-", "-")
        self.friends.append(new_friend)
        self.update_list()
        self.interaction_sort()
        # 생성이므로 친밀도 X

    def rename_selected_friend(self):
        row = self.friend_list_widget.currentRow()
        if row < 0:
            QMessageBox.warning(self, "경고", "먼저 친구를 선택하세요!")
            return
        friend = self.friends[row]
        new_name, ok = QInputDialog.getText(self, "이름 변경", "새 이름:", text=friend.name)
        if ok and new_name.strip():
            friend.name = new_name.strip()
            self.update_list()
        self.interaction_sort()
        # 친밀도 관련 X

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
        self.map_viewer.friends = self.friends

        # reverse geocode 지연 실행 (GUI 끊김 이슈)
        def update_country():
            try:
                geolocator = Nominatim(user_agent="friend_map_app")
                location = geolocator.reverse((lat, lng), language='en', timeout = 3)
                if location and 'country' in location.raw['address']:
                    friend.country = location.raw['address']['country']
                    print(f"Country select: {friend.country}")
            except Exception as e:
                print(f"Reverse geocoding error: {e}")
            finally:
                self.interaction_sort()
                # 친밀도 관련 X
                QMessageBox.information(
                self,
                "완료",
                f"<div align='center'>{friend.name} : {friend.country}<br>위치 저장 완료</div>"
)
        
        QTimer.singleShot(50, update_country)  # 50ms 후 실행
    

    def update_list(self):
        self.friend_list_widget.clear()
        for i, f in enumerate(self.friends, 1):
            self.friend_list_widget.addItem(
                f"{i}. {f.name}\n국가: {f.country}  |  ❤️{f.intimacy}"
            )
        # 지도 갱신
        self.map_viewer.update_map()

    def select_period(self, period):
        self.selected_period = period
        self.map_viewer.selected_period = period
        self.all_calculate_intimacy()   # 목록 내 친구 전부에 대한 친밀도 값 최신화
        self.interaction_sort()
        self.map_viewer.update_map() # 친밀도 선 굵기 변경
        
        

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

            self.calculate_intimacy(friend)  # 1명에 대한 대화 파일만 업로드 하므로 그 사람에 대한 것만 계산(최적화화)
            self.interaction_sort()  
            self.map_viewer.update_map() # 친밀도 선 굵기 변경


    def delete_selected_friend(self):
        row = self.friend_list_widget.currentRow()
        if row < 0:
            QMessageBox.warning(self, "경고", "먼저 친구를 선택하세요!")
            return
        current = self.friend_list_widget.currentRow()
        if current >= 0:
            del self.friends[current]
            self.update_list()
            self.interaction_sort()
            self.map_viewer.update_map() # 친밀도 선 굵기 변경


    def show_help_dialog(self):  # ❗ 도움말 다이얼로그 정의
        help_text = (
            "# 정렬 기준: 이름순, 등록순, 친밀도순 중 선택 \n"
            "# 친구 추가: 친구 추가 버튼 --> 이후 아래 버튼들로 수정 \n"
            "# 이름 설정: 이름 설정(변경) 버튼 -> 이름 입력 \n"
            "# 위치 설정: 친구 선택 -> 위치 입력 버튼 → 지도에서 클릭으로 위치 지정 \n"
            "\n"
            "# 분석 기간 선택: 오늘, 1일, 1주일, 1개월, 1년 중 선택하여 분석 가능 \n"
            "# 채팅 업로드: 친구 선택 후 Upload KakaoTalk Chat 클릭 → 카카오톡 '대화 내보내기' 파일 업로드 \n"
            "# 친구 삭제: 친구 선택 -> 친구 삭제 버튼 클릭 "
        )

        help_box = QMessageBox(self)
        help_box.setWindowTitle("도움말")
        help_box.setText(help_text)
        help_box.setStandardButtons(QMessageBox.Ok)
        help_box.exec_()






    def save_friends(self):
        file_path = os.path.join("users", f"{self.user_info['id']}.json")

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

    def sort_friends(self, mode):
        if mode == "이름순":
            self.friends.sort(key=lambda f: (f.name == "-", f.name))  #이름 비어있으면(-) -> 가장 뒤로 보내기기
        elif mode == "등록순": 
            self.friends.sort(key=lambda f: f.registered_at)
        elif mode == "친밀도순":
            self.friends.sort(key=lambda f: -f.intimacy)
        self.update_list()

    def all_calculate_intimacy(self):         #전체 친구의 친밀도 계산
        today = datetime.date.today()
        period = self.selected_period

        cutoff_days = {
            "오늘": 0,
            "1일": 1,
            "1주일": 7,
            "1개월": 30,
            "1년": 365
        }.get(period, 0)  # 며칠 더할 지

        for friend in self.friends:
            if not hasattr(friend, "chat_history") or not friend.chat_history:      #기록 없으면 그냥 0으로
                friend.intimacy = 0
                continue

            # 현재부터 cutoff_days 까지 대화 수 더하기
            friend.intimacy = sum(
                num for date_str, num in friend.chat_history.items()
                if (today - datetime.date.fromisoformat(date_str)).days <= cutoff_days
            )

        self.update_list()


    def calculate_intimacy(self, friend):   #특정 친구와의 친밀도만 계산
        today = datetime.date.today()
        period = self.selected_period

        cutoff_days = {
            "오늘": 0,
            "1일": 1,
            "1주일": 7,
            "1개월": 30,
            "1년": 365
        }.get(period, 0)

        if not hasattr(friend, "chat_history") or not friend.chat_history:
            friend.intimacy = 0
            return

        friend.intimacy = sum(
            num for date_str, num in friend.chat_history.items()
            if (today - datetime.date.fromisoformat(date_str)).days <= cutoff_days
        )

    def interaction_sort(self):
        self.save_friends()
        self.sort_friends(self.sort_box.currentText())
        