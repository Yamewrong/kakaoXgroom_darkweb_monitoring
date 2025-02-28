import requests
import sqlite3
import json
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urlparse, urljoin

new_domain_count = 0

# 사용자 정의 User-Agent 헤더
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/103.0.0.0 Safari/537.36"
}

# Tor 프록시 세션 생성
def get_tor_session():
    session = requests.Session()
    session.proxies = {
        "http": "socks5h://127.0.0.1:9050",
        "https": "socks5h://127.0.0.1:9050"
    }
    session.headers.update(HEADERS)
    return session

# SQLite DB 설정
DB_FILE = "victim.db"

def init_db():
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
    return conn

# ✅ DB에서 도메인 존재 여부 확인
def is_domain_in_db(conn, domain):
    """DB에 해당 도메인이 있는지 확인"""
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM leaks WHERE domain = ?", (domain,))
    exists = cursor.fetchone() is not None
    return exists

# WHOIS API 설정
WHOISXML_API_KEY = ""

def get_domain_country(domain, max_retries=3, timeout=10):
    """WHOIS API를 사용하여 도메인의 국가 정보를 조회 (재시도 및 예외 처리 포함)"""
    api_url = f"https://www.whoisxmlapi.com/whoisserver/WhoisService?apiKey={WHOISXML_API_KEY}&domainName={domain}&outputFormat=JSON"

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(api_url, timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                country = data.get("WhoisRecord", {}).get("registrant", {}).get("country", "Unknown")
                return country if country else "Unknown"

            print(f"⚠️ WHOIS 요청 실패 (도메인: {domain}) - 응답 코드 {response.status_code}")
            return "Unknown"

        except requests.exceptions.ReadTimeout:
            print(f"⏳ WHOIS 조회 시간 초과 (도메인: {domain}, 재시도 {attempt}/{max_retries})")
        except requests.exceptions.RequestException as e:
            print(f"❌ WHOIS 요청 오류 (도메인: {domain}): {e}")
            return "Unknown"

        # 재시도 전 5초 대기
        time.sleep(5)

    print(f"❌ 최종 WHOIS 요청 실패 (도메인: {domain}) - 모든 재시도 실패")
    return "Unknown"

# ✅ 데이터 저장 (기존 DB에 없는 도메인만 WHOIS 조회)
def store_domain(conn, site, domain, upload_date):
    global new_domain_count
    cursor = conn.cursor()

    if is_domain_in_db(conn, domain):
        return False  # 기존 도메인이므로 무시

    # 새로운 도메인이므로 WHOIS API 조회
    country = get_domain_country(domain)

    try:
        cursor.execute('INSERT INTO leaks (site, domain, upload_time, country) VALUES (?, ?, ?, ?)', 
                       (site, domain, upload_date, country))
        conn.commit()
        new_domain_count += 1
        return True
    except sqlite3.IntegrityError:
        return False

# ✅ TLD 필터링
# ✅ 스크리닝할 TLD 목록 (원래 리스트 100% 유지)
VALID_TLDS = (
    '.com', '.net', '.org', '.edu', '.za', '.ma', '.ca', '.vn', 
    '.bank', '.in', '.th', '.uk', '.my', '.tr', '.br', '.sg', '.es', 
    '.au', '.pl', '.cr', '.it', '.il', '.de', '.af', '.ax', '.al', 
    '.dz', '.as', '.ad', '.ao', '.ai', '.aq', '.ag', '.ar', '.am', 
    '.aw', '.at', '.az', '.bs', '.bh', '.bd', '.bb', '.by', '.be', 
    '.bz', '.bj', '.bm', '.bt', '.bo', '.bq', '.ba', '.bw', '.bv', 
    '.io', '.bn', '.bg', '.bf', '.bi', '.cv', '.kh', '.cm', '.ky', 
    '.cf', '.td', '.cl', '.cn', '.cx', '.cc', '.co', '.km', '.cg', 
    '.cd', '.ck', '.ci', '.hr', '.cu', '.cw', '.cy', '.cz', '.dk', 
    '.dj', '.dm', '.do', '.ec', '.eg', '.sv', '.gq', '.er', '.ee', 
    '.sz', '.et', '.fk', '.fo', '.fj', '.fi', '.fr', '.gf', '.pf', 
    '.tf', '.ga', '.gm', '.ge', '.gh', '.gi', '.gr', '.gl', '.gd', 
    '.gp', '.gu', '.gt', '.gg', '.gn', '.gw', '.gy', '.ht', '.hm', 
    '.va', '.hn', '.hk', '.hu', '.is', '.id', '.ir', '.iq', '.ie', 
    '.im', '.jm', '.jp', '.je', '.jo', '.kz', '.ke', '.ki', '.kp', 
    '.kr', '.kw', '.kg', '.la', '.lv', '.lb', '.ls', '.lr', '.ly', 
    '.li', '.lt', '.lu', '.mo', '.mg', '.mw', '.mv', '.ml', '.mt', 
    '.mh', '.mq', '.mr', '.mu', '.yt', '.mx', '.fm', '.md', '.mc', 
    '.mn', '.me', '.ms', '.mz', '.mm', '.na', '.nr', '.np', '.nl', 
    '.nc', '.nz', '.ni', '.ne', '.ng', '.nu', '.nf', '.mp', '.no', 
    '.om', '.pk', '.pw', '.ps', '.pa', '.pg', '.py', '.pe', '.ph', 
    '.pn', '.pt', '.pr', '.qa', '.re', '.ro', '.ru', '.rw', '.bl', 
    '.sh', '.kn', '.lc', '.mf', '.pm', '.vc', '.ws', '.sm', '.st', 
    '.sa', '.sn', '.rs', '.sc', '.sl', '.sx', '.sk', '.si', '.sb', 
    '.so', '.gs', '.ss', '.lk', '.sd', '.sr', '.sj', '.se', '.ch', 
    '.sy', '.tw', '.tj', '.tz', '.tl', '.tg', '.tk', '.to', '.tt', 
    '.tn', '.tm', '.tc', '.tv', '.ug', '.ua', '.ae', '.gb', '.us', 
    '.um', '.uy', '.uz', '.vu', '.ve', '.vg', '.vi', '.wf', '.eh', 
    '.ye', '.zm', '.zw'
)


def is_valid_domain(domain):
    """도메인이 미리 정의한 TLD 목록 중 하나로 끝나는지 확인"""
    return any(domain.endswith(tld) for tld in VALID_TLDS)

# ✅ 날짜 추출
def extract_upload_date(tag):
    """태그 내부에서 날짜 패턴(YYYY-MM-DD 또는 DD/MM/YYYY) 검색"""
    text = tag.get_text(separator=" ", strip=True)
    match = re.search(r'\b(?:\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{4})\b', text)
    return match.group(0) if match else None

# ✅ 도메인 & 날짜 추출
def extract_domains_and_dates(html):
    """HTML에서 도메인과 날짜를 추출하여 딕셔너리 반환"""
    soup = BeautifulSoup(html, "html.parser")
    domains_dates = {}
    tags_to_check = ['a', 'strong', 'code', 'span', 'pre', 'p', 'div', 'h1', 'h2', 'h3']

    for tag in soup.find_all(tags_to_check):
        text = tag.get_text(strip=True)
        found_domains = re.findall(r'(?:https?://)?([a-z0-9.-]+\.[a-z]{2,})', text, re.IGNORECASE)
        for domain in found_domains:
            if is_valid_domain(domain) and domain not in domains_dates:
                domains_dates[domain] = extract_upload_date(tag)
    return domains_dates

# ✅ 재귀 크롤링
def crawl(url, depth, max_depth, session, conn, visited):
    if depth > max_depth or url in visited:
        return
    visited.add(url)

    parsed_url = urlparse(url)
    site = parsed_url.netloc

    try:
        response = session.get(url, timeout=30)
        if response.status_code != 200:
            print(f"페이지 로드 실패 ({url}): 상태 코드 {response.status_code}")
            return

        html = response.text
        domains_dates = extract_domains_and_dates(html)

        for domain, upload_date in domains_dates.items():
            store_domain(conn, site, domain, upload_date)

        # 내부 링크 재귀 크롤링
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a", href=True):
            link = urljoin(url, a['href'])
            if urlparse(link).netloc == site:
                crawl(link, depth + 1, max_depth, session, conn, visited)

    except Exception as e:
        print(f"요청 실패 ({url}): {e}")

# ✅ 메인 크롤링 실행
def main():
    global new_domain_count

    target_onion_urls = [
        "http://pdcizqzjitsgfcgqeyhuee5u6uki6zy5slzioinlhx6xjnsw25irdgqd.onion/",
        "http://5butbkrljkaorg5maepuca25oma7eiwo6a2rlhvkblb4v6mf3ki2ovid.onion/"
    ]
    
    max_depth = 0
    crawl_interval = 3600  # 1시간마다 실행

    session = get_tor_session()
    conn = init_db()

    while True:
        visited = set()
        new_domain_count = 0
        print("🔍 크롤링 시작...")

        for url in target_onion_urls:
            crawl(url, 0, max_depth, session, conn, visited)

        print(f"✅ 크롤링 완료! {new_domain_count}개의 새로운 도메인 추가됨")
        print(f"{crawl_interval}초 후 다시 크롤링 시작...")
        time.sleep(crawl_interval)

if __name__ == "__main__":
    main()
