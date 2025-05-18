# data/friend.py

from datetime import datetime
import time

class Friend:
    def __init__(self, name, country, city, x=0, y=0, intimacy=0):
        self.name = name
        self.country = country
        self.city = city
        self.x = x
        self.y = y
        self.intimacy = intimacy
        self.registered_at = datetime.now()

    def to_dict(self):
        return {
            "name": self.name,
            "country": self.country,
            "city": self.city,
            "x": self.x,
            "y": self.y,
            "intimacy": self.intimacy
        }

    @staticmethod
    def from_dict(data):
        return Friend(
            name=data["name"],
            country=data["country"],
            city=data["city"],
            x=data.get("x", 0),
            y=data.get("y", 0),
            intimacy=data.get("intimacy", 0)
        )