import requests

# 다크웹 URL
url = "http://ransomxifxwc5eteopdobynonjctkxxvap77yqifu2emfbecgbqdw6qd.onion/"

# Tor 프록시 설정
proxies = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050",
}

# 하드코딩된 쿠키
cookies = {
    "_token": "2842856222",
    "_uuid": "b7c87b00-4df6-43d9-8b4e-4aa66e67f352"
}

# 추가적인 보안 우회를 위한 헤더
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Referer": url
}

# 세션 생성 및 요청
session = requests.Session()
session.cookies.update(cookies)

try:
    response = session.get(url, headers=headers, proxies=proxies, timeout=30)
    response.raise_for_status()
    print("✅ 인증 성공! 페이지 로드됨.")
    print(response.text[:500])  # 응답 내용 일부 출력
except requests.exceptions.HTTPError as e:
    print(f"❌ 인증 실패 (HTTPError): {e}")
except requests.exceptions.RequestException as e:
    print(f"❌ 요청 실패 (RequestException): {e}")
