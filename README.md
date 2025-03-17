# 🔍 다크웹 랜섬웨어 모니터링 시스템

![header](https://capsule-render.vercel.app/api?type=waving&color=gradient&height=200&section=header&text=Dark%20Web%20Monitoring&fontSize=40&fontAlignY=40)

## 📌 프로젝트 개요

이 프로젝트는 **다크웹 기반의 랜섬웨어 피해 도메인 모니터링 시스템**으로, **자동화된 크롤링 및 실시간 보안 알림 기능**을 제공합니다. Scrapy를 이용한 **웹 크롤링**, Selenium을 활용한 **우회 탐색**, Flask 기반 **웹 대시보드**가 포함되며, **Tor 네트워크를 활용하여 `.onion` 사이트에서 데이터를 수집**합니다.

이 프로젝트는 **KakaoXGoorm 정보보호 마스터 과정**의 일환으로 개발되었습니다.

---

## 🛠 기술 스택

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Scrapy](https://img.shields.io/badge/Scrapy-448aff?style=for-the-badge&logo=python&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white)
![Tor](https://img.shields.io/badge/Tor-7D4698?style=for-the-badge&logo=torproject&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

---

## 🚀 주요 기능

### 🕵️ **다크웹 크롤링 및 위협 모니터링**
- Scrapy 프레임워크를 활용한 `.onion` 웹사이트 크롤링
- Selenium을 이용한 로그인 및 CAPTCHA 우회 자동화
- Tor 프록시를 통한 다크웹 데이터 수집

### 🔔 **실시간 보안 경고 시스템**
- Slack API를 이용한 즉각적인 알림 전송
- 데이터베이스에 자동 저장하여 분석 가능

### 🌐 **웹 기반 보안 위협 분석 대시보드**
- Flask 기반 UI 제공 (검색 및 데이터 시각화)
- 랜섬웨어 피해 도메인 국가별 분포 시각화 지원

---

## 📜 프로젝트 구조

```bash
📂 darkweb_crawler
│── 📜 README.md   # 프로젝트 문서
│── 📜 requirements.txt  
│── 📂 darkweb_crawler  # 크롤러 디렉토리
│   │── 📂 data
│   │   ├── leaked_credit_cards.json  # 수집된 유출 데이터
│   │── 📂 spiders
│   │   ├── static/
│   │   │   ├── 도룡농.jpg  # 정적 파일 예시
│   │   ├── templates/  # Flask UI 템플릿
│   │   │   ├── country_visualization.html
│   │   │   ├── index.html
│   │   │   ├── visualization.html
│   │── app.py    # 웹 애플리케이션 백엔드
│   │── config.json   # 설정 파일
│   │── fetch_cookies.py  # 인증 처리
│   │── known_domains.json  # 감지된 도메인 목록 저장
│   │── ransom_monitor1.py  # Tor 기반 크롤러
│   │── ransom_monitor2.py  # Selenium 기반 크롤링
│   │── ransom_monitor3.py  # 재귀적 도메인 스캔
│   │── victim.db  # SQLite 데이터베이스
│   │── middlewares.py  # Scrapy 미들웨어
│   │── settings.py  # Scrapy 설정 파일
│   │── scrapy.cfg  # Scrapy 프로젝트 설정
```

---

## ⚙️ 실행 방법

### 1️⃣ **가상환경 설정 및 필수 패키지 설치**
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2️⃣ **다크웹 크롤링 시작**
```bash
python darkweb_crawler/ransom_monitor1.py
python darkweb_crawler/ransom_monitor2.py
python darkweb_crawler/ransom_monitor3.py
```

### 3️⃣ **Flask 기반 웹 대시보드 실행**
```bash
python darkweb_crawler/app.py
```

---

## 📬 문의 및 참고 자료

🔗 **GitHub:** [github.com/Yamewrong](https://github.com/Yamewrong)  
🔗 **기술 블로그:** [yamewrong.tistory.com](https://yamewrong.tistory.com)  
📧 **이메일:** [yameiswrong@gmail.com](mailto:your_yameiswrong@gmail.com)  

---

🚀 *자동화된 다크웹 인텔리전스로 사이버 보안을 강화합니다!*
