import scrapy
from pyvi.pyvi import ViTokenizer


class MuaBanSpider(scrapy.Spider):
    name = "muaban"
    BASE_URL = 'https://muaban.net/mua-ban-nha-dat-cho-thue-toan-quoc-l0-c3'
    
    def start_requests(self):
        url = self.BASE_URL
        yield scrapy.Request(url=url, callback=self.parse)
        
    def parse(self, response):
        links = response.css('.mbn-box-list .mbn-box-list-content  a.mbn-image::attr(href)').extract()
        paging = response.css('.paging .pagination li:last-child a::attr(href)').extract_first()
        for link in links:
            yield scrapy.Request(link, callback=self.parse_content)
        if paging is not None:
            yield scrapy.Request(paging, callback=self.parse)


    def parse_content(self, response):
        title = response.css('.cl-title h1::text').extract_first()
        category = response.css('.rdfa-breadcrumb > div:nth-child(1) > div:nth-child(1) > span:nth-child(8) > a:nth-child(1)::attr(title)').extract_first()
        subcat = response.css('.rdfa-breadcrumb > div:nth-child(1) > div:nth-child(1) > span:nth-child(10) > a:nth-child(1)::attr(title)').extract_first()
        content = response.css('.ct-body').xpath('.//text()').extract()
        content = '\n'.join(content).lstrip().rstrip()
        mobile = response.css('.contact-mobile span::text').extract_first()
        info = response.css('.cl-price-sm span.float-left')
        price = info.xpath('.//i[contains(@class, "icon-dollar")]/following-sibling::node()/descendant-or-self::text()').extract_first()
        location = info.xpath('.//i[contains(@class, "icon-map")]/following-sibling::node()/descendant-or-self::text()').extract_first()
        date = info.xpath('.//i[contains(@class, "icon-clock")]/following-sibling::node()/descendant-or-self::text()').extract_first()
        details = response.css('.ct-tech li.tect-item')
        detail_dicts = []
        for item in details:
            item_detail = {}
            item_detail['name'] = item.xpath('.//div[contains(@class, "item-name")]/text()').extract_first()
            item_detail['value'] = item.xpath('.//div[contains(@class, "item-value")]/text()').extract_first()
            detail_dicts.append(item_detail)
        yield {'_id': response.url,
               'date': date,
               'title': title,
               'content': content,
               'type': category,
               'subtype': subcat,
               'price': price,
               'location': location,
               'mobile': mobile
               }
