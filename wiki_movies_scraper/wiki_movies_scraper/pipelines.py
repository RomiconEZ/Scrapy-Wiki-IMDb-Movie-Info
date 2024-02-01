import csv
from scrapy.exceptions import DropItem
from scrapy import signals


class SaveMoviesPipeline:
    def open_spider(self, spider):
        self.file = open('movies.csv', 'w', newline='', encoding='utf-8')
        self.writer = csv.writer(self.file)
        self.writer.writerow(['Title', 'Genre', 'Director', 'Country', 'Year'])
        spider.logger.info("Pipeline: CSV файл открыт.")

    def close_spider(self, spider):
        self.file.close()
        spider.logger.info("Pipeline: CSV файл закрыт.")

    def process_item(self, item, spider):
        if item['title'] is not None:  # Убедимся, что у фильма есть название и режиссер
            self.writer.writerow([item['title'], item['genre'], item['director'], item['country'], item['year']])
            spider.logger.info(f"Pipeline: Элемент сохранен в CSV - {item['title']}")
            return item
        else:
            spider.logger.warning(f"Pipeline: Пропущен элемент, отсутствует название - {item}")
            raise DropItem(f"Missing title in {item}")
