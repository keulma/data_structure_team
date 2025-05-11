# data/friend.py
from datetime import datetime

class Friend:
    def __init__(self, name, country, city, intimacy=0):
        self.name = name
        self.country = country
        self.city = city
        self.intimacy = intimacy
        self.registered_at = datetime.now()
