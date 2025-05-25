import folium
import os
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import QUrl, QTimer
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="friend_map_app")

class MapViewer(QWidget):
    def __init__(self, friends, user_info):
        super().__init__()
        self.friends = friends
        self.user_info = user_info
        self.clicked_coords = None
        self.on_click_callback = None
        self.click_checked = False
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        self.setLayout(layout)
        self.update_map()

    def set_click_callback(self, callback_func):
        self.on_click_callback = callback_func

    def update_map(self):
        os.makedirs("assets", exist_ok=True)

        m = folium.Map(
            location=[36.5, 127.5],
            zoom_start=5,
            min_zoom=2,
            max_zoom=6,
            tiles="CartoDB positron",
            control_scale=True,
            no_wrap=True,
            max_bounds=True
        )

        map_var = m.get_name()
        m.get_root().script.add_child(folium.Element(f"""
            setTimeout(function() {{
                if (typeof {map_var} !== 'undefined') {{
                    {map_var}.setMaxBounds([[-70, -25], [90, 335]]);
                    {map_var}.options.maxBoundsViscosity = 0;
                    {map_var}.setMinZoom(2);
                    {map_var}.setMaxZoom(8);
                }}
            }}, 500);
        """))

        coords = []
        for friend in self.friends:
            if friend.x != 0 and friend.y != 0:
                latlon = [friend.x, friend.y]
                coords.append(latlon)
                folium.Marker(
                    latlon,
                    tooltip=f"{friend.name} ❤️{friend.intimacy}"
                ).add_to(m)

        try:
            location = geolocator.geocode(f"{self.user_info['city']}, {self.user_info['country']}")
            if location:
                user_latlon = [location.latitude, location.longitude]
                coords.append(user_latlon)
                folium.Marker(
                    user_latlon,
                    tooltip=f"🧍 {self.user_info['id']} (You)",
                    icon=folium.Icon(color="blue", icon="user")
                ).add_to(m)
        except Exception as e:
            print(f"[❌ 사용자 위치 오류] {e}")
            
        # 클릭 이벤트 등록
        m.get_root().script.add_child(folium.Element(f"""
            function onMapClick(e) {{
                window.clickedLat = e.latlng.lat;
                window.clickedLng = e.latlng.lng;
            }}
            setTimeout(function() {{
                if (typeof {map_var} !== 'undefined') {{
                    {map_var}.on('click', onMapClick);
                }}
            }}, 500);
        """))

        map_path = os.path.abspath("assets/world_map.html")
        m.save(map_path)
        self.web_view.load(QUrl.fromLocalFile(map_path))
        QTimer.singleShot(1000, self.check_for_click)

    def check_for_click(self):
        if self.click_checked:
            return

        self.web_view.page().runJavaScript("""
            if (typeof window.clickedLat !== 'undefined' && typeof window.clickedLng !== 'undefined') {
                [window.clickedLat, window.clickedLng]
            } else {
                null
            }
        """, self.handle_click_result)

    def handle_click_result(self, result):
        if result:
            lat, lng = result
            print(f"[클릭됨] 위도: {lat}, 경도: {lng}")
            self.clicked_coords = (lat, lng)

            self.web_view.page().runJavaScript("""
                window.clickedLat = undefined;
                window.clickedLng = undefined;
            """)

            if self.on_click_callback:
                self.on_click_callback(lat, lng)

        QTimer.singleShot(1000, self.check_for_click)
