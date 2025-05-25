#text_analyze.py

import re, datetime, json, os
from collections import defaultdict


all_conversations = defaultdict(int)  # 날짜별 총 메시지 수
period_stats = {
    "오늘": 0,
    "1일": 0,
    "1주일": 0,
    "1개월": 0,
    "6개월": 0,
    "1년": 0
}







def parse_kakao_txt(file_path):
    global all_conversations, period_stats
    all_conversations.clear()
    period_stats = {key: 0 for key in period_stats}

    today = datetime.date.today()
    current_date = None

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        # 날짜 추출
        date_match = re.match(r"-{5,} (\d{4})년 (\d{1,2})월 (\d{1,2})일", line)
        if date_match:
            y, m, d = map(int, date_match.groups())
            current_date = datetime.date(y, m, d)
            continue

        # 메시지 카운트 ( 보낸 사람 구분 X )
        if line.startswith("[") and "] [" in line and current_date:
            all_conversations[current_date.isoformat()] += 1

            delta = (today - current_date).days
            if delta == 0:
                period_stats["오늘"] += 1
            if delta <= 1:
                period_stats["1일"] += 1
            if delta <= 7:
                period_stats["1주일"] += 1
            if delta <= 30:
                period_stats["1개월"] += 1
            if delta <= 180:
                period_stats["6개월"] += 1
            if delta <= 365:
                period_stats["1년"] += 1


                

def save_analysis(friend_name):
    output_dir = "analysis_results"
    os.makedirs(output_dir, exist_ok=True)

    data = {
        "conversations_by_date": dict(all_conversations),
        "conversations_by_period": period_stats
    }

    output_path = os.path.join(output_dir, f"{friend_name}_chat_summary.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
