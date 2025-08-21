from datetime import date


today = date.today()
formatted = f"{today.year} 年 {today.month} 月 {today.day} 日"

with open("data/last-update.txt", "w", encoding="utf-8") as f:
    f.write(formatted)
