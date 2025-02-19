import json

# JSON 파일 불러오기
with open("onion_links.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# URL만 추출하여 리스트 생성
onion_urls = [entry["onion_link"].split("redirect_url=")[-1] for entry in data]

# 파일로 저장
with open("onion_urls.txt", "w", encoding="utf-8") as f:
    for url in onion_urls:
        f.write('"'+url+'"' + "\n")

print("추출된 .onion URL이 onion_urls.txt 파일에 저장되었습니다.")