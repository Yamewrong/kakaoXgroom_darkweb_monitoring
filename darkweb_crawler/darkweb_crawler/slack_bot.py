import requests
import json

# 🔹 Slack Webhook URL (설정한 Webhook URL 입력)
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

def send_slack_message(message):
    """Slack 채널로 메시지를 전송하는 함수"""
    payload = {
        "text": message  # Slack 메시지 내용
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(SLACK_WEBHOOK_URL, data=json.dumps(payload), headers=headers)
        response.raise_for_status()  # HTTP 에러 발생 시 예외 처리
        print("✅ Slack 메시지 전송 성공!")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Slack 메시지 전송 실패: {e}")
        return None

# ✅ Slack 메시지 테스트 실행
if __name__ == "__main__":
    send_slack_message("🚨 테스트 메시지 - Slack API 정상 동작 확인")
