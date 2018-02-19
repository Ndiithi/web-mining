'''
Created on Jan 11, 2018

@author: duncan
'''
import sys
import scrapy
import re
#sys.path.insert(0, "/home/duncan/workspace/upwork_scripts/spiders/MailScrapper/MailScrapper")
from .. items import CasinoscraperItem
from scrapy.linkextractors import LinkExtractor

class MySpider(scrapy.Spider):
    name = 'CasionScraper'
    allowed_domains = ['worldcasinodirectory.com']
    
    start_urls = [
     "https://www.worldcasinodirectory.com/united-states",
     ]
    
    def normalize_whitespace(self,strr):
        strr = strr.strip()
        strr = re.sub(r'\r\n\t\t\t\t\t\r\n\t\t\t\t', ' ', strr)
        return strr
    
    
    def get_casino_attributes(self,response):
        from __builtin__ import str
        item = CasinoscraperItem()
        casino_name = response.meta.get('casino_name')
        file_name= response.meta.get('file_name')
        casino_meta=response.css('div div.contactInfo div')

        
        casino_phone=''
        casino_url=''
        casino_email=''
        casino_fb=''
        casino_twitter=''
        address=response.css('#content div div h3 span::text')[0].extract()
        
        found_phone=False
        
        for count,p_tag in enumerate(casino_meta.css('p strong::text').extract()):
            
            
            if(str(p_tag).strip().lower()==str('phone:')):
                
                casino_phone = self.normalize_whitespace(casino_meta.css('p::text')[count].extract())
                found_phone=True
          
            if(str(p_tag).strip().lower()==str('website:')):
                casino_url = casino_meta.css('p')[count].css('a::attr(href)').extract()[0]
                
            if(str(p_tag).strip().lower()==str('email:')):
                casino_email = casino_meta.css('p')[count].css('a::attr(href)').extract()[0]
                casino_email=casino_email.replace('mailto:', '')
#     
            if(str(p_tag).strip().lower()=='facebook:'):
                casino_fb = casino_meta.css('p')[count].css('a::attr(href)').extract()[0]

                
            if(str(p_tag).strip().lower()=='twitter:'):
                casino_twitter = casino_meta.css('p')[count].css('a::attr(href)').extract()[0]
            
            
            if(str(p_tag)==str('toll-free:') and found_phone==False):
                casino_phone = self.normalize_whitespace(casino_meta.css('p::text')[count].extract())
                

        item['casino_name'] = casino_name
        item['casino_phone'] = casino_phone
        item['casino_url'] = casino_url 
        item['casino_email'] = casino_email
        item['casino_facebook'] = casino_fb
        item['casino_twitter']= casino_twitter
        item['file_name']= file_name
        item['address']=address
        
        yield item
        
    
    def get_city_casino(self, response):
        file_name= response.meta.get('file_name')
        individual_casion_link= response.css('div.casino-bricks-container div  div.halfWidth  div.item-cell div div.hideCasino a::attr(href)').extract()   
        casino_name =response.css('div.casino-bricks-container div  div.halfWidth  div.item-cell div div.hideCasino a::attr(data-full)').extract()
        for key in range(len(casino_name)):
            yield scrapy.Request(individual_casion_link[key], callback=self.get_casino_attributes, meta={'casino_name': casino_name[key],'file_name':file_name})   
    
    
    def parse(self, response):
        item = CasinoscraperItem()
        casino_list_location =response.css('#multimenu-locations div ul li a::attr(href)').extract()
        casino_list_cities =response.css('#multimenu-locations div ul li a::text').extract()
   

        for count,link in enumerate(casino_list_location):
            file_name=casino_list_cities[count]
            link='https://'+link
            yield scrapy.Request(link, callback=self.get_city_casino,meta={'file_name':file_name})

        item['casino_twitter'] = casino_list_location

        yield item
        
        
      