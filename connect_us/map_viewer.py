import folium
import os
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import QUrl, QTimer
from geopy.geocoders import Nominatim

class MapViewer(QWidget):
    def __init__(self, friends):
        super().__init__()
        self.friends = friends
        self.clicked_coords = None
        self.on_click_callback = None
        self.click_checked = False  # ✅ 클릭 여부 플래그
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
        geolocator = Nominatim(user_agent="friend_map_app")
        m = folium.Map(location=[30, 100], zoom_start=3)

        coords = {}
        for f in self.friends:
            try:
                location = geolocator.geocode(f.city + ", " + f.country)
                if location:
                    latlon = [location.latitude, location.longitude]
                    coords[f.name] = latlon
                    folium.Marker(latlon, tooltip=f"{f.name} ❤️{f.intimacy}").add_to(m)
            except:
                continue

        if coords:
            self_loc = list(coords.values())[0]
            for name, latlon in list(coords.items())[1:]:
                folium.PolyLine([self_loc, latlon], color="red", weight=2).add_to(m)

        map_var = m.get_name()
        click_js = f"""
            function onMapClick(e) {{
                window.clickedLat = e.latlng.lat;
                window.clickedLng = e.latlng.lng;
            }}
            setTimeout(function() {{
                if (typeof {map_var} !== 'undefined') {{
                    {map_var}.on('click', onMapClick);
                }}
            }}, 500);
        """
        m.get_root().script.add_child(folium.Element(click_js))

        map_path = os.path.abspath("assets/world_map.html")
        m.save(map_path)
        self.web_view.load(QUrl.fromLocalFile(map_path))

        QTimer.singleShot(1000, self.check_for_click)

    def check_for_click(self):
        if self.click_checked:
            return  # ✅ 이미 클릭했으면 종료

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
            print(f"[클릭됨] 위도: {lat}, 경도: {lng}")  # 콘솔 테스트 로그
            self.clicked_coords = (lat, lng)

            #클릭 정보 초기화
            self.web_view.page().runJavaScript("""      
                window.clickedLat = undefined;
                window.clickedLng = undefined;
            """)

            if self.on_click_callback:
                self.on_click_callback(lat, lng)

        QTimer.singleShot(1000, self.check_for_click)