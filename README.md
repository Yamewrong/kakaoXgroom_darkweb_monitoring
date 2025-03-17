# 🔍 KakaoXGoorm Semi Project

![header](https://capsule-render.vercel.app/api?type=waving&color=gradient&height=200&section=header&text=Cybersecurity%20Project&fontSize=40&fontAlignY=40)

## 📌 Project Overview

**KakaoXGoorm 정보보호 마스터 과정**에서 수행한 **다크웹 모니터링 및 랜섬웨어 피해 도메인 탐지 시스템** 프로젝트입니다. 다크웹에서 랜섬웨어 공격 그룹이 공개한 피해 기업 도메인을 **자동으로 수집하고 분석하여 보안 관계자에게 실시간 알림을 제공**하는 시스템을 구축하였습니다.

---

## 🛠 Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Tor](https://img.shields.io/badge/Tor-7D4698?style=for-the-badge&logo=torproject&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white)
![Slack API](https://img.shields.io/badge/Slack-4A154B?style=for-the-badge&logo=slack&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

---

## 🚀 Features

### 🛠 **Dark Web Monitoring & Automated Crawling**
- **Tor 네트워크**를 활용한 다크웹 크롤링
- **Selenium 기반 웹 자동화**를 통한 데이터 수집
- **랜섬웨어 피해 기업 도메인 실시간 탐지**

### 🔔 **Real-Time Notification System**
- **Slack API를 활용한 실시간 보안 알림** 전송
- 새로운 피해 도메인 발견 시 보안 담당자에게 즉각적인 경고 제공

### 🌐 **Web-Based Analysis Dashboard**
- **Flask 기반의 UI**로 크롤링된 데이터를 검색 및 시각화
- **SQLite 데이터베이스**를 활용한 보안 위협 관리

---

## 📜 Project Structure

```bash
📂 kakaoXgroom_semi_project
│── 📜 README.md   # 프로젝트 소개
│── 📂 src        # 크롤링 및 데이터 분석 코드
│── 📂 docs       # 프로젝트 문서 및 보고서
│── 📂 webapp     # Flask 기반 웹 대시보드
│── 📂 database   # SQLite 데이터 저장
```

---

## 📌 How to Run

### 1️⃣ **환경 설정**
```bash
# 가상환경 생성 및 패키지 설치
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2️⃣ **크롤링 실행**
```bash
python src/crawler.py
```

### 3️⃣ **웹 대시보드 실행**
```bash
python webapp/app.py
```

---

## 📬 Contact & Links

🔗 **GitHub:** [github.com/Yamewrong](https://github.com/Yamewrong)  
🔗 **Tistory Blog:** [yamewrong.tistory.com](https://yamewrong.tistory.com)  
📧 **Email:** [your_email@example.com](mailto:your_email@example.com)  

---

🚀 *Enhancing cybersecurity with automated dark web intelligence!*
