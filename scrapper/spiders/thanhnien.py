import scrapy
# from pyvi.pyvi import ViTokenizer
import unicodedata

class ThanhNienSpider(scrapy.Spider):
    name = "thanhnien"
    BASE_URL = 'https://thanhnien.vn'

    def start_requests(self):
        url = self.BASE_URL
        yield scrapy.Request(url=url, callback=self.parse_first_level)

    def parse_first_level(self, response):
        links = response.css('nav.site-header__nav a::attr(href)').extract()
        normal_links = [self.BASE_URL + x for x in links if not x.startswith('http') and "javascript" not in x]
        for link in normal_links:
            yield scrapy.Request(link, callback=self.parse_second_level)

    def parse_second_level(self, response):
        for link in self.parse_third_level(1, response.url)(response):
            yield link
        links = response.css('nav.site-header__nav a::attr(href)').extract()
        normal_links = [self.BASE_URL + x for x in links if not x.startswith('http') and "javascript" not in x]
        for link in normal_links:
            yield scrapy.Request(link, callback=self.parse_third_level(1, link))

    def parse_third_level(self, count, orig):
        def child(response):
            article_groups = response.css('div.cate-content div.zone--timeline')
            article_links = article_groups.css('div.relative article.story a::attr(href)').extract()
            for link in article_links:
                link = '/'.join(link.split('/')[-2:])
                yield scrapy.Request(self.BASE_URL + '/' + link, callback=self.parse_content)
            yield scrapy.Request(orig + 'trang-{}.html'.format(count+1), callback=self.parse_third_level(count+1, orig))
        return child

    def parse_content(self, response):
        article = response.css("div#storybox")
        title = ' '.join(article.css("h1.details__headline").xpath('.//text()').extract())
        summary = ' '.join(article.css("div.sapo").xpath('.//text()').extract())
        content = '\n'.join(' '.join(x.strip() for x in div.xpath('.//text()[not(ancestor::td) and not(ancestor::article)]').extract() if x.strip() != "").strip() for div in article.css("div#main_detail div#abody").xpath("./div[not(contains(@class,'details__morenews')) and not(contains(@class,'imgcaption'))] | ./h3 | ./p"))
        cat = ', '.join(response.css('div.breadcrumbs').xpath('//span[@itemprop="title"]').css('::text').extract())
        date = ' '.join(response.css('div.details__meta div.meta time::text').extract())
        # tags = response.xpath('//ul[@class="tags"]//a/text()').extract()
        yield {
            '_id': response.url,
            'date': date,
            'title': unicodedata.normalize('NFKC', title),
            'summary': unicodedata.normalize('NFKC', summary),
            'content': unicodedata.normalize('NFKC', content),
            'type': cat,
            # 'tags': tags
        }
