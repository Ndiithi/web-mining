# -*- coding: utf-8 -*-

import time
import sys
from datetime import datetime
import os
from selenium.webdriver.common.action_chains import ActionChains
import signal
from selenium.webdriver.support.ui import WebDriverWait
import csv
import urllib
import io
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import logging.handlers
from logging import Logger
from time import sleep
from cookielib import logger


IMAGE_PATH = os.path.abspath('./images')
IMAGE_PATH = IMAGE_PATH + "/"

#start_url = 'http://139.59.4.7:8080/settings/'
start_url='https://www.tripadvisor.es/Restaurants'
LOG_PATH = os.path.abspath('./logs')
LOG_PATH = LOG_PATH + "/"

break_all_count = 0
break_all = False
initial_req=True
max_scroll_page=None

class BrowserAutomation(object):

    def __init__(self):

        if not os.path.isfile("searchtext.txt"):
            logger.error("'Search text' file does not exist")
            sys.exit()
        else:
            f = io.open('searchtext.txt', 'r', encoding="utf-8")
            self.search_texts = f.readlines()
            
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--no-sandbox')
        options.add_argument("--test-type")
        options.add_argument("--window-size=1420,780")
        # options.binary_location = "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"
        
        driver = webdriver.Chrome(chrome_options=options)
        global IMAGE_PATH 
        global count
        self.driver = driver  # webdriver.PhantomJS(executable_path='/Users/krishnachandak/scrapbroker/node_modules/phantomjs/bin/phantomjs',desired_capabilities=capabilities, service_args=service_args)
        self.driver.implicitly_wait(5)  # seconds


    def read_scrap_position(self):
    #open position file if exists else create        
        try:
            position = open("position.txt", 'r')
            self.last_position = position.readline()
            self.last_position = self.last_position.strip()
            position.close()
        except IOError:
            position = open("position.txt", 'w')
            position.write('0;1;0')
            position.close()
            position = open("position.txt", 'r')
            self.last_position = position.readline()
            self.last_position = self.last_position.strip()
            position.close()
    
    
    def launch_browser(self,start_url):
        logger.info('Launching Browser')
        self.driver.get(start_url)
        sleep(5)
        self.driver.save_screenshot(IMAGE_PATH + 'mainScreen.png')
        logger.info("Browser launch successfully.")

    
    def _parse(self,item_position,cur_page):    
        logger.info('looking for list item')
        listings = WebDriverWait(self.driver, 10).until(lambda x: x.find_elements_by_css_selector('div#search_result div.all-results div.all-results div.result div.result_wrap div.info div.title'))
        logger.info('looking for list item done')
        for index, listing in enumerate(listings):
            logger.info('stats, item on loop {}, item to scrap {}'.format(index, item_position))
            if(index != int(item_position)):
                logger.info('skip to item to scrap')
                continue
            try:
                print 'Opening listing Number: -->'
                print item_position
                #listing.click()
                logger.info('item name: {}'.format(listing.find_element_by_css_selector('span').text))
                sleep(7)
                self.read_scrap_position()
                cont_position = self.last_position.split(';')
                cur_search_string = cont_position[0]
                cur_page = cont_position[1]
                cur_listing_pos = int(cont_position[2]) + 1
                item_position=cur_listing_pos
                self.save_update_scrap_position(str(cur_search_string), str(cur_page), str(cur_listing_pos))
            # retry searching and click again
            except Exception, e:
                try:
                    print 'Failed to click item'
                    print 'Retrying search & click item'
                    l = WebDriverWait(self.driver, 10).until(lambda x: x.find_elements_by_css_selector('div#search_result div.all-results div.all-results div.result div.result_wrap div.info div.title'))
                    logger.info('item name: {}'.format(listing.find_element_by_css_selector('span').text))
                    #l[index].click()
                    sleep(7)
                except Exception, e:
                    # break all to refresh listing after failed click, max set to 1 (break_all_count==1)
                    cont_position = self.last_position.split(';')
                    cur_search_string = cont_position[0]
                    cur_page = cont_position[1]
                    cur_listing_pos = int(cont_position[2]) + 1
                    item_position=cur_listing_pos
                    self.save_update_scrap_position(str(cur_search_string), str(cur_page), str(cur_listing_pos))
                    break_all_count = 0
        
        cont_position = self.last_position.split(';')
        cur_search_string = cont_position[0]
        cur_page = cont_position[1]
        cur_listing_pos = 0
        self.save_update_scrap_position(str(cur_search_string), str(cur_page), str(cur_listing_pos))
            
    
    
    def get_page_to_scrap(self,max_scroll_page,cur_page):
        continue_next_page=True
        #if index > int(page_link.get_attribute("data-page")) or 
        logger.info('Maximum scroll page {}'.format(max_scroll_page))
        if(max_scroll_page is not None):
            if int(cur_page) > int(max_scroll_page):
                logger.info('maximum page scroll reached')
                continue_next_page=False
                self.read_scrap_position()
                cont_position = self.last_position.split(';')
                cur_search_string = cont_position[0]
                cur_page = 1
                cur_listing_pos = 0
                self.save_update_scrap_position(str(cur_search_string), str(cur_page), str(cur_listing_pos))
                logger.info('updating position done')
                return continue_next_page
        logger.info('looking for start position')
        sleep(5)
        while True:
            logger.info('looking for pagination')
            pagination_pages = WebDriverWait(self.driver, 10).until(lambda x: x.find_elements_by_css_selector('div#search_result div div div.ui_pagination div.pageNumbers a.pageNum'))
            logger.info('looking for pagination done')
            for indx,page_link in enumerate(pagination_pages):
                logger.info('page link {}'.format(page_link.get_attribute("data-page")))
                last_page=int(pagination_pages[len(pagination_pages)-1].get_attribute("data-page"))
                if(int(page_link.get_attribute("data-page"))==int(cur_page)):
                    if('current' not in page_link.get_attribute("class")):
                        sleep(5)
                        try:
                            page_link.click()
                        except Exception,e:
                            try:
                                pagination_pages = WebDriverWait(self.driver, 10).until(lambda x: x.find_elements_by_css_selector('div#search_result div div div.ui_pagination div.pageNumbers a.pageNum'))
                                pagination_pages[indx].click()
                            except Exception,e:
                                logger.info('Last click page link retry')
                                if(int(cur_page)!=last_page):
                                    pagination_pages[indx+1].click()
                                    cur_page=cur_page+1
                                    cont_position = self.last_position.split(';')
                                    cur_search_string = cont_position[0]
                                    cur_page = int(cont_position[1])+1
                                    cur_listing_pos = cont_position[2]
                                    self.save_update_scrap_position(str(cur_search_string), str(cur_page), str(cur_listing_pos))
                                    
                    logger.info('starting at page {}'.format(cur_page))
                    sleep(6)
                    
                    if(int(cur_page)==last_page):
                        logger.info('updating position')
                        self.read_scrap_position()
                        cont_position = self.last_position.split(';')
                        cur_search_string = cont_position[0]
                        cur_page = 1
                        cur_listing_pos = 0
                        self.save_update_scrap_position(str(cur_search_string), str(cur_page), str(cur_listing_pos))
                        logger.info('updating position done')
                        return continue_next_page
                
                
                    
                    return continue_next_page
                
            sleep(4)
            try:
                logger.info("clicking pagination number {}".format(pagination_pages[len(pagination_pages)-2].get_attribute("data-page")))
                pagination_pages[len(pagination_pages)-2].click()
            except Exception,e:
                pagination_pages = WebDriverWait(self.driver, 10).until(lambda x: x.find_elements_by_css_selector('div#search_result div div div.ui_pagination div.pageNumbers a.pageNum'))
                sleep(3)
                pagination_pages[len(pagination_pages)-2].click()
            logger.info('scrolling to second last link in pagination page to get last stop position')
            sleep(7)
        break_all = False
        return continue_next_page
    
    
    def parse_document(self, max_scroll_page=None):
        cont = True
        max_scroll_page = max_scroll_page
        # for index,search_text in enumerate(self.search_texts):
        srch_index = 0
        submit_text_len = len(self.search_texts)
        initial_req = True
        
        # for each search term loop
        while cont: 
            self.read_scrap_position()
            search_text = self.search_texts[srch_index]
            #search_text = search_text.encode('utf-8').strip()
            if(len(self.last_position) == 0):
                cur_page = 1
                cur_listing_pos = 0
            else:
                cont_position = self.last_position.split(';')
                cur_page = cont_position[1]
                cur_listing_pos = cont_position[2]
                if srch_index != int(cont_position[0]):
                    srch_index = srch_index + 1
                    continue
            logger.info('current search term --->')
            logger.info(search_text)

            self.driver.execute_script("document.querySelector('div#taplc_trip_search_home_restaurants_0 div  div div span input.typeahead_input').value=arguments[0]",search_text)         #search_elem = self.driver.find_element_by_css_selector('div#taplc_trip_search_home_restaurants_0 div  div div span input.typeahead_input')
            logger.debug('clear search input')
            sleep(3)
            WebDriverWait(self.driver, 10).until(lambda x: x.find_element_by_css_selector("button#SUBMIT_RESTAURANTS")).click()
            logger.debug('search for text')
            sleep(7)
            
            while True:
                continue_next_page=True
                continue_next_page=self.get_page_to_scrap(max_scroll_page,cur_page)
                if(continue_next_page):
                    sleep(7)
                    self.read_scrap_position()
                    cont_position = self.last_position.split(';')
                    cur_page = cont_position[1]
                    cur_listing_pos = cont_position[2]
                    
                    logger.info('Parsing page')
                    self._parse(cur_listing_pos,cur_page)
                    
                    logger.info('updating position')
                    self.read_scrap_position()
                    cont_position = self.last_position.split(';')
                    cur_search_string = cont_position[0]
                    cur_page = int(cont_position[1])+1
                    cur_listing_pos = cont_position[2]
                    self.save_update_scrap_position(str(cur_search_string), str(cur_page), str(cur_listing_pos))
                    logger.info('updating position done')
                else:
                    break
                
            cont_position = self.last_position.split(';')            
            cur_search_string = int(cont_position[0]) + 1
            cur_page = 1
            cur_listing_pos = 0
            self.save_update_scrap_position(str(cur_search_string), str(cur_page), str(cur_listing_pos))
        
            if srch_index + 1 == submit_text_len:
                print 'exiting completely'
                cont = False
            else:
                srch_index = srch_index + 1


    def save_update_scrap_position(self, cur_search_string, cur_page_pos, cur_item_pos):
        print 'updating position'
        position = open("position.txt", 'w')
        pos = str(cur_search_string) + ';' + str(cur_page_pos) + ';' + str(cur_item_pos)
        position.write(pos)
        position.close()
        position = open("position.txt", 'r')
        self.last_position = position.readline()
        position.close()
    
    
    def tear_down(self):
        logger.info("terminating upwork crawler, shutting down web driver")
        try:
            self.driver.quit()
            #os.system("pkill geckodriver") #if usign fire fox, change accordingly
        except WebDriverException,e:
            pass
    
    
    def save_item_details(self, file_name, name, address, asked_qstn):  
        print 'Check if question submitted before saving'
        print 'Was question submitted {}'.format(asked_qstn)
        file_name = file_name.strip().encode('utf-8')
        file_exists = os.path.isfile(file_name + '.csv')
        if os.name == 'nt':
            _binary = 'b'
        else:
            _binary = ''
        with open(file_name + '.csv', 'a' + _binary) as csvfile:
            name = name.encode('utf-8')
            address = address.encode('utf-8')
            print(name + ' ' + address)
            filewriter = csv.writer(csvfile)
            if not file_exists:
                filewriter.writerow(['Date', 'Name', 'Address'])
            if len(name.strip()) != 0 and len(address.strip()) != 0 and asked_qstn:
                dt = datetime.now().strftime('%Y-%m-%d')
                filewriter.writerow([dt, name, address])
                print 'Item was saved'
            else:
                print 'Item was not saved'
            print('------------------==================--------------------')
        
    
    def reset_position(self):
        position = open("position.txt", 'w')
        position.write('0;1;0')
        position.close()
    
    
    def run_automation(self,max_scroll_page=None):
        self.launch_browser(start_url)
        self.parse_document(max_scroll_page)
        self.reset_position()



