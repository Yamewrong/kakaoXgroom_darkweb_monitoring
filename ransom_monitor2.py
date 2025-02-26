#country 비율 시각화

import sqlite3
import matplotlib.pyplot as plt
from collections import Counter

def get_country_data(db_path, table_name):
    """DB에서 country 컬럼의 데이터를 가져와 리스트로 반환"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = f"SELECT country FROM {table_name};"
    cursor.execute(query)
    rows = cursor.fetchall()
    # None 값은 제외하고 country 값만 추출
    countries = [row[0] for row in rows if row[0] is not None]
    conn.close()
    return countries

def plot_country_distribution(countries):
    """국가별 빈도수를 계산하여 백분율로 변환 후 막대그래프로 시각화"""
    total = len(countries)
    # 국가별 개수를 계산 (예: {'USA': 10, 'KOR': 5, ...})
    counts = Counter(countries)
    
    # 각 국가의 빈도수를 백분율로 변환
    percentages = {country: (count / total) * 100 for country, count in counts.items()}
    
    # 백분율 내림차순 정렬
    sorted_data = sorted(percentages.items(), key=lambda x: x[1], reverse=True)
    labels, values = zip(*sorted_data)
    
    plt.figure(figsize=(10, 6))
    plt.bar(labels, values, color='skyblue')
    plt.xlabel("Country")
    plt.ylabel("Percentage (%)")
    plt.title("Country Distribution")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

def main():
    #db_path = 'my_ransomware_domains.db'  # 실제 DB 파일 경로로 변경
    db_path = 'cj_ransomware_domains.db'  # 실제 DB 파일 경로로 변경
    table_name = 'domains'      # 실제 테이블 이름으로 변경
    
    # DB에서 country 데이터를 가져옴
    countries = get_country_data(db_path, table_name)
    if countries:
        plot_country_distribution(countries)
    else:
        print("DB에서 country 데이터를 찾을 수 없습니다.")

if __name__ == "__main__":
    main()
