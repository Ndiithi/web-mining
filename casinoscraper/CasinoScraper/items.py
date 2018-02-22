# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CasinoscraperItem(scrapy.Item):
    # define the fields for your item here like:
    casino_name = scrapy.Field()
    casino_phone = scrapy.Field()
    casino_url = scrapy.Field()
    casino_email = scrapy.Field()
    casino_facebook = scrapy.Field()
    casino_twitter = scrapy.Field()
    file_name = scrapy.Field()
    address = scrapy.Field()