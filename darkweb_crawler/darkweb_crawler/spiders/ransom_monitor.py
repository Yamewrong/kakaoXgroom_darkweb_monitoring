import os
import time
import json
import requests
import sqlite3
from bs4 import BeautifulSoup

# 토르 프로키지 설정
PROXIES = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050",
}

# 다크웨브 사이트별 인증 방식 (하드코딩된 쿠키 적용)
AUTH_METHODS = {
    "ransomxifxwc5eteopdobynonjctkxxvap77yqifu2emfbecgbqdw6qd.onion": {
        "method": "cookie",
        "cookies": {
            "_uuid": "92a6e52e-cd1e-441f-ad58-5109609e331e",
            "_token": "7357914022"
        }
    }
}

# Slack Webhook URL
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

# SQLite DB 설정
DB_FILE = "ransomware_domains.db"

def setup_database():
    """SQLite DB를 생성하고 테이블을 초기화"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS domains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site TEXT NOT NULL,
            domain TEXT NOT NULL UNIQUE,
            upload_time TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_to_db(site, domain, upload_time):
    """새로운 도메인을 DB에 저장 (중복 방지)"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO domains (site, domain, upload_time) VALUES (?, ?, ?)", (site, domain, upload_time))
        conn.commit()
        return True  # 새로 추가된 경우
    except sqlite3.IntegrityError:
        return False  # 중복된 경우
    finally:
        conn.close()

def authenticate(site):
    """사이트별 인증 방식 적용 (하드코딩된 쿠키 사용)"""
    auth_config = AUTH_METHODS.get(site)
    session = requests.Session()
    if auth_config and auth_config["method"] == "cookie":
        session.cookies.update(auth_config["cookies"])
        print(f"🔑 {site} 하드코딩된 쿠키 인증 완료")
    return session

def send_slack_alert(message):
    """Slack 알림 전송"""
    payload = {"text": message}
    requests.post(SLACK_WEBHOOK_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"})

def crawl_domains(target_url):
    """랜섬웨어 사이트에서 도메인 크롤링"""
    site = target_url.replace("http://", "").replace("/", "")
    session = authenticate(site)

    try:
        response = session.get(target_url, proxies=PROXIES, timeout=30)

        if response.status_code == 401:
            print(f"❌ {target_url} 인증 실패 (401 Unauthorized) - 하드코딩된 쿠키 확인 필요")
            return []

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        domains = []

        # ✅ 페이지에서 크롤링된 HTML 일부를 출력
        print(f"🔍 [디버깅] 크롤링된 HTML 일부:\n{soup.prettify()[:1000]}")  # 1000자까지만 출력

        for card in soup.find_all("div", class_="col-12 col-md-6 col-lg-4"):
            anchor_tag = card.find("a", class_="index-anchor")

            if anchor_tag:
                domain_text = card.find("div", class_="card-title").text.strip()

                # 📌 업로드 시간 가져오기
                upload_time_div = card.find("div", class_="card-footer")
                upload_time = upload_time_div.text.strip() if upload_time_div else "N/A"

                # 📌 확장된 도메인 필터 적용
                if domain_text.endswith((".com", ".net", ".org", ".edu", ".za", ".ma", ".ca", ".vn",
                                        ".bank", ".in", ".th", ".uk", ".my", ".tr", ".br", ".sg",
                                        ".es", ".au", ".pl", ".cr", ".it", ".il", ".de", ".br")):
                    domains.append((domain_text, upload_time))

            else:
                print(f"⚠️ {target_url}: index-anchor 태그 없음, 건너뜀")


        return domains

    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패 ({target_url}): {e}")

    return []



def monitor_ransomware_sites():
    """랜섬웨어 사이트들을 주기적으로 모니터링"""
    setup_database()
    targets = [
        "http://ransomxifxwc5eteopdobynonjctkxxvap77yqifu2emfbecgbqdw6qd.onion/",
    ]

    for target_url in targets:
        print(f"🔍 {target_url} 크롤링 중...")
        domains = crawl_domains(target_url)
        
        if domains:
            new_count = 0
            for domain, upload_time in domains:
                if save_to_db(target_url, domain, upload_time):
                    new_count += 1
            
            # ✅ 처음 크롤링 시 Slack 알림 전송
            if new_count == len(domains):
                send_slack_alert(f"🚨 {target_url} 에서 {new_count}개의 도메인 크롤링 완료!")

            # ✅ 새로운 도메인이 추가되면 Slack 알림 전송
            elif new_count > 0:
                send_slack_alert(f"🆕 {target_url} 에서 {new_count}개의 새로운 도메인이 감지됨!")

        else:
            print(f"❌ {target_url}에서 도메인 크롤링 실패!")

# 🔥 실행
if __name__ == "__main__":
    monitor_ransomware_sites()
