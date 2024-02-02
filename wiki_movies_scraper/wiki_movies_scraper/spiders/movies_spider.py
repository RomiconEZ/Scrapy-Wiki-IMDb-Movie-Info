import re
import scrapy
from scrapy.http import Response
from urllib.parse import unquote
from ..items import WikiMoviesScraperItem
import pymorphy2


class MoviesSpider(scrapy.Spider):
    """
    Spider for scraping movie data from Wikipedia and IMDb.

    This spider starts by scraping a list of movies by year from Wikipedia,
    then fetches detailed information for each movie, including IMDb ratings.
    """

    name = "movies_spider"
    allowed_domains = ["ru.wikipedia.org", "www.imdb.com"]
    start_urls = ["https://ru.wikipedia.org/wiki/Категория:Фильмы_по_годам"]

    def parse(self, response: Response, **kwargs):
        """
        Parses the main page of movie categories by year.

        Args:
            response (Response): The response object used to select parts of the page to extract data.
        """
        self.logger.info(f'Visiting page: {unquote(response.url.split("/")[-1])}')
        # Iterate through all links to movie categories by year
        for href in response.xpath(
            '//*[@id="mw-subcategories"]/div/div/div[3]/ul/li/div/div['
            '@class="CategoryTreeItem"]/a/@href'
        ):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_year_page)

    def parse_year_page(self, response: Response, **kwargs):
        """
        Parses the page for a specific year, extracting links to individual movies.

        Args:
            response (Response): The response object for the year page.
        """
        year = unquote(response.url.split("/")[-1]).split("_")[-2]
        self.logger.info(f'Visiting page: {unquote(response.url.split("/")[-1])}')

        # Iterate through all links to individual movies
        for href in response.xpath(
            '//*[@id="mw-pages"]//div[contains(@class, "mw-category-group")]//ul/li/a/@href'
        ):
            url = response.urljoin(href.extract())
            yield scrapy.Request(
                url, callback=self.parse_movie_details, cb_kwargs={"year": year}
            )

    def parse_movie_details(self, response: Response, **kwargs):
        """
        Parses the details page of an individual movie.

        Args:
            response (Response): The response object for the movie details page.
            kwargs: Additional keyword arguments, primarily used for passing the year of the movie.
        """
        self.logger.info(f'Visiting movie page: {unquote(response.url.split("/")[-1])}')
        item = WikiMoviesScraperItem()

        # XPath expressions for extracting various movie details
        base_xpath = '//*[@id="mw-content-text"]/div[1]/table[1]'
        title_xpath = f'{base_xpath}//th[@class="infobox-above"]//text()'

        try:
            item["title"] = response.xpath(title_xpath).get()
        except Exception as e:
            item["title"] = None
            self.logger.error(f"Error extracting title: {e}")

        # If the title is missing or empty, yield the item early
        if item["title"] is None or item["title"].strip() == "":
            yield item

        # More XPath expressions for other details
        genre_xpath = f"""
            {base_xpath}//th[contains(., "Жанр") or contains(., "Жанры")]/following-sibling::td//span[@data-wikidata-property-id="P136"]//text() |
            {base_xpath}//th[contains(., "Жанр") or contains(., "Жанры")]/following-sibling::td//a/text() |
            {base_xpath}//th[contains(., "Жанр") or contains(., "Жанры")]/following-sibling::td/text()
        """.strip()
        director_xpath = f"""{base_xpath}//th[contains(text(), "Режиссёр") or contains(text(), "Режиссёры")]/following-sibling::td//text()"""
        country_xpath = f"""
            {base_xpath}//th[contains(text(), "Страна") or contains(text(), "Страны")]/following-sibling::td//a/text() |
            {base_xpath}//th[contains(text(), "Страна") or contains(text(), "Страны")]/following-sibling::td//span[@data-sort-value]/@data-sort-value |
            {base_xpath}//th[contains(text(), "Страна") or contains(text(), "Страны")]/following-sibling::td//span[contains(@class, "no-wikidata")]/text() |
            {base_xpath}//th[contains(text(), "Страна") or contains(text(), "Страны")]/following-sibling::td/text()
        """.strip()
        flag_title_xpath = f"{base_xpath}//th[contains(., 'Страна') or contains(., 'Страны')]/following-sibling::td//a[@class='mw-file-description']/@title"
        imdb_site_link_xpath = f"{base_xpath}//th[a[@title='Internet Movie Database']]/following-sibling::td//a[contains(@href, '/title/')]/@href"

        # Extract and clean the genre data
        try:
            genres_list = response.xpath(genre_xpath).getall()
            genres_cleaned = clean_list(genres_list)
            item["genre"] = genres_cleaned or None
        except Exception as e:
            item["genre"] = None
            self.logger.error(f"Error extracting genre: {e}")

        # Extract and clean the director data
        try:
            directors_list = response.xpath(director_xpath).getall()
            directors_cleaned = clean_list(directors_list)
            item["director"] = directors_cleaned or None
        except Exception as e:
            item["director"] = None
            self.logger.error(f"Error extracting director: {e}")

        # Extract and clean the country data
        try:
            country_data = response.xpath(country_xpath).getall()
            country = clean_list(country_data)
            if not country:
                flag_titles = response.xpath(flag_title_xpath).getall()
                if flag_titles:
                    country = convert_flag_list_to_country_list(flag_titles)
                else:
                    country = None
            item["country"] = country
        except Exception as e:
            item["country"] = None
            self.logger.error(f"Error extracting country: {e}")

        # Extract the year of the movie
        try:
            year = kwargs.get("year")
            item["year"] = year if year else None
        except Exception as e:
            item["year"] = None
            self.logger.error(f"Error extracting year: {e}")

        item["rating"] = None
        try:
            imdb_site_link = response.xpath(imdb_site_link_xpath).get()
        except Exception as e:
            imdb_site_link = None
            self.logger.error(f"Error extracting IMDb link: {e}")

        # If IMDb link exists, fetch the rating, otherwise yield the item
        if imdb_site_link:
            yield scrapy.Request(
                imdb_site_link,
                callback=self.parse_imdb_movie_ratings,
                cb_kwargs={"item": item},
            )
        else:
            self.logger.warning(f'No IMDb link for {item["title"]}')
            yield item

    def parse_imdb_movie_ratings(self, response: Response, **kwargs):
        """
        Parses the IMDb page for a movie to extract the rating.

        Args:
            response (Response): The response object for the IMDb page.
            kwargs: Contains the item being processed.
        """
        item = kwargs.get("item")
        self.logger.info(f'Visiting IMDb rating page for: {item["title"]}')

        try:
            # XPath to find the span with text 'IMDb Rating' and then navigate to the rating value
            rating_xpath = "//div[contains(text(), 'IMDb RATING')]/following-sibling::a//div[contains(@data-testid, 'rating')]/span/text()"
            # Extract the rating
            rating = response.xpath(rating_xpath).get()
            if rating:
                item["rating"] = float(rating)
            else:
                item["rating"] = None
        except Exception as e:
            item["rating"] = None
            self.logger.error(f"Error extracting rating: {e}")
        yield item


def convert_flag_list_to_country_list(flag_list):
    """
    Converts a list of flags to a list of countries.

    Args:
        flag_list (list): List of flags, typically extracted from the Wikipedia page.

    Returns:
        list: List of country names in normal form.
    """
    morph = pymorphy2.MorphAnalyzer()
    country_list = []

    for flag in flag_list:
        # Remove "Flag" word and extract the country name
        country_name_part = flag.replace("Флаг ", "")
        # Normalize the country name
        parsed_word = morph.parse(country_name_part)[0]
        country = parsed_word.normal_form
        country_list.append(country)

    return country_list


def clean_list(_list):
    """
    Cleans a list by stripping white spaces and removing unwanted characters.

    Args:
        _list (list): The list to be cleaned.

    Returns:
        list: The cleaned list.
    """
    cleaned_list = [
        element.strip()
        for element in _list
        if re.search(r"[a-zA-Zа-яА-Я]", element) and element.strip() not in ["[d]", "и"]
    ]
    return cleaned_list
