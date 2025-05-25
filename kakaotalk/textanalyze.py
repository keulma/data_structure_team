import tkinter as tk
from tkinter import filedialog, messagebox
import re
from collections import defaultdict
import datetime

my_name = "김동준"
all_conversations = defaultdict(int)  # 날짜별 전체 메시지 수
partner_name = None                   # 상대방 이름 저장
start_date = None
selected_period = None

def parse_kakao_txt(file_path):
    global all_conversations, partner_name
    all_conversations.clear()
    partner_name = None

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_date = None

    for line in lines:
        # 날짜 줄 처리
        date_match = re.match(r"-{5,} (\d{4})년 (\d{1,2})월 (\d{1,2})일", line)
        if date_match:
            y, m, d = date_match.groups()
            current_date = datetime.date(int(y), int(m), int(d)).isoformat()
            continue

        # 메시지 시작 줄만 파싱
        if line.startswith("[") and "] [" in line:
            msg_match = re.match(r"\[(.+?)\] \[.+?\]", line)
            if msg_match and current_date:
                sender = msg_match.group(1)
                if sender != my_name and partner_name is None:
                    partner_name = sender  # 상대방 이름 저장 (최초 1회만)

                all_conversations[current_date] += 1  # 나든 상대든 전부 포함




def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if not file_path:
        return
    try:
        parse_kakao_txt(file_path)
        messagebox.showinfo("완료", "파일 분석이 완료되었습니다. 기간을 선택한 뒤 출력하세요.")
    except Exception as e:
        messagebox.showerror("오류", str(e))




def set_period(period):
    global start_date, selected_period
    today = datetime.date.today()

    if period == "오늘":
        start_date = today
    elif period == "1일":
        start_date = today - datetime.timedelta(days=1)
    elif period == "1주일":
        start_date = today - datetime.timedelta(weeks=1)
    elif period == "1개월":
        start_date = today - datetime.timedelta(days=30)
    elif period == "6개월":
        start_date = today - datetime.timedelta(days=180)
    elif period == "1년":
        start_date = today - datetime.timedelta(days=365)

    selected_period = period
    messagebox.showinfo("선택 완료", f"{period} 전부터의 대화량이 출력됩니다.")

def show_filtered_result():
    if start_date is None:
        messagebox.showwarning("기간 없음", "먼저 기간을 선택하세요.")
        return

    output_text.delete("1.0", tk.END)
    if selected_period == "오늘":
        output_text.insert(tk.END, f"오늘 총 대화 횟수\n\n")
    else:
        output_text.insert(tk.END, f"지난 {selected_period} 동안 총 대화 횟수\n\n")

    today = datetime.date.today()
    total_count = 0

    for date_str, count in all_conversations.items():
        date_obj = datetime.date.fromisoformat(date_str)

        if selected_period == "오늘":
            if date_obj == today:
                total_count += count
        elif selected_period == "1일":
            if date_obj == today or date_obj == (today - datetime.timedelta(days=1)):
                total_count += count
        else:
            if date_obj >= start_date:
                total_count += count

    if partner_name and total_count > 0:
        output_text.insert(tk.END, f"{partner_name} 과의 대화 횟수 : {total_count}회\n")
    else:
        output_text.insert(tk.END, "대화 기록이 없습니다.\n")

# GUI 구성
root = tk.Tk()
root.title("카카오톡 개인톡 대화 분석기")

frame = tk.Frame(root)
frame.pack(padx=20, pady=10)

btn_load = tk.Button(frame, text="카카오톡 TXT 파일 열기", command=open_file)
btn_load.grid(row=0, column=0, padx=5)

btn_today = tk.Button(frame, text="오늘", command=lambda: set_period("오늘"))
btn_day = tk.Button(frame, text="1일", command=lambda: set_period("1일"))
btn_week = tk.Button(frame, text="1주일", command=lambda: set_period("1주일"))
btn_month = tk.Button(frame, text="1개월", command=lambda: set_period("1개월"))
btn_6month = tk.Button(frame, text="6개월", command=lambda: set_period("6개월"))
btn_year = tk.Button(frame, text="1년", command=lambda: set_period("1년"))

btn_today.grid(row=0, column=1, padx=2)
btn_day.grid(row=0, column=2, padx=2)
btn_week.grid(row=0, column=3, padx=2)
btn_month.grid(row=0, column=4, padx=2)
btn_6month.grid(row=0, column=5, padx=2)
btn_year.grid(row=0, column=6, padx=2)

btn_show = tk.Button(root, text="출력", command=show_filtered_result)
btn_show.pack(pady=5)

output_text = tk.Text(root, width=60, height=30)
output_text.pack()

root.mainloop()
