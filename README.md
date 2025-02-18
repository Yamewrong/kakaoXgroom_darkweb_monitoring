🛠 Scrapy 크롤러 실행
1️⃣ Scrapy 크롤러 실행

sh
복사
편집
scrapy crawl onion_spider -o onion_data.json
👉 .onion 사이트 크롤링 후 결과를 onion_data.json에 저장

2️⃣ Scrapy 크롤러 실행 (디버깅 모드)

sh
복사
편집
scrapy crawl onion_spider --loglevel=DEBUG
👉 크롤링 과정에서 발생하는 문제를 디버깅하기 위해 로그를 상세하게 출력

📂 JSON 데이터 가공 및 저장
3️⃣ .onion URL만 추출하는 Python 스크립트 실행

sh
복사
편집
python extract_onion_links.py
👉 onion_links.json에서 .onion URL만 추출하여 onion_urls.txt로 저장

4️⃣ extract_onion_links.py 내용 예시:

python
복사
편집
import json

# JSON 파일 불러오기
with open("onion_links.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# URL만 추출하여 리스트 생성
onion_urls = [entry["onion_link"].split("redirect_url=")[-1] for entry in data]

# 파일로 저장
with open("onion_urls.txt", "w", encoding="utf-8") as f:
    for url in onion_urls:
        f.write(url + "\n")

print("추출된 .onion URL이 onion_urls.txt 파일에 저장되었습니다.")
💾 CSV 파일을 JSON으로 변환
5️⃣ csv_to_json.py 실행 (CSV → JSON 변환)

sh
복사
편집
python csv_to_json.py
👉 크롤링한 .onion 데이터를 CSV에서 JSON으로 변환

6️⃣ csv_to_json.py 내용 예시:

python
복사
편집
import csv
import json

# CSV 파일을 JSON 파일로 변환
csv_file = "onion_data.csv"
json_file = "onion_data.json"

# 데이터 변환
with open(csv_file, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    data = [row for row in reader]

# JSON 저장
with open(json_file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4)

print(f"{json_file} 파일이 생성되었습니다.")
🕵 Scrapy 로그 확인 및 재시도 설정
7️⃣ Scrapy 크롤러 재시도 가능하도록 설정 후 실행

sh
복사
편집
scrapy crawl onion_spider -s RETRY_ENABLED=True -s RETRY_TIMES=5 -s DOWNLOAD_DELAY=2
👉 .onion 사이트에서 요청이 실패할 경우 최대 5번까지 재시도하며, 요청 간 2초 지연

🎯 전체 자동 실행 스크립트
8️⃣ 모든 작업을 한 번에 실행하는 run_all.sh (리눅스/macOS)

sh
복사
편집
#!/bin/bash

echo "Scrapy 크롤러 실행 중..."
scrapy crawl onion_spider -o onion_data.json

echo "JSON 데이터에서 .onion URL 추출 중..."
python extract_onion_links.py

echo "CSV 파일을 JSON으로 변환 중..."
python csv_to_json.py

echo "모든 작업 완료!"
👉 실행 방법:

sh
복사
편집
chmod +x run_all.sh  # 실행 권한 부여
./run_all.sh         # 실행
