import scrapy

class OnionSpider(scrapy.Spider):
    name = "onion_crawler"
    allowed_domains = ["ahmia.fi"]
    start_urls = ["https://ahmia.fi/search/?q=credit+card+leak"]

    def parse(self, response):
        for link in response.css("a::attr(href)").getall():
            if ".onion" in link:
                yield {"onion_link": link}
