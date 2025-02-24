from scrapy import signals
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware
from scrapy.exceptions import IgnoreRequest

class TorProxyMiddleware(HttpProxyMiddleware):
    """
    🛠️ Tor Proxy를 사용하여 .onion 사이트에 접속하는 Scrapy 미들웨어
    """

    def process_request(self, request, spider):
        if ".onion" in request.url:
            spider.logger.info(f"🔄 Tor Proxy를 통해 요청 중: {request.url}")
            request.meta["proxy"] = "socks5h://127.0.0.1:9050"

    def process_exception(self, request, exception, spider):
        """
        🛠️ Tor 네트워크 요청 실패 시 재시도
        """
        spider.logger.error(f"🚨 Tor Proxy 요청 실패: {request.url} | 예외: {exception}")
        return None  # Scrapy가 자동으로 재시도

class DarkwebCrawlerSpiderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        return None

    def process_spider_output(self, response, result, spider):
        for i in result:
            yield i

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class DarkwebCrawlerDownloaderMiddleware:
    """
    🛠️ Scrapy 기본 Downloader 미들웨어
    """

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        return None

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        return None

    def spider_opened(self, spider):
        spider.logger.info("🔄 Spider Downloader Middleware 시작됨: %s" % spider.name)
