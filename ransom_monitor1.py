#크롤러


import requests
import sqlite3
import json
from bs4 import BeautifulSoup
import time
import datetime
import re
from urllib.parse import urlparse, urljoin

flag = 1

# 사용자 정의 User-Agent 헤더
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/103.0.0.0 Safari/537.36"
}

# Tor 프록시 세션 생성 (9150 포트 사용)
def get_tor_session():
    session = requests.Session()
    session.proxies = {
        "http": "socks5h://127.0.0.1:9150",
        "https": "socks5h://127.0.0.1:9150"
    }
    session.headers.update(HEADERS)
    return session

# 특정 onion 사이트에 대해 하드코딩된 인증 정보 (예시)
AUTH_METHODS = {
    'http://dataleakypypu7uwblm5kttv726l3iripago6p336xjnbstkjwrlnlid.onion/': {
        "sid": "73fddff8-bbbe-4295-96bb-0f18698d3866"
    }
}

# Slack Webhook URL (실제 값으로 변경하세요)
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

def send_slack_notification(message):
    """Slack 알림 전송 함수"""
    payload = {"text": message}
    requests.post(SLACK_WEBHOOK_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"})

# SQLite DB 초기화 및 테이블 생성 (upload_date 컬럼 추가)
DB_FILE = "cj_ransomware_domains.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS domains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site TEXT NOT NULL,
            domain TEXT NOT NULL UNIQUE,
            upload_date TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn

def store_domain(conn, site, domain, upload_date):
    """
    도메인과 추출된 날짜를 DB에 저장.
    중복된 도메인은 저장하지 않으며, 새 도메인일 경우 True 반환.
    """
    cursor = conn.cursor()
    timestamp = datetime.datetime.utcnow().isoformat()
    try:
        cursor.execute('INSERT INTO domains (site, domain, upload_date) VALUES (?, ?, ?)', 
                       (site, domain, upload_date))
        conn.commit()
        return True  # 새로운 도메인 저장됨
    except sqlite3.IntegrityError:
        # 이미 저장된 도메인인 경우
        return False

# 스크리닝할 TLD 목록 (중복되는 항목은 제거)
VALID_TLDS = ('.com', '.net', '.org', '.edu', '.za', '.ma', '.ca', '.vn', 
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
            '.ye', '.zm', '.zw')


def is_valid_domain(domain):
    """
    도메인이 미리 정의한 TLD 목록 중 하나로 끝나는지 확인.
    """
    domain = domain.strip().lower()
    return any(domain.endswith(tld) for tld in VALID_TLDS)

def extract_upload_date(tag):
    """
    태그 내부 및 주변 텍스트에서 날짜 패턴(연도-월-일 또는 일/월/연도)을 검색하여 반환.
    """
    text = tag.get_text(separator=" ", strip=True)
    match = re.search(r'\b(?:\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{4})\b', text)
    if match:
        return match.group(0)
    
    # 부모 태그에서 날짜 검색
    if tag.parent:
        parent_text = tag.parent.get_text(separator=" ", strip=True)
        match = re.search(r'\b(?:\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{4})\b', parent_text)
        if match:
            return match.group(0)
    
    # 이전 형제 태그에서 검색
    previous_sibling = tag.find_previous_sibling(text=True)
    if previous_sibling:
        match = re.search(r'\b(?:\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{4})\b', previous_sibling)
        if match:
            return match.group(0)
    
    # 다음 형제 태그에서 검색
    next_sibling = tag.find_next_sibling(text=True)
    if next_sibling:
        match = re.search(r'\b(?:\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{4})\b', next_sibling)
        if match:
            return match.group(0)
    
    return None

def extract_domains_and_dates(html):
    """
    HTML 내의 지정 태그들에서 도메인과 해당 태그 주변의 날짜를 추출하여
    도메인:날짜 형태의 딕셔너리로 반환.
    """
    soup = BeautifulSoup(html, "html.parser")
    domains_dates = {}
    # 조사할 태그 목록 지정
    tags_to_check = ['a', 'strong', 'code', 'span', 'pre', 'p', 'div', 'h1', 'h2', 'h3', 'h4', 'li', 'b', 'img']
    
    for tag in soup.find_all(tags_to_check):
        text = tag.get_text(strip=True)
        if text:
            # 태그 내부의 텍스트에서 도메인 패턴 검색
            found = re.findall(r'(?:https?://)?((?:www\.)?[a-z0-9][a-z0-9-]*(?:\.[a-z0-9][a-z0-9-]*)+\b)', text, re.IGNORECASE)
            for domain in found:
                if is_valid_domain(domain):
                    # 도메인이 처음 발견되면 해당 태그에서 날짜 추출
                    if domain not in domains_dates:
                        upload_date = extract_upload_date(tag)
                        domains_dates[domain] = upload_date
    return domains_dates

def crawl(url, depth, max_depth, session, conn, visited):
    if depth > max_depth:
        return
    if url in visited:
        return
    visited.add(url)
    print(f"[Depth {depth}] Crawling: {url}")

    parsed_url = urlparse(url)
    site = parsed_url.netloc
    cookies = AUTH_METHODS.get(site, None)
    global flag
    
    try:
        response = session.get(url, cookies=cookies, timeout=20)
        content_type = response.headers.get("Content-Type", "")
        print("Content-Type:", content_type)
        
        if response.status_code != 200:
            print(f"페이지 로드 실패 ({url}): 상태 코드 {response.status_code}")
            return

        html = response.text

        # Content-Type 헤더가 있으면 해당 헤더 기반으로 HTML 여부 판단
        if content_type:
            if "text/html" not in content_type:
                print(f"HTML이 아닌 콘텐츠입니다. 건너뜁니다: {url}")
                return
        else:
            stripped_html = html.lstrip().lower()
            if not (stripped_html.startswith("<!doctype html") or stripped_html.startswith("<html")):
                print(f"HTML이 아닌 콘텐츠입니다. 건너뜁니다: {url}")
                return

    except Exception as e:
        print(f"요청 중 에러 발생 ({url}):", e)
        return

    try:
        # 도메인과 날짜를 함께 추출
        domains_dates = extract_domains_and_dates(html)
    except Exception as e:
        print(f"HTML 파싱 중 에러 발생 ({url}):", e)
        return

    for domain, upload_date in domains_dates.items():
        if store_domain(conn, site, domain, upload_date):
            msg = f"새 도메인 발견 ({site}): {domain}, 날짜: {upload_date if upload_date else 'N/A'}"
            print(msg)
            if flag == 0:
                send_slack_notification(msg)
                flag = 1
    
    # 같은 사이트 내의 링크 재귀적 크롤링
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a", href=True):
        link = urljoin(url, a['href'])
        if urlparse(link).netloc == site:
            crawl(link, depth + 1, max_depth, session, conn, visited)

def main():
    # 크롤링 대상 onion URL (실제 URL로 변경)
    
    
    target_onion_url = ["http://pdcizqzjitsgfcgqeyhuee5u6uki6zy5slzioinlhx6xjnsw25irdgqd.onion/",
                        "http://5butbkrljkaorg5maepuca25oma7eiwo6a2rlhvkblb4v6mf3ki2ovid.onion/",
                        "http://nz4z6ruzcekriti5cjjiiylzvrmysyqwibxztk6voem4trtx7gstpjid.onion/",
                        "http://rnsm777cdsjrsdlbs4v5qoeppu3px6sb2igmh53jzrx7ipcrbjz5b2ad.onion/",
                        "http://weg7sdx54bevnvulapqu6bpzwztryeflq3s23tegbmnhkbpqz637f2yd.onion/",
                        "http://arcuufpr5xxbbkin4mlidt7itmr6znlppk63jbtkeguuhszmc5g7qdyd.onion/",
                        "http://jbmk7h6xlkedn2gg5yi76zca6y3jgdlp5wchlsrd7735tlnrmmvqe5ad.onion/",
                        "http://7ukmkdtyxdkdivtjad57klqnd3kdsmq6tp45rrsxqnu76zzv3jvitlqd.onion/",
                        "http://nsalewdnfclsowcal6kn5csm4ryqmfpijznxwictukhrgvz2vbmjjjyd.onion/",
                        "http://nerqnacjmdy3obvevyol7qhazkwkv57dwqvye5v46k5bcujtfa6sduad.onion/"]

    max_depth = 0          # 재귀적 크롤링 최대 깊이
    crawl_interval = 3600  # 크롤링 주기 (초 단위, 예: 1시간)
    
    session = get_tor_session()
    conn = init_db()
    
    # 주기적 크롤링의 경우 주석 해제 후 사용
    """
    while True:
        visited = set()
        print("크롤링 시작...")
        crawl(target_onion_url, 0, max_depth, session, conn, visited)
        print(f"{crawl_interval}초 후 다시 크롤링합니다...")
        time.sleep(crawl_interval)
    """
    
    visited = set()
    print("크롤링 시작...")
    for i in range(0, len(target_onion_url)):
        crawl(target_onion_url[i], 0, max_depth, session, conn, visited)

if __name__ == "__main__":
    main()
