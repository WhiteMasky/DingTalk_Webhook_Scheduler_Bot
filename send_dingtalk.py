# send_dingtalk.py
import os
import requests
import time
import hmac
import hashlib
import base64
import urllib.parse
from datetime import datetime, timezone, timedelta

# 固定名单（顺序不可变）- 格式：显示名称:userId
MEMBERS = [
    {"name": "@钿钿", "userId": "USER_ID_1"},
    {"name": "@久七", "userId": "USER_ID_2"},
    {"name": "@德洛", "userId": "USER_ID_3"},
    {"name": "@青之", "userId": "USER_ID_4"},
    {"name": "@可文", "userId": "USER_ID_5"},
    {"name": "@昕允", "userId": "USER_ID_6"},
    {"name": "@周砥", "userId": "USER_ID_7"},
    {"name": "@舟舟", "userId": "USER_ID_8"},
    {"name": "@焱枫", "userId": "USER_ID_9"},
    {"name": "@子珩", "userId": "USER_ID_10"},
    {"name": "@九岚", "userId": "USER_ID_11"},
    {"name": "@启涵", "userId": "USER_ID_12"},
    {"name": "@熙城", "userId": "USER_ID_13"}
]

# 固定任务顺序
TASKS = ["整理昨晚小考真题", "发问题清单", "记笔记", "检查模拟题"]

def get_today_assignments():
    """根据当前日期计算今日轮值的4人及对应任务"""
    tz_beijing = timezone(timedelta(hours=8))
    now = datetime.now(tz_beijing)
    base_date = datetime(2025, 1, 1, tzinfo=tz_beijing)
    days_since_base = (now - base_date).days
    offset = (days_since_base * 4 + 12) % len(MEMBERS)

    assignments = []
    at_user_ids = []
    
    for i in range(4):
        member_index = (offset + i) % len(MEMBERS)
        member = MEMBERS[member_index]
        task = TASKS[i]
        assignments.append(f"{member['name']}：{task}")
        at_user_ids.append(member['userId'])
    
    return assignments, at_user_ids

def send_message():
    webhook_url = os.getenv("DINGTALK_WEBHOOK_URL")
    secret = os.getenv("DINGTALK_SECRET")

    if not webhook_url or not secret:
        raise ValueError("环境变量 DINGTALK_WEBHOOK_URL 或 DINGTALK_SECRET 未设置")

    assignments, at_user_ids = get_today_assignments()
    assignment_text = "\n".join(assignments)
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')

    message = {
        "msgtype": "text",
        "text": {
            "content": f"【GitHub Action 通知】{current_time}\n今日排班：\n{assignment_text}"
        },
        "at": {
            "atUserIds": at_user_ids,
            "isAtAll": False
        }
    }

    # 计算签名（DingTalk 安全机制）
    timestamp = str(round(time.time() * 1000))
    string_to_sign = f'{timestamp}\n{secret}'
    hmac_code = hmac.new(
        secret.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))

    full_url = f"{webhook_url}&timestamp={timestamp}&sign={sign}"
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    response = requests.post(full_url, json=message, headers=headers)

    print(response.status_code, response.text)
    return response.ok

if __name__ == "__main__":
    send_message()
