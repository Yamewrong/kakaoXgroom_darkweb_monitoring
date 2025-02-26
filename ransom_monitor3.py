#OSINT 유출된 사이트 나라 검색

import sqlite3
import requests

def ensure_country_column_exists(db_path, table_name):
    """
    지정한 테이블에 country 컬럼이 존재하는지 확인하고,
    없으면 country TEXT 컬럼을 추가합니다.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 테이블의 컬럼 정보를 가져옴
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()  # 각 튜플: (cid, name, type, notnull, default_value, pk)
    column_names = [col[1] for col in columns]
    
    # country 컬럼이 없으면 추가
    if 'country' not in column_names:
        print("Country 컬럼이 존재하지 않습니다. 추가합니다.")
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN country TEXT;")
        conn.commit()
    conn.close()

def get_domain_list(db_path, table_name):
    """SQLite DB에서 domain 컬럼의 값을 리스트로 반환"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = f"SELECT domain FROM {table_name};"
    cursor.execute(query)
    rows = cursor.fetchall()
    domain_list = [row[0] for row in rows]
    conn.close()
    return domain_list

def get_country_for_domain(domain, api_key):
    """
    whoisxml API를 호출하여 domain의 country 값을 반환.
    whoisxml API의 응답 구조에 따라 키를 변경할 수 있음.
    """
    url = "https://www.whoisxmlapi.com/whoisserver/WhoisService"
    params = {
        "apiKey": api_key,
        "domainName": domain,
        "outputFormat": "JSON"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        whois_record = data.get("WhoisRecord")
        if not whois_record:
            return None
        registry_data = whois_record.get("registryData")
        if registry_data:
            registrant = registry_data.get("registrant")
            if registrant:
                return registrant.get("country")
        registrant = whois_record.get("registrant")
        if registrant:
            return registrant.get("country")
        return None
    else:
        print(f"Error fetching data for domain {domain}: {response.status_code}")
        return None

def update_country_in_db(db_path, table_name, domain, country):
    """특정 도메인에 대한 country 값을 데이터베이스에 업데이트"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = f"UPDATE {table_name} SET country = ? WHERE domain = ?;"
    cursor.execute(query, (country, domain))
    conn.commit()
    conn.close()

def main():
    db_path = 'my_ransomware_domains.db'  # 실제 DB 파일 경로로 변경
    table_name = 'domains'      # 실제 테이블 이름으로 변경
    api_key = 'at_k2hOe8U1K45FWWym6mFG0Y6PDiPfE'       # whoisxml API 키로 변경

    # country 컬럼이 존재하는지 확인 후, 없으면 추가
    ensure_country_column_exists(db_path, table_name)

    # SQLite에서 도메인 목록 가져오기
    domain_list = get_domain_list(db_path, table_name)

    for domain in domain_list:
        country = get_country_for_domain(domain, api_key)
        print(f"Domain: {domain}, Country: {country}")
        # 가져온 country 값을 DB에 업데이트
        update_country_in_db(db_path, table_name, domain, country)

if __name__ == "__main__":
    main()
