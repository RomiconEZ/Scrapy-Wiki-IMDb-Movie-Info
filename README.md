# Movie Information Scraper

## Project Overview
The Wiki Movies Scraper is a Scrapy project designed to collect information on movies from Wikipedia, including their Title, Genre, Director, Country & Year, and IMDB Rating. The data is then stored in a CSV format.

To use it in your language, change the scraping parameters related to the selection of words from the html page

## Features
- Scrape movie details from Wikipedia.
- Output the data in CSV format

## Requirements
- Python 3.10
- Scrapy

## Installation and Setup
Clone the repository and navigate to the project directory:
```bash
git clone https://github.com/RomiconEZ/Scrapy-Wiki-IMDb-Movie-Info.git
```
```bash
cd wiki_movies_scraper
```

## Usage
To start scraping movies, run the following command:
```bash
scrapy crawl movies_spider
```

## Project Structure
The directory structure for this Scrapy project is as follows:
- `ScrapyParsers/`
  - `wiki_movies_scraper/`
    - `wiki_movies_scraper/`
      - `spiders/`
        - `__init__.py`
        - `movies_spider.py`
      - `__init__.py`
      - `items.py`
      - `middlewares.py`
      - `pipelines.py`
      - `settings.py`
      - `scrapy.cfg`
      - `movies_example.csv`
    - `poetry.lock`
    - `pyproject.toml`
    - `README.md`