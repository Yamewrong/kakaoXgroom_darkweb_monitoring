from flask import Flask, render_template, request, jsonify
import sqlite3
from collections import Counter
from tldextract import extract

app = Flask(__name__)
DB_FILE = "ransomware_domains.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def get_domain_tld(domain):
    extracted = extract(domain)
    return extracted.suffix if extracted.suffix else "Unknown"

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/visualization')
def visualization():
    return render_template("visualization.html")  # visualization.html 서빙

@app.route('/api/domains', methods=['GET'])
def get_domains():
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 20))
    offset = (page - 1) * limit
    search_query = request.args.get("search", "").strip()
    date_filter = request.args.get("date", "").strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    # 기본 쿼리
    query = "SELECT domain, upload_time FROM domains WHERE 1=1"
    params = []

    # 도메인 검색 추가
    if search_query:
        query += " AND domain LIKE ?"
        params.append(f"%{search_query}%")

    # 날짜 필터 추가
    if date_filter:
        query += " AND DATE(upload_time) >= ?"
        params.append(date_filter)

    # 전체 데이터 개수 가져오기
    count_query = "SELECT COUNT(*) FROM (" + query + ")"
    cursor.execute(count_query, params)
    total_rows = cursor.fetchone()[0]
    total_pages = (total_rows // limit) + (1 if total_rows % limit > 0 else 0)

    # 데이터 가져오기 (페이지네이션 적용)
    query += " ORDER BY upload_time DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()

    # 응답을 JSON 형식으로 변환
    data = [dict(row) for row in results]

    return jsonify({"domains": data, "total_pages": total_pages})

@app.route('/api/tld_stats', methods=['GET'])
def get_tld_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT domain FROM domains")  # 모든 도메인 조회
    results = cursor.fetchall()
    conn.close()
    
    tld_list = [get_domain_tld(row["domain"]) for row in results]
    tld_counts = dict(Counter(tld_list))
    
    return jsonify(tld_counts)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
