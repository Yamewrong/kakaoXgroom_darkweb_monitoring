import os
import time
import json
import requests
import sqlite3
import schedule
from bs4 import BeautifulSoup

# 🔥 Tor 프록시 설정
PROXIES = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050",
}

# 📂 SQLite DB 설정
DB_FILE = "victim.db"

# 📂 쿠키 정보 저장된 JSON 파일
CONFIG_FILE = "config.json"

#🔍 WHOIS API 설정
WHOIS_API_KEY = ""
WHOIS_URL = "https://www.whoisxmlapi.com/whoisserver/WhoisService"

# 📌 도메인 필터 규칙
VALID_DOMAINS = (
    ".com", ".net", ".org", ".edu", ".za", ".ma", ".ca", ".vn", ".bank",
    ".in", ".th", ".uk", ".my", ".tr", ".br", ".sg", ".es", ".au", ".pl",
    ".cr", ".it", ".il", ".de", ".br"
)

def load_config():
    """JSON 파일에서 쿠키 및 인증 정보 로드"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def setup_database():
    """SQLite 데이터베이스 생성 및 테이블 초기화"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leaks (
            site TEXT NOT NULL,
            domain TEXT NOT NULL UNIQUE,
            upload_time TEXT DEFAULT NULL,
            country TEXT DEFAULT 'Unknown',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("✅ 데이터베이스가 설정되었습니다.")

def is_domain_in_db(domain):
    """DB에 해당 도메인이 있는지 확인"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM leaks WHERE domain = ?", (domain,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def get_domain_country(domain):
    """WHOIS API를 사용하여 도메인의 국가 정보 조회 (새로운 도메인만 조회)"""
    params = {
        "apiKey": WHOIS_API_KEY,
        "domainName": domain,
        "outputFormat": "json"
    }

    try:
        response = requests.get(WHOIS_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # 국가 정보 추출
        return data.get("WhoisRecord", {}).get("registrant", {}).get("country", "Unknown")

    except requests.exceptions.RequestException as e:
        print(f"❌ WHOIS 요청 실패 ({domain}): {e}")
        return "Unknown"

def save_to_db(site, domain, upload_time):
    """새로운 도메인을 DB에 저장 (기존 DB에 없을 때만 WHOIS 조회)"""
    if is_domain_in_db(domain):
        return False  # 중복된 경우 저장 안 함

    # WHOIS API로 국가 정보 조회 (새로운 도메인일 때만 실행)
    country = get_domain_country(domain)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO leaks (site, domain, upload_time, country) VALUES (?, ?, ?, ?)",
            (site, domain, upload_time, country)
        )
        conn.commit()
        return True  # 새로 추가된 경우
    except sqlite3.IntegrityError:
        return False  # 중복된 경우
    finally:
        conn.close()

def authenticate(site):
    """사이트별 인증 방식 적용 (config.json에서 쿠키 정보 로드)"""
    config = load_config()
    auth_config = config.get(site, {})

    session = requests.Session()
    if auth_config and auth_config.get("method") == "cookie":
        session.cookies.update(auth_config["cookies"])
    return session

def crawl_domains(target_url):
    """랜섬웨어 사이트에서 도메인 크롤링"""
    site = target_url.replace("http://", "").replace("/", "")
    session = authenticate(site)

    try:
        response = session.get(target_url, proxies=PROXIES, timeout=30)

        if response.status_code == 401:
            print(f"❌ {target_url} 인증 실패 (401 Unauthorized) - 쿠키 갱신 필요!")
            return []

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        domains = []

        for card in soup.find_all("div", class_="col-12 col-md-6 col-lg-4"):
            anchor_tag = card.find("a", class_="index-anchor")

            if anchor_tag:
                domain_text = card.find("div", class_="card-title").text.strip()

                # 📌 업로드 시간 가져오기
                upload_time_div = card.find("div", class_="card-footer")
                upload_time = upload_time_div.text.strip() if upload_time_div else "N/A"

                # 📌 ✅ 도메인 필터 추가
                if domain_text.endswith(VALID_DOMAINS):
                    domains.append((domain_text, upload_time))

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

            if new_count > 0:
                print(f"✅ 크롤링 완료! {new_count}개의 새로운 데이터 저장됨")
            else:
                print(f"✅ 크롤링 완료! 새로운 데이터 없음")

def job():
    """최초 실행 및 1시간마다 실행될 작업"""
    monitor_ransomware_sites()

# ✅ 최초 실행 즉시 수행
job()

# 🔥 1시간마다 실행하도록 스케줄 설정
schedule.every(1).hours.do(job)

# **백그라운드 실행 유지**
if __name__ == "__main__":
    print("🔄 랜섬웨어 사이트 모니터링 시작 (1시간마다 자동 실행)...")
    while True:
        schedule.run_pending()
        time.sleep(60)  # 1분마다 실행 여부 확인
