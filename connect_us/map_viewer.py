import folium
import math
import os
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import QUrl, QTimer
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="friend_map_app")

def generate_smooth_curve(p1, p2, curve_strength=0.5, num_points=60):
    mid_lat = (p1[0] + p2[0]) / 2
    mid_lng = (p1[1] + p2[1]) / 2

    # 곡선 중심을 항상 북쪽으로 올리기
    curve_lat = mid_lat + abs(p2[0] - p1[0]) * curve_strength
    curve_lng = mid_lng  # 좌우 이동 없음

    def bezier(t):
        lat = (1 - t) ** 2 * p1[0] + 2 * (1 - t) * t * curve_lat + t ** 2 * p2[0]
        lng = (1 - t) ** 2 * p1[1] + 2 * (1 - t) * t * curve_lng + t ** 2 * p2[1]
        return [lat, lng]

    return [bezier(t / num_points) for t in range(num_points + 1)]

class MapViewer(QWidget):
    def __init__(self, friends, user_info):
        super().__init__()
        self.friends = friends
        self.user_info = user_info
        self.clicked_coords = None
        self.on_click_callback = None
        self.click_checked = False
        self.selected_period = "하루" 

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
            max_zoom=18,
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
                    {map_var}.setMaxZoom(18);
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
                    tooltip=f"{self.user_info['id']} (You)",
                    icon=folium.Icon(color="blue", icon="user")
                ).add_to(m)
        except Exception as e:
            print(f"[user location error] {e}")

        if 'user_latlon' in locals():
            for friend in self.friends:
                if friend.x != 0 and friend.y != 0:
                    friend_latlon = [friend.x, friend.y]
                    talk_weight = self.get_weight_from_intimacy(friend.intimacy)
                    
                    color = "#e41b1b"

                    points = generate_smooth_curve(user_latlon, friend_latlon)
                    folium.PolyLine(
                        locations=points,
                        color=color,
                        weight=talk_weight,
                        opacity=0.7
                    ).add_to(m)
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
            print(f"latitude: {lat}, longitude: {lng}")
            self.clicked_coords = (lat, lng)

            self.web_view.page().runJavaScript("""
                window.clickedLat = undefined;
                window.clickedLng = undefined;
            """)

            if self.on_click_callback:
                self.on_click_callback(lat, lng)

        QTimer.singleShot(1000, self.check_for_click)

    def get_weight_from_intimacy(self, intimacy):
        period_ratio = {
            "오늘": 365,
            "1일": 182,
            "1주일": 52,
            "1개월": 12,
            "6개월": 2,
            "1년": 1
        }

        ratio = period_ratio.get(self.selected_period, 1)
        adjusted_score = min(intimacy * ratio, 10000)
        if adjusted_score == 0:
            level_weight = 0
            return level_weight
        else :
            level_weight = int(adjusted_score // 1000) + 1  # 0~999 → 1, ..., 9000~9999 → 10
            return level_weight