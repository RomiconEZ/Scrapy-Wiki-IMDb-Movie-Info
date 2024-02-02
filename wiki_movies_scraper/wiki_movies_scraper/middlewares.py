from scrapy import signals


class WikiMoviesScraperSpiderMiddleware:
    """
    Middleware for processing spider input and output.

    This middleware connects to the spider_opened signal and defines how responses and results are processed.
    """

    @classmethod
    def from_crawler(cls, crawler):
        """
        Initializes the middleware and connects it to the spider_opened signal.

        Args:
            crawler: The crawler instance.

        Returns:
            Instance of WikiMoviesScraperSpiderMiddleware.
        """
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        """
        Processes input for the spider.

        Args:
            response: The response being processed.
            spider: The spider processing the response.

        Returns:
            None, to continue processing other middlewares.
        """
        return None

    def process_spider_output(self, response, result, spider):
        """
        Processes the output from the spider.

        Args:
            response: The response associated with the output.
            result: The result from the spider.
            spider: The spider that produced the result.

        Yields:
            The items from the result.
        """
        for i in result:
            yield i

    def process_start_requests(self, start_requests, spider):
        """
        Processes the start requests of the spider.

        Args:
            start_requests: The initial requests of the spider.
            spider: The spider that issued the start requests.

        Yields:
            The start requests.
        """
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        """
        Handles the spider_opened signal.

        Args:
            spider: The spider that was opened.
        """
        spider.logger.info(f"Spider opened: {spider.name}")


class WikiMoviesScraperDownloaderMiddleware:
    """
    Middleware for processing requests and responses.

    This middleware connects to the spider_opened signal and modifies how requests and responses are handled.
    """

    @classmethod
    def from_crawler(cls, crawler):
        """
        Initializes the middleware and connects it to the spider_opened signal.

        Args:
            crawler: The crawler instance.

        Returns:
            Instance of WikiMoviesScraperDownloaderMiddleware.
        """
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        """
        Processes each request sent by the spider.

        Args:
            request: The request being processed.
            spider: The spider sending the request.

        Returns:
            None, to continue processing other middlewares.
        """
        spider.logger.debug(f"Request sent: {request.url}")
        return None

    def process_response(self, request, response, spider):
        """
        Processes the response received by the spider.

        Args:
            request: The request that resulted in the response.
            response: The response being processed.
            spider: The spider that received the response.

        Returns:
            The response, to continue processing other middlewares.
        """
        spider.logger.debug(f"Response received: {response.url}")
        return response

    def spider_opened(self, spider):
        """
        Handles the spider_opened signal.

        Args:
            spider: The spider that was opened.
        """
        spider.logger.info(f"Spider opened: {spider.name}")
