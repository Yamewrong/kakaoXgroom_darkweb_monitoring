import json
import time
import schedule
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 🔥 Tor 프록시 설정
FIREFOX_TOR_PROXY = "127.0.0.1:9050"

# 📂 쿠키 저장 JSON 파일
CONFIG_FILE = "config.json"

# 📌 크롤링할 대상 사이트 (.onion 도메인)
TARGET_URL = "http://ransomxifxwc5eteopdobynonjctkxxvap77yqifu2emfbecgbqdw6qd.onion/"

def load_existing_config():
    """기존 config.json 파일을 로드 (없으면 빈 딕셔너리 반환)"""
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def fetch_cookies_with_selenium():
    """Selenium을 사용하여 Tor 네트워크를 통해 쿠키 크롤링"""
    options = Options()
    options.headless = False  # 🛑 디버깅을 위해 False (문제 해결 후 True로 변경 가능)
    options.set_preference("network.proxy.type", 1)
    options.set_preference("network.proxy.socks", "127.0.0.1")
    options.set_preference("network.proxy.socks_port", 9050)

    driver = webdriver.Firefox(options=options)

    try:
        print(f"🔍 {TARGET_URL} 접속 중...")
        driver.get(TARGET_URL)

        # 페이지가 완전히 로딩될 때까지 기다림
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(5)  # 추가 대기 (JS 동적 데이터 로드 고려)

        # 현재 페이지의 쿠키 가져오기
        cookies = driver.get_cookies()

        if not cookies:
            print("⚠️ 쿠키가 감지되지 않았습니다!")
            return None

        # ✅ 크롤링된 쿠키 출력
        cookie_dict = {cookie["name"]: cookie["value"] for cookie in cookies}
        print(f"✅ 크롤링된 쿠키: {cookie_dict}")

        return cookie_dict

    except Exception as e:
        print(f"❌ Selenium 쿠키 크롤링 오류: {e}")
        return None

    finally:
        driver.quit()

def save_cookies_to_config(cookies):
    """새로운 쿠키 값을 config.json 파일에 저장"""
    if not cookies:
        print("❌ 저장할 쿠키 값이 없습니다.")
        return

    # 기존 설정 불러오기
    config = load_existing_config()

    # 해당 사이트 정보 업데이트
    site_key = TARGET_URL.replace("http://", "").replace("/", "")
    config[site_key] = {
        "method": "cookie",
        "cookies": cookies
    }

    # JSON 파일 업데이트
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
        print(f"✅ 쿠키 정보가 {CONFIG_FILE}에 저장되었습니다!")
    except Exception as e:
        print(f"❌ config.json 저장 오류: {e}")

# ✅ 1시간마다 실행할 작업
def job():
    """최초 실행 및 1시간마다 실행될 작업"""
    print(f"🔍 {TARGET_URL}에서 Selenium을 이용해 쿠키 크롤링 중...")
    cookies = fetch_cookies_with_selenium()

    if cookies:
        save_cookies_to_config(cookies)
    else:
        print("❌ 쿠키 저장 실패. 다시 시도해주세요.")

# ✅ 최초 실행 즉시 수행
job()

# 🔥 5분마다 실행하도록 스케줄 설정
schedule.every(5).minutes.do(job)

# **백그라운드 실행 유지**
if __name__ == "__main__":
    print("🔄 쿠키 크롤링 시작 (5분마다 자동 실행)...")
    while True:
        schedule.run_pending()
        time.sleep(60)  # 1분마다 실행 여부 확인
