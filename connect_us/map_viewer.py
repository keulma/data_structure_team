# map_viewer.py
import folium
import os
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from geopy.geocoders import Nominatim
from PyQt5.QtCore import QUrl

class MapViewer(QWidget):
    def __init__(self, friends):
        super().__init__()
        self.friends = friends
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        self.setLayout(layout)

        self.update_map()

    def update_map(self):
        os.makedirs("assets", exist_ok=True)

        geolocator = Nominatim(user_agent="friend_map_app")
        
        m = folium.Map(location=[30, 100], zoom_start=3)
        coords = {}
        # 마커 찍기
        for f in self.friends:
            try:
                location = geolocator.geocode(f.city + ", " + f.country)
                if location:
                    latlon = [location.latitude, location.longitude]
                    coords[f.name] = latlon
                    folium.Marker(latlon, tooltip=f"{f.name} ❤️{f.intimacy}").add_to(m)
            except:
                continue

        # 친밀도 선 그리기 (예시: 자기 자신 기준 가장 친한 친구와 연결)
        # 향후 선 로직을 원하는 방식으로 변경 가능
        if coords:
            self_loc = list(coords.values())[0]  # 첫 번째 친구 위치
            for name, latlon in list(coords.items())[1:]:
                folium.PolyLine([self_loc, latlon], color="red", weight=2).add_to(m)

        # 지도 저장 및 로드
        map_path = os.path.abspath("assets/world_map.html")
        m.save(map_path)

        if os.path.exists(map_path):
            print(f"[DEBUG] Map saved at: {map_path}")
            self.web_view.load(QUrl.fromLocalFile(map_path))
        else:
            print("[ERROR] Map file not found!")