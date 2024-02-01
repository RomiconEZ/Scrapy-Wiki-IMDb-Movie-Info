import re

import scrapy
from scrapy.http import Response
from urllib.parse import unquote
from ..items import WikiMoviesScraperItem


def clean_list(_list):
    # Фильтрация списка, оставляя только элементы, содержащие буквы
    cleaned_list = [country for country in _list if re.search(r'[a-zA-Zа-яА-Я]', country)]
    # Удаление пробелов и переносов строк в начале и конце каждого элемента
    cleaned_list = [country.strip() for country in cleaned_list]
    return cleaned_list
def extract_country_from_flag_title(flag_title):
    # Использование регулярного выражения для извлечения названия страны из строки
    match = re.search(r"Флаг\s(.+)", flag_title)
    if match:
        # Возвращаем название страны в виде списка с одним элементом
        return [match.group(1)]
    return []

class MoviesSpider(scrapy.Spider):
    name = 'movies_spider'
    allowed_domains = ['ru.wikipedia.org']
    start_urls = ['https://ru.wikipedia.org/wiki/Категория:Фильмы_по_годам']

    def parse(self, response: Response, **kwargs):
        self.logger.info(f'Посещение страницы: {unquote(response.url.split("/")[-1])}')
        # Перебор всех ссылок на категории фильмов по годам
        for href in response.xpath(
                '//*[@id="mw-subcategories"]/div/div/div[3]/ul/li/div/div['
                '@class="CategoryTreeItem"]/a/@href'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_year_page)

    def parse_year_page(self, response: Response, **kwargs):
        year = unquote(response.url.split("/")[-1]).split('_')[-2]
        self.logger.info(f'Посещение страницы: {unquote(response.url.split("/")[-1])}')

        # Перебор всех ссылок на отдельные фильмы
        for href in response.xpath('//*[@id="mw-pages"]//div[contains(@class, "mw-category-group")]//ul/li/a/@href'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_movie_details, cb_kwargs={'year': year})

    def parse_movie_details(self, response: Response, **kwargs):
        self.logger.info(f'Посещение страницы фильма: {unquote(response.url.split("/")[-1])}')
        item = WikiMoviesScraperItem()

        # XPath для извлечения данных
        base_xpath = '//*[@id="mw-content-text"]/div[1]/table[1]'
        title_xpath = f'{base_xpath}//th[@class="infobox-above"]//text()'
        genre_xpath = f'''
            {base_xpath}//th[contains(., "Жанр") or contains(., "Жанры")]/following-sibling::td//span[@data-wikidata-property-id="P136"]//text() |
            {base_xpath}//th[contains(., "Жанр") or contains(., "Жанры")]/following-sibling::td//a/text() |
            {base_xpath}//th[contains(., "Жанр") or contains(., "Жанры")]/following-sibling::td/text()
        '''.strip()

        director_xpath = f'''{base_xpath}//th[contains(text(), "Режиссёр") or contains(text(), "Режиссёры")]/following-sibling::td//text()'''
        country_xpath = f'''
            {base_xpath}//th[contains(text(), "Страна") or contains(text(), "Страны")]/following-sibling::td//a/text() |
            {base_xpath}//th[contains(text(), "Страна") or contains(text(), "Страны")]/following-sibling::td//span[@data-sort-value]/@data-sort-value |
            {base_xpath}//th[contains(text(), "Страна") or contains(text(), "Страны")]/following-sibling::td//span[contains(@class, "no-wikidata")]/text() |
            {base_xpath}//th[contains(text(), "Страна") or contains(text(), "Страны")]/following-sibling::td/text()
        '''.strip()
        flag_title_xpath = f"{base_xpath}//th[contains(text(), 'Страна') or contains(text(), 'Страны')]/following-sibling::td//img/@title"
        imdb_site_link_xpath = f'''{base_xpath}//th[contains(text(), "IMDb")]/following-sibling::td//a[contains(@href, "imdb.com")]/@href'''

        try:
            item['title'] = response.xpath(title_xpath).get() or None
        except Exception as e:
            item['title'] = None
            self.logger.error(f'Ошибка при извлечении названия: {e}')

        try:
            genres_list = response.xpath(genre_xpath).getall()
            genres_cleaned = clean_list(genres_list)
            genres_cleaned = [genre for genre in genres_cleaned if genre not in ['[d]', 'и']]
            item['genre'] = genres_cleaned or None
        except Exception as e:
            item['genre'] = None
            self.logger.error(f'Ошибка при извлечении жанра: {e}')

        try:
            directors_list = response.xpath(director_xpath).getall()
            directors_cleaned = clean_list(directors_list)
            item['director'] = directors_cleaned or None
        except Exception as e:
            item['director'] = None
            self.logger.error(f'Ошибка при извлечении режиссёра: {e}')

        try:
            country_data = response.xpath(country_xpath).getall()
            country = clean_list(country_data)
            if not country:
                flag_title = response.xpath(flag_title_xpath).get()
                if flag_title:
                    country_list = extract_country_from_flag_title(flag_title)
                    print(country_list)
                else:
                    country = None
            item['country'] = country
        except Exception as e:
            item['country'] = None
            self.logger.error(f'Ошибка при извлечении страны: {e}')

        try:
            year = kwargs.get('year')
            item['year'] = year if year else None
        except Exception as e:
            item['year'] = None
            self.logger.error(f'Ошибка при извлечении года: {e}')

        yield item


    def parse_imdb_movie_ratings(self, response: Response, **kwargs):
        self.logger.info(f'Посещение страницы фильма: {unquote(response.url.split("/")[-1])}')

        # XPath для извлечения данных
        base_xpath = '//*[@id="mw-content-text"]/div[1]/table[1]'
        title_xpath = f'{base_xpath}//th[@class="infobox-above"]//text()'
        genre_xpath = f'''
            {base_xpath}//th[contains(., "Жанр") or contains(., "Жанры")]/following-sibling::td//span[@data-wikidata-property-id="P136"]//text() |
            {base_xpath}//th[contains(., "Жанр") or contains(., "Жанры")]/following-sibling::td//a/text() |
            {base_xpath}//th[contains(., "Жанр") or contains(., "Жанры")]/following-sibling::td/text()
        '''.strip()

        director_xpath = f'''{base_xpath}//th[contains(text(), "Режиссёр") or contains(text(), "Режиссёры")]/following-sibling::td//text()'''
        country_xpath = f'''
            {base_xpath}//th[contains(text(), "Страна") or contains(text(), "Страны")]/following-sibling::td//a/text() |
            {base_xpath}//th[contains(text(), "Страна") or contains(text(), "Страны")]/following-sibling::td//span[@data-sort-value]/@data-sort-value |
            {base_xpath}//th[contains(text(), "Страна") or contains(text(), "Страны")]/following-sibling::td//span[contains(@class, "no-wikidata")]/text() |
            {base_xpath}//th[contains(text(), "Страна") or contains(text(), "Страны")]/following-sibling::td/text()
        '''.strip()
        flag_title_xpath = f"{base_xpath}//th[contains(text(), 'Страна') or contains(text(), 'Страны')]/following-sibling::td//img/@title"

        try:
            item['title'] = response.xpath(title_xpath).get() or None
        except Exception as e:
            item['title'] = None
            self.logger.error(f'Ошибка при извлечении названия: {e}')

        try:
            genres_list = response.xpath(genre_xpath).getall()
            genres_cleaned = clean_list(genres_list)
            genres_cleaned = [genre for genre in genres_cleaned if genre not in ['[d]', 'и']]
            item['genre'] = genres_cleaned or None
        except Exception as e:
            item['genre'] = None
            self.logger.error(f'Ошибка при извлечении жанра: {e}')

        try:
            directors_list = response.xpath(director_xpath).getall()
            directors_cleaned = clean_list(directors_list)
            item['director'] = directors_cleaned or None
        except Exception as e:
            item['director'] = None
            self.logger.error(f'Ошибка при извлечении режиссёра: {e}')

        try:
            country_data = response.xpath(country_xpath).getall()
            country = clean_list(country_data)
            if not country:
                flag_title = response.xpath(flag_title_xpath).get()
                if flag_title:
                    country_list = extract_country_from_flag_title(flag_title)
                    print(country_list)
                else:
                    country = None
            item['country'] = country
        except Exception as e:
            item['country'] = None
            self.logger.error(f'Ошибка при извлечении страны: {e}')

        try:
            year = kwargs.get('year')
            item['year'] = year if year else None
        except Exception as e:
            item['year'] = None
            self.logger.error(f'Ошибка при извлечении года: {e}')

        yield item
