import os
import json
import sqlite3
import time
import requests
import schedule
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re  # 날짜 변환을 위한 정규 표현식

# 🔥 Tor 프록시 설정
PROXIES = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050",
}

# 📂 SQLite DB 설정
DB_FILE = "victim.db"

# ✅ 1️⃣ 데이터베이스 설정
def setup_database():
    """SQLite 데이터베이스 생성 및 테이블 초기화"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leaks (
            site TEXT NOT NULL,
            domain TEXT NOT NULL UNIQUE,
            upload_time TEXT DEFAULT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("✅ 데이터베이스가 설정되었습니다.")


# ✅ 2️⃣ 날짜 변환 함수
def convert_date_format(date_str):
    """DD/MM/YYYY → YYYY-MM-DD 변환"""
    match = re.match(r"(\d{2})/(\d{2})/(\d{4})", date_str)
    if match:
        day, month, year = match.groups()
        return f"{year}-{month}-{day}"  # YYYY-MM-DD 형식으로 변환
    return None  # 잘못된 형식이면 None 반환

# ✅ 3️⃣ Selenium을 사용한 `.onion` 사이트 크롤링
def crawl_leaks_with_selenium(target_url):
    """Selenium을 사용하여 JavaScript 기반 `.onion` 사이트 크롤링"""

    options = Options()
    options.headless = True  # 🛑 백그라운드 실행을 위해 True 설정
    options.set_preference("network.proxy.type", 1)
    options.set_preference("network.proxy.socks", "127.0.0.1")
    options.set_preference("network.proxy.socks_port", 9050)
    options.set_preference("network.proxy.socks_remote_dns", True)  # DNS를 Tor 통해 처리

    driver = webdriver.Firefox(options=options)

    try:
        print(f"🔍 {target_url} 접속 중...")
        driver.get(target_url)

        # 페이지가 완전히 로드될 때까지 기다림
        WebDriverWait(driver, 90).until(
            EC.presence_of_element_located((By.CLASS_NAME, "cls_recordMiddle"))  # 도메인 데이터가 있는 요소
        )
        time.sleep(10)  # 추가 대기 (JS 동적 데이터 로드 고려)

        # 페이지 스크롤을 아래로 내려서 추가 데이터 로딩 유도
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

        # 🔎 크롤링된 HTML 분석
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        extracted_data = []

        # 🔍 `.cls_recordMiddle` 및 `.cls_recordBottom` 클래스를 포함하는 모든 요소에서 도메인 + Action date 추출
        records = soup.find_all("div", class_="cls_record")
        for record in records:
            # 도메인 정보 찾기
            domain_element = record.find("div", class_="cls_recordMiddle")
            action_date_element = None

            # `cls_recordBottom` 내부에서 "Action date:"를 찾고, 그 다음 <div>을 가져옴
            record_bottom = record.find("div", class_="cls_recordBottom")
            if record_bottom:
                date_labels = record_bottom.find_all("div", class_="cls_headerSmall")
                for label in date_labels:
                    if "Action date:" in label.get_text(strip=True):
                        action_date_element = label.find_next_sibling("div")
                        break  # 첫 번째 매칭 요소만 사용

            # 도메인과 날짜 데이터 추출
            if domain_element and action_date_element:
                domain_text = domain_element.get_text(strip=True)
                action_date_text = action_date_element.get_text(strip=True)
                action_date_text = convert_date_format(action_date_text)  # 날짜 변환

                # URL 형식 확인 및 데이터 추가
                if domain_text.startswith("http") and "." in domain_text and action_date_text:
                    extracted_data.append((domain_text, action_date_text))

        return extracted_data

    except Exception as e:
        print(f"❌ Selenium 크롤링 오류: {e}")
        return []

    finally:
        driver.quit()

# ✅ 4️⃣ 데이터 저장 함수 (upload_time 포함)
def save_to_db(site, domain, upload_time):
    """DB에 데이터 저장 및 중복 확인"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO leaks (site, domain, upload_time)
            VALUES (?, ?, ?)
            ON CONFLICT(domain) DO UPDATE SET upload_time = excluded.upload_time
        """, (site, domain, upload_time))
        conn.commit()
        return True  # 새 데이터 추가됨
    except sqlite3.IntegrityError:
        return False  # 중복 데이터
    finally:
        conn.close()

# ✅ 5️⃣ 실행 코드 (1시간마다 실행)
def job():
    """크롤링 및 DB 저장 작업 실행"""
    setup_database()
    target_url = "http://zohlm7ahjwegcedoz7lrdrti7bvpofymcayotp744qhx6gjmxbuo2yid.onion/"

    print(f"🔍 {target_url} 크롤링 중...")
    extracted_data = crawl_leaks_with_selenium(target_url)

    if extracted_data:
        new_count = 0
        for domain, upload_time in extracted_data:
            if save_to_db(target_url, domain, upload_time):
                new_count += 1

        # ✅ 새로운 데이터가 있을 때만 출력
        if new_count > 0:
            print(f"✅ 크롤링 완료! {new_count}개의 새로운 데이터 저장됨")
        else:
            print(f"✅ 크롤링 완료! 새로운 데이터 없음")

# ✅ 최초 실행 즉시 수행
job()

# 🔥 1시간마다 실행하도록 스케줄 설정
schedule.every(1).hours.do(job)

# **백그라운드에서 실행**
if __name__ == "__main__":
    print("🔄 랜섬웨어 사이트 모니터링 시작 (1시간마다 자동 실행)...")
    while True:
        schedule.run_pending()
        time.sleep(60)  # 1분마다 스케줄 확인
