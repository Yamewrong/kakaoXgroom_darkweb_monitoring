# 🔍 Dark Web Ransomware Monitoring System

![header](https://capsule-render.vercel.app/api?type=waving&color=gradient&height=200&section=header&text=Dark%20Web%20Monitoring&fontSize=40&fontAlignY=40)

## 📌 Project Overview

This project is designed for **automated ransomware victim domain monitoring** using **dark web intelligence**. It utilizes **Scrapy for web crawling, Selenium for bypassing obstacles, and Flask for visualization**, integrating **Tor network access** to extract data from hidden `.onion` sites.

This project was developed as part of the **KakaoXGoorm Information Security Master Program**.

---

## 🛠 Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Scrapy](https://img.shields.io/badge/Scrapy-448aff?style=for-the-badge&logo=python&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white)
![Tor](https://img.shields.io/badge/Tor-7D4698?style=for-the-badge&logo=torproject&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

---

## 🚀 Features

### 🕵️ **Dark Web Crawling & Threat Monitoring**
- **Scrapy framework** used for crawling `.onion` websites
- **Selenium automation** to bypass login & CAPTCHA verification
- **Tor proxy integration** for accessing dark web content

### 🔔 **Automated Alert System**
- **Slack API integration** for real-time notifications
- **Database logging** to track monitored domains

### 🌐 **Web-Based Threat Analysis Dashboard**
- **Flask-based UI** for security visualization
- **Interactive country-based visualization** of threat data

---

## 📜 Project Structure

```bash
📂 darkweb_crawler
│── 📜 README.md   # Project Documentation
│── 📂 darkweb_crawler  # Main crawler directory
│   │── 📂 data
│   │   ├── leaked_credit_cards.json  # Extracted leaked data
│   │── 📂 spiders
│   │   ├── static/
│   │   │   ├── 도룡농.jpg  # Static assets (example)
│   │   ├── templates/  # HTML templates for Flask UI
│   │   │   ├── country_visualization.html
│   │   │   ├── index.html
│   │   │   ├── visualization.html
│   │── app.py    # Web application backend
│   │── config.json   # Configuration file
│   │── fetch_cookies.py  # Authentication handling
│   │── known_domains.json  # Detected domains storage
│   │── ransom_monitor1.py  # Tor-based crawler
│   │── ransom_monitor2.py  # Selenium-based monitor
│   │── ransom_monitor3.py  # Recursive domain scanning
│   │── victim.db  # SQLite database storage
│   │── middlewares.py  # Scrapy middlewares
│   │── settings.py  # Scrapy settings
│   │── scrapy.cfg  # Scrapy project config
```

---

## ⚙️ How to Run

### 1️⃣ **Set Up Virtual Environment & Install Dependencies**
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2️⃣ **Start Dark Web Crawling**
```bash
python darkweb_crawler/ransom_monitor1.py
python darkweb_crawler/ransom_monitor2.py
python darkweb_crawler/ransom_monitor3.py
```

### 3️⃣ **Run Flask Web Dashboard**
```bash
python darkweb_crawler/app.py
```

---

## 📬 Contact & Links

🔗 **GitHub:** [github.com/Yamewrong](https://github.com/Yamewrong)  
🔗 **Tistory Blog:** [yamewrong.tistory.com](https://yamewrong.tistory.com)  
📧 **Email:** [your_email@example.com](mailto:your_email@example.com)  

---

🚀 *Enhancing cybersecurity with automated dark web intelligence!*
