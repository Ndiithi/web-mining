'''
Created on Jan 11, 2018

@author: duncan
'''

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from urlparse import urlparse
import re
from mock.mock import self
import xlrd


class MySpider(CrawlSpider):
    name = 'MailSrapper'
    allowed_domains = []
    scrapped_mails={}
    
    book = xlrd.open_workbook("/home/duncan/workspace/upwork_scripts/spiders/MailScrapper/MailScrapper/sites_to_crawl.xlsx")
    sh = book.sheet_by_index(0)
    start_urls=[sh.cell_value(rowx=r, colx=c) for r in range(sh.nrows) for c in  range(sh.ncols)]

    for url in start_urls:
        loc=urlparse(url).netloc
        allowed_domains.append(loc)
    
    rules = (
        #Rule(LinkExtractor(allow=None),  callback='parse_item', follow=True, process_links='link_filtering'),
        Rule(LinkExtractor(allow=None,unique=True,allow_domains=allowed_domains),process_links='link_filtering', callback='parse_item', follow=True),
    )
       
            
            
    def link_filtering(self, links):
        ret = []
        for link in links:
            if('contact' in link.url  or 'info' in link.url  or 'help' in link.url):
                ret.append(link)
        return ret
    
    
    def parse_item(self, response):
        regex = re.compile('\w+[.|\w]\w+@\w+[.]\w+[.|\w+]\w+')
        emails = re.findall(regex, response.body)
        parsed_loc_uri=urlparse(response.url)
        loc='{uri.scheme}://{uri.netloc}/'.format(uri=parsed_loc_uri)
        for email in emails:
            try:
                mail_value=self.scrapped_mails[loc]
                if(email not in mail_value):
                    mail_value=mail_value+';'+email
                    self.scrapped_mails[loc]=mail_value
            except KeyError:
                self.scrapped_mails[loc]=email
        return self.scrapped_mails
    
    