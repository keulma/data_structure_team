# ui/main_page.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QComboBox, QFileDialog, QLabel
from data.friend import Friend
from map_viewer import MapViewer

class MainPage(QWidget):
    def __init__(self, user_info):
        super().__init__()
        self.user_info = user_info
        self.friends = []
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()

        # ✅ 왼쪽 지도 영역
        self.map_viewer = MapViewer(self.friends)
        layout.addWidget(self.map_viewer, 2)  # 지도는 2 비율

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

        delete_btn = QPushButton("Delete Friend")
        delete_btn.clicked.connect(self.delete_selected_friend)
        right_panel.addWidget(delete_btn)

        upload_btn = QPushButton("Upload KakaoTalk Chat")
        upload_btn.clicked.connect(self.upload_chat)
        right_panel.addWidget(upload_btn)

        layout.addLayout(right_panel, 1)
        self.setLayout(layout)

    def add_friend_dialog(self):
        # 예시: 바로 친구 추가
        new_friend = Friend("Alice", "USA", "New York")
        self.friends.append(new_friend)
        self.update_list()

    def delete_selected_friend(self):
        current = self.friend_list_widget.currentRow()
        if current >= 0:
            del self.friends[current]
            self.update_list()

    def upload_chat(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open KakaoTalk Text", "", "Text Files (*.txt)")
        if path:
            with open(path, 'r', encoding='utf-8') as file:
                chat = file.read()
                for friend in self.friends:
                    friend.intimacy += chat.count(friend.name)
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
