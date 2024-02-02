import csv
from scrapy.exceptions import DropItem


class SaveMoviesPipeline:
    """
    Pipeline for saving scraped movie data into a CSV file.

    This pipeline opens a CSV file at the start of the spider and writes the scraped data.
    It closes the file when the spider is finished.
    """

    def __init__(self):
        self.file = None
        self.writer = None

    def open_spider(self, spider):
        """
        Opens a CSV file at the start of the spider.

        Args:
            spider: The spider that is being opened.
        """
        self.file = open("movies.csv", "w", newline="", encoding="utf-8")
        self.writer = csv.writer(self.file)
        self.writer.writerow(
            ["Title", "Genre", "Director", "Country", "Year", "Rating"]
        )
        spider.logger.info("Pipeline: CSV file opened.")

    def close_spider(self, spider):
        """
        Closes the CSV file at the end of the spider.

        Args:
            spider: The spider that is being closed.
        """
        self.file.close()
        spider.logger.info("Pipeline: CSV file closed.")

    def process_item(self, item, spider):
        """
        Processes each item passed by the spider.

        Writes the item to the CSV file if the title is not None. If the title is None,
        the item is logged and dropped.

        Args:
            item: The item scraped by the spider.
            spider: The spider that scraped the item.

        Returns:
            The item if saved successfully, otherwise raises DropItem exception.
        """
        if item.get("title"):
            # Writing the item to CSV
            self.writer.writerow(
                [
                    item.get("title", ""),
                    item.get("genre", ""),
                    item.get("director", ""),
                    item.get("country", ""),
                    item.get("year", ""),
                    item.get("rating", ""),
                ]
            )
            # Uncomment the line below to log every item saved
            # spider.logger.info(f"Pipeline: Item saved to CSV - {item['title']}")
            return item
        else:
            # Logging and dropping the item if the title is missing
            spider.logger.warning("Pipeline: Item dropped, missing title.")
            raise DropItem("Missing title in item")
