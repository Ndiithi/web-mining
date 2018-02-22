# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import csv
import os
from urlparse import urlparse

class CasinoscraperPipeline(object):
    def process_item(self, item, spider):
        file_name=item['file_name']
        file_exists = os.path.isfile(file_name+'.csv')
        with open(file_name+'.csv',"a") as csvfile:
            
            name=item['casino_name'].encode('utf-8')
            phone=item['casino_phone'].encode('utf-8')
            parsed_loc_uri=urlparse(item['casino_url'])
            address=item['address'].encode('utf-8')
            print('------------------==================--------------------')
            print(address)
            web=parsed_loc_uri.scheme+'://'+parsed_loc_uri.netloc
            if len(web)<5:
                web=''
            mail=item['casino_email'].encode('utf-8')
            fb=item['casino_facebook'].encode('utf-8')
            tw=item['casino_twitter'].encode('utf-8')
            
#             filewriter = csv.writer(csvfile, delimiter=',',
#                                     quotechar='|', quoting=csv.QUOTE_MINIMAL)
            filewriter = csv.writer(csvfile)
            if not file_exists:
                filewriter.writerow(['Casino Name', 'address' ,'Phone', 'website url', 'Email', 'Facebook', 'Twitter'])
            filewriter.writerow([name,address, phone ,web, mail, fb, tw])
