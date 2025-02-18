import scrapy

class OnionSpider(scrapy.Spider):
    name = "onion_crawler"
    allowed_domains = ["ahmia.fi"]
    start_urls = ["https://ahmia.fi/search/?q=email+leak"]  # 이메일 유출 검색

    custom_settings = {
        "ROBOTSTXT_OBEY": False,  # robots.txt 무시
        "DOWNLOAD_DELAY": 2,  # 차단 방지 딜레이
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    def parse(self, response):
        onion_links = response.css("a::attr(href)").getall()
        for link in onion_links:
            if ".onion" in link:
                yield {"onion_link": link}
