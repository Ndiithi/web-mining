# -*- coding: utf-8 -*-



from xlutils.copy import copy
from xlrd import open_workbook 


class MailScrapperPipeline(object):
    def process_item(self, item, spider):
        return item

    def close_spider(self,spider):
        START_ROW = 0 # 0 based (subtract 1 from excel row number)
        col_url = 0
        col_mail = 1
        file_path="/home/duncan/workspace/upwork_scripts/spiders/MailScrapper/MailScrapper/sites_to_crawl.xlsx"
        rb = open_workbook(file_path)
        r_sheet = rb.sheet_by_index(0) 
        wb = copy(rb) 
        w_sheet = wb.get_sheet(0) 
        
        for row_index in range(START_ROW, r_sheet.nrows):
            site_url = r_sheet.cell(row_index, col_url).value
            for k in spider.scrapped_mails:
                if k in site_url or k==site_url or site_url in k:
                    w_sheet.write(row_index, col_mail, spider.scrapped_mails[k])
           
        wb.save(file_path +'.xlsx')
        