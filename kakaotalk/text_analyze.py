import re
import datetime
import json
from collections import defaultdict

my_name = "김동준"
all_conversations = defaultdict(int)
partner_name = None

def parse_kakao_txt(file_path):
    global all_conversations, partner_name
    all_conversations.clear()
    partner_name = None

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_date = None

    for line in lines:
        date_match = re.match(r"-{5,} (\d{4})년 (\d{1,2})월 (\d{1,2})일", line)
        if date_match:
            y, m, d = date_match.groups()
            current_date = datetime.date(int(y), int(m), int(d)).isoformat()
            continue

        if line.startswith("[") and "] [" in line:
            msg_match = re.match(r"\[(.+?)\] \[.+?\]", line)
            if msg_match and current_date:
                sender = msg_match.group(1)
                if sender != my_name and partner_name is None:
                    partner_name = sender
                all_conversations[current_date] += 1

def save_analysis():
    data = {
        "partner": partner_name,
        "conversations": dict(all_conversations)
    }
    with open("chat_summary.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
