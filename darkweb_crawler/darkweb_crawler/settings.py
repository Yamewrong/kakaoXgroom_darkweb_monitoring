# Scrapy settings for darkweb_crawler project

BOT_NAME = "darkweb_crawler"
SPIDER_MODULES = ["darkweb_crawler.spiders"]
NEWSPIDER_MODULE = "darkweb_crawler.spiders"

# 🚀 SOCKS5 프록시 직접 적용 (scrapy-socks2 없이)
HTTPPROXY_ENABLED = True
PROXY_URL = "socks5h://127.0.0.1:9050"

# 📌 Scrapy에서 프록시 적용 방법
PROXY_URL = "socks5h://127.0.0.1:9050"

# ✅ 기본 다운로드 핸들러
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 750,
}
# 🚀 프록시 직접 환경 변수에 설정
import os
os.environ["http_proxy"] = "socks5h://127.0.0.1:9050"
os.environ["https_proxy"] = "socks5h://127.0.0.1:9050"

# ✅ HTTP Proxy 활성화
HTTPPROXY_ENABLED = True
REQUESTS_PROXY = PROXY_URL

# ✅ Tor 네트워크 설정
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
DOWNLOAD_DELAY = 3
RETRY_ENABLED = True
RETRY_TIMES = 15  # 📌 Tor 네트워크에서 불안정한 연결 대비
RETRY_HTTP_CODES = [500, 502, 503, 504, 403, 408]
DOWNLOAD_TIMEOUT = 180
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
ROBOTSTXT_OBEY = False

# ✅ Tor 네트워크를 사용할 경우 User-Agent를 추가로 지정
DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

# ✅ 동시 요청 수 조정 (Tor 부하 방지)
CONCURRENT_REQUESTS = 8
CONCURRENT_REQUESTS_PER_DOMAIN = 4
CONCURRENT_REQUESTS_PER_IP = 4

# ✅ 캐시 사용 안 함 (최신 데이터 수집 목적)
HTTPCACHE_ENABLED = False

# ✅ 데이터 저장 인코딩 설정
FEED_EXPORT_ENCODING = "utf-8"
