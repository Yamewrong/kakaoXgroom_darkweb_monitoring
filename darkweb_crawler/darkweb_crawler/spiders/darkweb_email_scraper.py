import scrapy
from darkweb_crawler.slack_bot import send_slack_message  # ✅ Slack API 모듈 가져오기
import re

class DarkWebSpider(scrapy.Spider):
    name = "darkweb_email_scraper"
    
    # ✅ 다크웹 크롤링 대상 사이트 목록
    start_urls = [
  ]

    custom_settings = {
    "DOWNLOADER_MIDDLEWARES": {
        "scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware": 1,
    },
    "HTTP_PROXY": "socks5h://127.0.0.1:9050"
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
        """Slack 웹훅을 이용하여 알림을 전송하는 함수"""
        max_emails = 5  # 최대 5개 이메일만 Slack 알림에 포함
        email_list = ", ".join(emails[:max_emails])
        extra_count = len(emails) - max_emails

        message = f"🚨 Darkweb Email Leak Detected! 🚨\n" \
                  f"🔗 URL: {url}\n" \
                  f"📧 Emails Found: {email_list}" 

        if extra_count > 0:
            message += f"\n📌 (and {extra_count} more...)"

        send_slack_message(message)