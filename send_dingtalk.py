# send_dingtalk.py
import os
import requests
import time
import hmac
import hashlib
import base64
import urllib.parse

def send_message():
    webhook_url = os.getenv("DINGTALK_WEBHOOK_URL")
    secret = os.getenv("DINGTALK_SECRET")

    if not webhook_url or not secret:
        raise ValueError("环境变量 DINGTALK_WEBHOOK_URL 或 DINGTALK_SECRET 未设置")

    # 构造消息
    message = {
        "msgtype": "text",
        "text": {
            "content": f"【GitHub Action 通知】{time.strftime('%Y-%m-%d %H:%M:%S')} - 任务已执行！"
        }
    }

    # 计算签名
    timestamp = str(round(time.time() * 1000))
    string_to_sign = f'{timestamp}\n{secret}'
    hmac_code = hmac.new(secret.encode('utf-8'), string_to_sign.encode('utf-8'), digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))

    # 发送请求
    full_url = f"{webhook_url}&timestamp={timestamp}&sign={sign}"
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    response = requests.post(full_url, json=message, headers=headers)

    print(response.status_code, response.text)
    return response.ok

if __name__ == "__main__":
    send_message()
