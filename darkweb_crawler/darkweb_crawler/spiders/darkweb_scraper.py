import scrapy
import json

class DarkWebSpider(scrapy.Spider):
    name = "darkweb_scraper"

    def start_requests(self):
        # 🔹 JSON 파일에서 URL 불러오기
        with open("onion_links.json", "r", encoding="utf-8") as f:
            onion_links = json.load(f)

        # 🔹 크롤링할 URL 리스트 생성
        for entry in onion_links:
            yield scrapy.Request(url=entry["onion_link"], callback=self.parse)

    def parse(self, response):
        yield {
            "url": response.url,
            "title": response.css("title::text").get(),
            "body_text": response.css("body").get()
        }
