import requests
import os
import sys

# ================= 設定區 =================

# 從 GitHub Secrets 讀取 (不用改)
LINE_ACCESS_TOKEN = os.environ.get("LINE_ACCESS_TOKEN")
YOUR_USER_ID = os.environ.get("YOUR_USER_ID")

# 檢查 Token
if not LINE_ACCESS_TOKEN or not YOUR_USER_ID:
    print("❌ 錯誤：找不到 Token 或 User ID，請檢查 GitHub Secrets 設定。")
    sys.exit(1)

# 設定所在地：桃園市中壢區
LATITUDE = 24.9587
LONGITUDE = 121.2238

# ================= 核心功能區 =================

def get_report():
    """獲取天氣 + 空氣品質 + 紫外線，並產生建議"""
    
    # 1. 獲取天氣與紫外線 (UV)
    # 我們多加了 uv_index_max (每日最大紫外線指數)
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_max,uv_index_max&timezone=Asia%2FTaipei&forecast_days=1"
    
    # 2. 獲取空氣品質 (AQI) - 這是 Open-Meteo 另一個專用的 API
    # 我們抓取 current (當前) 的 US AQI 指數
    air_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={LATITUDE}&longitude={LONGITUDE}&current=us_aqi"

    try:
        # --- 抓天氣資料 ---
        res_weather = requests.get(weather_url)
        data_w = res_weather.json()
        daily = data_w['daily']
        
        date = daily['time'][0]
        min_temp = daily['temperature_2m_min'][0]
        max_temp = daily['temperature_2m_max'][0]
        rain_prob = daily['precipitation_probability_max'][0]
        uv_index = daily['uv_index_max'][0]

        # --- 抓空氣資料 ---
        res_air = requests.get(air_url)
        data_a = res_air.json()
        current_aqi = data_a['current']['us_aqi']

        # --- 產生「攜帶建議」邏輯 ---
        advice_list = []
        
        # 雨具建議
        if rain_prob >= 50:
            advice_list.append("🌧️ 下雨機率高，務必攜帶雨傘！")
        elif rain_prob >= 30:
            advice_list.append("🌂 有點變天，建議帶把摺疊傘備用。")
        else:
            advice_list.append("☀️ 降雨機率低，不用帶傘。")

        # 防曬建議 (UV指數邏輯)
        if uv_index >= 8:
            advice_list.append("🥵 紫外線超強！請帶陽傘或擦防曬。")
        elif uv_index >= 6:
            advice_list.append("😎 紫外線偏高，戶外活動注意防曬。")
            
        # 空氣建議
        aqi_status = "🟢 良好"
        if current_aqi > 150:
            aqi_status = "🔴 不健康"
            advice_list.append("😷 空氣很差，出門建議戴口罩！")
        elif current_aqi > 100:
            aqi_status = "🟠 對敏感族群不健康"
            advice_list.append("😷 過敏體質建議戴口罩。")
        elif current_aqi > 50:
            aqi_status = "🟡 普通"

        # --- 組合最終訊息 ---
        advice_msg = "\n".join(advice_list)
        
        msg_content = (
            f"早安！中壢今日氣象報告 📡\n"
            f"📅 日期: {date}\n"
            f"🌡️ 氣溫: {min_temp}°C ~ {max_temp}°C\n"
            f"☔ 降雨機率: {rain_prob}%\n"
            f"☀️ 紫外線指數: {uv_index}\n"
            f"🍃 空氣品質(AQI): {current_aqi} ({aqi_status})\n"
            f"----------------------\n"
            f"💡 小幫手建議：\n"
            f"{advice_msg}"
        )
            
        return msg_content
        
    except Exception as e:
        print(f"資料抓取失敗: {e}")
        return "⚠️ 抱歉，氣象資料讀取失敗，請檢查 API 連線。"

def send_line_push(message_text):
    """發送 LINE 訊息 (跟原本一樣)"""
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
    print("🚀 開始執行氣象抓取任務...")
    report = get_report()
    send_line_push(report)
