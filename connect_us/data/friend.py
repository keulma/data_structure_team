# data/friend.py

from datetime import datetime
import time

class Friend:
    def __init__(self, name, country, city, x=0, y=0, intimacy=0, registered_at=None, chat_history=None):
        self.name = name
        self.country = country
        self.city = city
        self.x = x
        self.y = y
        self.intimacy = intimacy
        self.registered_at = registered_at or datetime.now()  # 새로 생성 or 불러온 시간
        self.chat_history = chat_history or {}  # ✅ 날짜별 대화 수 저장

    def to_dict(self):
        return {
            "name": self.name,
            "country": self.country,
            "city": self.city,
            "x": self.x,
            "y": self.y,
            "intimacy": self.intimacy,
            "registered_at": self.registered_at.isoformat(),  # 문자열로 저장
            "chat_history": self.chat_history   # ✅ 포함
        }

    @staticmethod
    def from_dict(data):
        registered_at_str = data.get("registered_at")
        registered_at = datetime.fromisoformat(registered_at_str) if registered_at_str else datetime.now()

        return Friend(
            name=data["name"],
            country=data["country"],
            city=data["city"],
            x=data.get("x", 0),
            y=data.get("y", 0),
            intimacy=data.get("intimacy", 0),
            registered_at=registered_at,
            chat_history=data.get("chat_history", {}) 
        )