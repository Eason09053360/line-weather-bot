import requests
import os # 新增這個，用來讀取環境變數
import sys

# ================= 設定區 =================

# 改成從環境變數讀取 (等一下會在 GitHub 網站上設定)
LINE_ACCESS_TOKEN = os.environ.get("LINE_ACCESS_TOKEN")
YOUR_USER_ID = os.environ.get("YOUR_USER_ID")

# 檢查是否有讀取到 Token
if not LINE_ACCESS_TOKEN or not YOUR_USER_ID:
    print("❌ 錯誤：找不到 Token 或 User ID，請檢查 GitHub Secrets 設定。")
    sys.exit(1)

# 設定所在地：桃園市中壢區
LATITUDE = 24.9587
LONGITUDE = 121.2238

# ================= 核心功能區 (跟原本一樣) =================

def get_weather():
    # ... (這部分程式碼完全不用改，照抄原本的即可) ...
    # 為了節省篇幅，這裡省略，請保留您原本寫好的 get_weather 函式
    url = f"https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=Asia%2FTaipei&forecast_days=1"
    try:
        res = requests.get(url)
        data = res.json()
        daily = data['daily']
        date = daily['time'][0]
        min_temp = daily['temperature_2m_min'][0]
        max_temp = daily['temperature_2m_max'][0]
        rain_prob = daily['precipitation_probability_max'][0]
        
        msg_content = (
            f"🌞 早安！中壢今日天氣報報\n"
            f"📅 日期: {date}\n"
            f"🌡️ 氣溫: {min_temp}°C ~ {max_temp}°C\n"
            f"☔ 降雨機率: {rain_prob}%"
        )
        if rain_prob > 30: msg_content += "\n⚠️ 記得帶傘喔！"
        elif max_temp > 30: msg_content += "\n🥤 天氣很熱，多喝水！"
        return msg_content
    except Exception as e:
        print(f"天氣抓取失敗: {e}")
        return "⚠️ 天氣資料讀取失敗"

def send_line_push(message_text):
    # ... (這部分也跟原本一樣) ...
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
    }
    payload = {
        "to": YOUR_USER_ID,
        "messages": [{"type": "text", "text": message_text}]
    }
    res = requests.post(url, headers=headers, json=payload)
    if res.status_code == 200:
        print("✅ 訊息發送成功！")
    else:
        print(f"❌ 發送失敗: {res.status_code}, {res.text}")

# ================= 執行區 =================

if __name__ == "__main__":
    # 只要執行這行就好，不需要 schedule 迴圈
    print("🚀 GitHub Actions 開始執行...")
    weather_msg = get_weather()
    send_line_push(weather_msg)