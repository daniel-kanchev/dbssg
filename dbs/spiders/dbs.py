import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from dbs.items import Article


class dbsSpider(scrapy.Spider):
    name = 'dbs'
    start_urls = ['https://www.dbs.com/media/news-list.page']

    def parse(self, response):
        articles = response.xpath('//div[@id="newsLists"]//ul/li')
        for article in articles:
            link = article.xpath('./a/@href').get()
            date = article.xpath('.//span[@class="news-date"]/text()').get()
            if date:
                date = " ".join(date.split())

            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

        next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response, date):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@class="rich-text-box"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content[1:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
