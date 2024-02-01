from scrapy import signals


class WikiMoviesScraperSpiderMiddleware:
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

    def process_start_requests(self, start_requests, spider):
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class WikiMoviesScraperDownloaderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        spider.logger.debug(f"Запрос отправлен: {request.url}")
        return None

    def process_response(self, request, response, spider):
        spider.logger.debug(f"Получен ответ: {response.url}")
        return response

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