if __name__ == "__main__":
    
    if not os.path.isdir(LOG_PATH):
        try:
            os.mkdir(LOG_PATH)                
        
        except Exception, e:
            pass

    log_file = "scraper.log"
    full_pth = os.path.join(LOG_PATH, log_file)
    logger = logging.getLogger("scraper")
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.setLevel(logging.DEBUG)
    
    browser = BrowserAutomation()

    try:

        if os.path.isdir(LOG_PATH):

            fh = logging.handlers.RotatingFileHandler(full_pth, maxBytes=5242880, backupCount=5)
            fh.setFormatter(formatter)
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(formatter)
            logger.addHandler(ch)
            logger.addHandler(fh)
        else:
            fh = logging.handlers.RotatingFileHandler(log_file, maxBytes=5242880, backupCount=5)
            fh.setFormatter(formatter)
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(formatter)
            logger.addHandler(ch)
            logger.addHandler(fh)
            
        logger.info("====================================================================")
        logger.info( "Script Started At : " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        logger.info("====================================================================")

        try: 
            max_scroll_page = sys.argv[1]
        except IndexError:
            pass
        
        #start scraping
        browser.run_automation(max_scroll_page)
        
    except Exception as e:
        browser.driver.save_screenshot(IMAGE_PATH + 'end.png')
        logger.error("Error occured ")
        logger.error(e, exc_info=True)
        browser.driver.save_screenshot(IMAGE_PATH + 'end.png')
    finally:
        logger.info("====================================================================")
        logger.info("Script End At : " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        logger.info("====================================================================")
        browser.driver.service.process.send_signal(signal.SIGTERM)
        browser.tear_down()



