import os
import time
import json
import sqlite3
import threading
import datetime
import requests
from flask import Flask, render_template, request, jsonify
from collections import Counter
from tldextract import extract
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

app = Flask(__name__)
DB_FILE = "victim.db"
KNOWN_DOMAINS_FILE = "known_domains.json"  # 🚨 감지된 도메인 저장 JSON

# 🔔 Slack 설정
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL_ID = "C08EJCTPT9V"  # 'test_alert' 채널 ID
SLACK_WEBHOOK_URL = ""
slack_client = WebClient(token=SLACK_BOT_TOKEN)

# 🕵️ NEW 아이콘 유지 기간 (최근 X시간 이내 등록된 데이터에만 표시)
NEW_BADGE_HOURS = 24  # 24시간 이내 데이터는 NEW 배지 표시

def get_db_connection():
    """SQLite 데이터베이스 연결"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def load_known_domains():
    """JSON 파일에서 감지된 도메인 목록 불러오기"""
    if os.path.exists(KNOWN_DOMAINS_FILE):
        with open(KNOWN_DOMAINS_FILE, "r", encoding="utf-8") as f:
            try:
                return set(json.load(f))
            except json.JSONDecodeError:
                return set()
    return set()

def save_known_domains(domains):
    """새로운 감지된 도메인을 JSON 파일에 저장"""
    with open(KNOWN_DOMAINS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(domains), f, indent=4)

def get_domain_tld(domain):
    """도메인에서 TLD 추출"""
    extracted = extract(domain)
    return extracted.suffix if extracted.suffix else "Unknown"

@app.route('/')
def index():
    """메인 페이지"""
    return render_template("index.html")

@app.route('/visualization')
def visualization():
    """시각화 페이지"""
    return render_template("visualization.html")

@app.route('/api/domains', methods=['GET'])
def get_domains():
    """도메인 목록 가져오기 (페이징 지원 & NEW 표시)"""
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 20))
    offset = (page - 1) * limit
    search_query = request.args.get("search", "").strip()
    date_filter = request.args.get("date", "").strip()

    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT domain, upload_time, timestamp FROM leaks WHERE 1=1"
    params = []

    if search_query:
        query += " AND domain = ?"
        params.append(search_query)

    if date_filter:
        query += " AND DATE(upload_time) >= ?"
        params.append(date_filter)

    count_query = "SELECT COUNT(*) FROM (" + query + ")"
    cursor.execute(count_query, params)
    total_rows = cursor.fetchone()[0]
    total_pages = (total_rows // limit) + (1 if total_rows % limit > 0 else 0)

    query += " ORDER BY upload_time DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()

    # 🆕 NEW 아이콘을 위한 필드 추가 (최근 X시간 내 추가된 도메인)
    now = datetime.datetime.now()
    data = []
    for row in results:
        timestamp = datetime.datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
        is_new = (now - timestamp).total_seconds() / 3600 < NEW_BADGE_HOURS  # NEW 기간 내면 True
        row_dict = dict(row)
        row_dict["is_new"] = is_new
        data.append(row_dict)

    return jsonify({"domains": data, "total_pages": total_pages})

@app.route('/api/tld_stats', methods=['GET'])
def get_tld_stats():
    """TLD별 도메인 통계"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT domain FROM leaks")
    results = cursor.fetchall()
    conn.close()
    
    tld_list = [get_domain_tld(row["domain"]) for row in results]
    tld_counts = dict(Counter(tld_list))
    
    return jsonify(tld_counts)

# ✅ 1️⃣ DB 업데이트 감지 기능 개선
def watch_db_updates():
    """DB 변경을 감지하고 업데이트 발생 시 새로운 도메인만 Slack 알림 전송"""
    known_domains = load_known_domains()  # 기존 감지된 도메인 로드

    while True:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # DB에서 최근 50개 도메인 가져오기
            cursor.execute("SELECT domain FROM leaks ORDER BY timestamp DESC LIMIT 50")
            latest_domains = {row["domain"] for row in cursor.fetchall()}
            conn.close()

            # 기존 감지된 도메인과 비교해서 새로운 도메인 찾기
            new_domains = latest_domains - known_domains  # 차집합 연산으로 새로운 도메인 찾기

            if new_domains:  # 새로운 도메인이 있으면 Slack 알림 전송
                print(f"🔄 새로운 도메인 감지됨: {new_domains}")
                send_slack_alert(list(new_domains))  # Slack 알림 보내기
                known_domains.update(new_domains)  # 기존 도메인 목록 업데이트
                save_known_domains(known_domains)  # JSON 파일에 저장

        except Exception as e:
            print(f"❌ DB 감시 오류: {e}")

        time.sleep(60)  # 1분마다 확인

# ✅ 2️⃣ 새로운 도메인 Slack 알림 전송 개선
def send_slack_alert(new_domains):
    """새로운 도메인이 추가되었을 때 Slack으로 경고 메시지 전송"""
    if not new_domains:
        print("⚠️ 새로 추가된 도메인이 없습니다. Slack 알림을 전송하지 않습니다.")
        return

    # Slack 메시지 작성
    message = (
        ":rotating_light: *새로운 랜섬웨어 피해 사이트 발견!* :rotating_light:\n\n"
        "🚨 *긴급 알림*\n\n"
        "🔴 *감염된 도메인 목록:*\n"
    )

    # 도메인 목록 추가 (최대 20개만 표시)
    message += "\n".join([f"🔴 `{domain}`" for domain in new_domains[:20]])

    payload = {"text": message}

    try:
        response = requests.post(SLACK_WEBHOOK_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"})
        if response.status_code == 200:
            print("✅ Slack 알림 전송 성공!")
        else:
            print(f"⚠️ Slack 전송 실패: {response.status_code}, 응답: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Slack 전송 중 오류 발생: {e}")

# ✅ 3️⃣ Flask 앱 실행 + DB 감시 스레드 시작
if __name__ == '__main__':
    threading.Thread(target=watch_db_updates, daemon=True).start()
    app.run(debug=True, host='0.0.0.0', port=5000)
