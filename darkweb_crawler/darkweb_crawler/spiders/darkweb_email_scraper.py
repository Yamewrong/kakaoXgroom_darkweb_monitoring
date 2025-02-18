import scrapy
from darkweb_crawler.slack_bot import send_slack_message  # ✅ Slack API 모듈 가져오기
import re

class DarkWebSpider(scrapy.Spider):
    name = "darkweb_email_scraper"
    
    # ✅ 다크웹 크롤링 대상 사이트 목록
    start_urls = [
"http://tzoz3be4x4vd7ydkruxl2hczax3m5yv5up4frq4y2awnel7pyj6nxbid.onion/contribute/design/MAC_address/"
"https://ainita2ucg473h7tjp3j32fu6wabxtrk2lrz6hauystamloiap3a4did.onion/signing-up-for-chapar-receiving-email-via-sms"
"http://hellhoh5o35sylxrpfu45p5r74n2lzvirnvszmziuvn7bcejlynaqxyd.onion/threads/cock-li-under-red-alert-a-privacy-based-email.12424/"
    ]

    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware": 1,
        },
        "PROXY": "socks5h://127.0.0.1:9050"
    }
    def parse(self, response):
        # 이메일 패턴 정규식
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

        # 페이지에서 이메일 찾기
        emails = re.findall(email_pattern, response.text)

        if emails:
            # Slack으로 알림 전송
            self.send_slack_alert(response.url, emails)

        yield {
            "url": response.url,
            "emails": emails
        }

    def send_slack_alert(self, url, emails):
        """이메일이 감지되면 Slack 웹훅을 이용하여 메시지를 전송하는 함수"""
        message = f"🚨 Darkweb Email Leak Detected! 🚨\n" \
                    f"🔗 URL: {url}\n" \
                    f"📧 Emails Found: {', '.join(emails)}"

        send_slack_message(message)  # ✅ Slack 알림 전송