import scrapy
from wiki_film_scraper.items import WikiFilmScraperItem


class FilmSpider(scrapy.Spider):
    name = 'movies'
    allowed_domains = ['wikipedia.org']
    start_urls = ['https://ru.wikipedia.org/wiki/Категория:Фильмы_по_алфавиту']

    def parse(self, response):
        movie_links = response.xpath('//*[@id="mw-pages"]/div[2]/div//a/@href').getall()
        for link in movie_links:
            movie_url = response.urljoin(link)
            yield scrapy.Request(movie_url, callback=self.parse_movie)

        next_page = response.xpath('//a[contains(text(), "Следующая страница")]/@href').get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            self.logger.info(f"Следующая страница найдена. {next_page_url}")
            yield scrapy.Request(next_page_url, callback=self.parse)
        else:
            self.logger.info("Следующая страница не найдена.")

    def parse_movie(self, response):
        movie = WikiFilmScraperItem()

        title = response.xpath('//*[@id="mw-content-text"]/div[1]/table[1]/tbody/tr[1]/th//text()').getall()
        movie['title'] = " ".join([t.strip() for t in title if t.strip()])

        genre_links = response.xpath('//*[@id="mw-content-text"]/div[1]/table[1]/tbody/tr[3]/td/span/a/text()').getall()
      
        if not genre_links:
            genre_text = response.xpath('//*[@id="mw-content-text"]/div[1]/table[1]/tbody/tr[3]/td/span//text()').getall()
            genre = " ".join([g.strip() for g in genre_text if g.strip()])
           
            if not genre:
                genre = "Не указан"
        
        movie['genre'] = genre

        director = response.xpath('//th[contains(text(), "Режиссёр")]/following-sibling::td//a/text()').getall()
        director = " ".join([d.strip() for d in director if d.strip()])
        if not director:
            director = "Не указан"
        movie['director'] = director

        country = response.xpath('''
            //th[contains(text(), "Страна")]/following-sibling::td/span/span/a/span//text()|
            //th[contains(text(), "Страны")]/following-sibling::td/span/span/a/span//text() |
            //th[contains(text(), "Страна")]/following-sibling::td//a/text() |
            //th[contains(text(), "Страны")]/following-sibling::td//a/text()
            ''').getall()
        if not country:
            country = ["Не указана"]
        movie['country'] = " ".join([c.strip() for c in country if c.strip()])

        year = response.xpath('''
            //th[contains(text(), "Год")]/following-sibling::td//a/text() |
            //th[contains(text(), "Год")]/following-sibling::td//text()
        ''').getall()
        year = " ".join([y.strip() for y in year if y.strip()])
        if not year:
            year = "Не указан"
        movie['year'] = year

        yield movie
