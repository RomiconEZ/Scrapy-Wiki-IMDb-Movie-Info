import scrapy


class WikiMoviesScraperItem(scrapy.Item):
    """
    Scrapy Item for storing movie data.
    """

    title = scrapy.Field()  # Title of the movie
    genre = scrapy.Field()  # Genre(s) of the movie
    director = scrapy.Field()  # Director(s) of the movie
    country = scrapy.Field()  # Country or countries of production
    year = scrapy.Field()  # Release year of the movie
    rating = scrapy.Field()  # IMDb rating of the movie
