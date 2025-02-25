import requests
from stem.control import Controller

# Tor 프록시 설정 (SOCKS5)
proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050',
}

# 크롤링할 다크웹 URL (실제 .onion URL로 변경 필요)
url = "ransomxifxwc5eteopdobynonjctkxxvap77yqifu2emfbecgbqdw6qd.onion"

# Tor 세션 시작
def get_tor_session():
    session = requests.Session()
    session.proxies = proxies
    return session

# Tor 컨트롤러로 새로운 아이덴티티 요청
def renew_tor_ip():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password='YOUR_TOR_PASSWORD')  # Tor 설정에서 지정한 비밀번호
        controller.signal('NEWNYM')

# Tor 세션을 사용하여 요청 보내기
session = get_tor_session()
response = session.get(url)

# 응답 출력
if response.status_code == 200:
    print("접속 성공!")
    print(response.text)  # HTML 내용 출력
else:
    print("접속 실패:", response.status_code)
