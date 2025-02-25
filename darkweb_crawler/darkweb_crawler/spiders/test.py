import time
import sqlite3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from stem.control import Controller

# 🔥 Tor 프록시 설정 (Selenium용)
TOR_PROXY = "socks5h://127.0.0.1:9050"

# ✅ SQLite DB 설정
DB_FILE = "test.db"

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

def renew_tor_ip():
    """Tor 네트워크에서 새로운 아이덴티티 요청 (IP 변경)"""
    try:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate()
            controller.signal("NEWNYM")
        time.sleep(5)  # 변경 후 안정화 시간
        print("✅ 새로운 Tor 아이덴티티 적용됨!")
    except Exception as e:
        print(f"⚠️ Tor IP 변경 실패: {e}")

def get_selenium_driver():
    """Selenium WebDriver 설정 (Tor 네트워크 사용)"""
    options = Options()
    options.headless = True  # 브라우저 창 없이 실행
    options.set_preference("network.proxy.type", 1)
    options.set_preference("network.proxy.socks", "127.0.0.1")
    options.set_preference("network.proxy.socks_port", 9050)
    driver = webdriver.Firefox(options=options)
    return driver

def crawl_domains(target_url):
    """랜섬웨어 사이트에서 도메인 크롤링 (Selenium + Tor)"""
    driver = get_selenium_driver()
    try:
        driver.get(target_url)
        time.sleep(5)  # JavaScript가 렌더링될 시간을 줌

        soup = BeautifulSoup(driver.page_source, "html.parser")
        print("🔍 [디버깅] 크롤링된 HTML 일부:\n", soup.prettify()[:500])

        domains = []
        for link in soup.find_all("a"):
            domain_text = link.text.strip()
            if domain_text and "." in domain_text:  # 간단한 필터링
                domains.append((domain_text, "N/A"))  # 업로드 시간 없음 처리

        return domains

    except Exception as e:
        print(f"❌ 요청 실패: {e}")
        return []
    finally:
        driver.quit()

def monitor_ransomware_sites():
    """랜섬웨어 사이트들을 주기적으로 모니터링"""
    setup_database()
    targets = [
        "http://zohlm7ahjwegcedoz7lrdrti7bvpofymcayotp744qhx6gjmxbuo2yid.onion/"
    ]

    for target_url in targets:
        print(f"🔍 {target_url} 크롤링 중...")
        renew_tor_ip()  # IP 변경 후 요청
        domains = crawl_domains(target_url)
        
        if domains:
            new_count = 0
            for domain, upload_time in domains:
                if save_to_db(target_url, domain, upload_time):
                    new_count += 1
            
            print(f"✅ {target_url} 에서 {new_count}개의 새로운 도메인 추가됨!")
        else:
            print(f"❌ {target_url}에서 도메인 크롤링 실패!")

# 🔥 실행
if __name__ == "__main__":
    monitor_ransomware_sites()
