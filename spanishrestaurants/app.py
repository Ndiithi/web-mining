# -*- coding: utf-8 -*-
import sys
from datetime import datetime
import os
import signal
from selenium.webdriver.support.ui import WebDriverWait
import csv
import io
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from time import sleep
import logging

IMAGE_PATH = os.path.abspath('./images')
IMAGE_PATH = IMAGE_PATH + "/"

LOG_PATH = os.path.abspath('./logs')
LOG_PATH = LOG_PATH + "/"

break_all_count = 0
break_all = False
initial_req = True
max_scroll_page = None


class BrowserAutomation(object):

    def __init__(self):

        if not os.path.isfile("urltext.txt"):
            logger.error("'Search text' or url text file missing")
            sys.exit()
        else:

            f = io.open('urltext.txt', 'r', encoding="utf-8")
            self.start_url = f.readlines()
            
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--no-sandbox')
        options.add_argument("--test-type")
        options.add_argument("--window-size=1420,780")
        
        driver = webdriver.Chrome(chrome_options=options)
        global IMAGE_PATH 
        global count
        self.driver = driver  
        self.driver.implicitly_wait(5)  

    def read_scrap_position(self):
    # open position file if exists else create        
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
    
    def launch_browser(self, start_url):
        logger.info('Launching Browser')
        self.driver.get(start_url)
        sleep(5)
        self.driver.save_screenshot(IMAGE_PATH + 'mainScreen.png')
        logger.info("Browser launch successfully.")
    
    def scrap_item_details(self, current_win_handle):
        logger.info('Scraping item details')
        all_win_handles = self.driver.window_handles
        try:
            for win_handle in all_win_handles:
                if  win_handle != current_win_handle:
                    logger.info('switching window handle')
                    self.driver.switch_to.window(win_handle)
                    sleep(7)
                    logger.info('collecting item details')
                    name = ''
                    phone = ''
                    street = ''
                    locality = ''
                    country = ''
                    email = ''
                    
                    try:
                        name = WebDriverWait(self.driver, 10).until(lambda x: x.find_element_by_css_selector('h1#HEADING.heading_title'))
                        name = name.text
                        name = name.encode('latin-1')
                    except Exception, e:
                        pass
                    
                    try:
                        phone = WebDriverWait(self.driver, 10).until(lambda x: x.find_element_by_css_selector('div.phone.directContactInfo span:nth-child(2)'))
                        phone = phone.text  
                        phone = phone.encode('latin-1')
                    except Exception, e:
                        pass
                    
                    try:
                        email = WebDriverWait(self.driver, 10).until(lambda x: x.find_element_by_css_selector('div.details_tab div.additional_info div.content ul.detailsContent li a'))
                        email = email.get_attribute("href").encode('utf-8').replace('mailto:', '')
                        email = email.encode('latin-1')
                    except Exception, e:
                        pass
                    
                    try:
                        street = WebDriverWait(self.driver, 10).until(lambda x: x.find_elements_by_css_selector('div.address span.street-address'))
                        street = street[0].text.encode('latin-1')
                    except Exception, e:
                        pass
                    
                    try:
                        locality = WebDriverWait(self.driver, 10).until(lambda x: x.find_elements_by_css_selector('div.address span.locality'))
                        locality = locality[0].text.encode('latin-1')
                    except Exception, e:
                        pass
                    
                    try:
                        country = WebDriverWait(self.driver, 10).until(lambda x: x.find_elements_by_css_selector('div.address span.country-name'))
                        country = country[0].text.encode('latin-1')
                    except Exception, e:
                        pass
                    
                    address = '{},{}{}'.format(street, locality, country)

            file_name = 'restaurants'
            file_exists = os.path.isfile(file_name + '.csv')
            if os.name == 'nt':
                _binary = 'b'
            else:
                _binary = ''
                
            logger.info('Saving item details')
            with open(file_name + '.csv', 'a' + _binary) as csvfile:
                address = address.strip()
                logger.info('Saving item name: {} {} {} {}'.format(name, email, address, phone))
                filewriter = csv.writer(csvfile)
                if not file_exists:
                    filewriter.writerow(['Date', 'Name', 'Email', 'Address', 'Phone'])
                if len(name.strip()) != 0 and len(address.strip()) != 0:
                    dt = datetime.now().strftime('%Y-%m-%d')
                    filewriter.writerow([dt, name, email, address, phone])
                    logger.info('Item was saved')
                else:
                    logger.info('Item was not saved')
                logger.info('------------------==================--------------------')
        except Exception, e:
            logger.error(e, exc_info=True)
                   
        finally:        
            if self.driver.current_window_handle != current_win_handle:
                self.driver.close()  
                self.driver.switch_to.window(current_win_handle)
                
    def _parse(self, item_position, cur_page):    
        logger.info('looking for list item')
        listings = WebDriverWait(self.driver, 10).until(lambda x: x.find_elements_by_css_selector('div.listing div div.shortSellDetails div.title a.property_title'))
        logger.info('looking for list item done')
        current_win_handle = self.driver.current_window_handle
        for index, listing in enumerate(listings):
            logger.info('stats, item on loop {}, item to scrap {}'.format(index, item_position))
            if(index != int(item_position)):
                logger.info('skip to item to scrap')
                continue
            try:
                logger.info('Opening listing Number: -->')
                logger.info(item_position)
                # listing.click()
                self.driver.execute_script("$(arguments[0]).click();", listing)
                sleep(9)
                self.scrap_item_details(current_win_handle)
                
                sleep(7)
                self.read_scrap_position()
                cont_position = self.last_position.split(';')
                cur_search_string = cont_position[0]
                cur_page = cont_position[1]
                cur_listing_pos = int(cont_position[2]) + 1
                item_position = cur_listing_pos
                self.save_update_scrap_position(str(cur_search_string), str(cur_page), str(cur_listing_pos))
            # retry searching and click again
            except Exception, e:
                logger.error(e)
                try:
                    logger.error('Failed to click item')
                    logger.error('Retrying search & click item')
                    l = WebDriverWait(self.driver, 10).until(lambda x: x.find_elements_by_css_selector('div.listing div div.shortSellDetails div.title a.property_title'))
                    # l[index].click()
                    self.driver.execute_script("$(arguments[0]).click();", l[index])
                    sleep(9)
                    self.scrap_item_details(current_win_handle)
                    sleep(7)
                    
                    self.read_scrap_position()
                    cont_position = self.last_position.split(';')
                    cur_search_string = cont_position[0]
                    cur_page = cont_position[1]
                    cur_listing_pos = int(cont_position[2]) + 1
                    item_position = cur_listing_pos
                    self.save_update_scrap_position(str(cur_search_string), str(cur_page), str(cur_listing_pos))
                except Exception, e:
                    # break all to refresh listing after failed click, max set to 1 (break_all_count==1)
                    cont_position = self.last_position.split(';')
                    cur_search_string = cont_position[0]
                    cur_page = cont_position[1]
                    cur_listing_pos = int(cont_position[2]) + 1
                    item_position = cur_listing_pos
                    self.save_update_scrap_position(str(cur_search_string), str(cur_page), str(cur_listing_pos))
                    break_all_count = 0
                    
        cont_position = self.last_position.split(';')
        cur_search_string = cont_position[0]
        cur_page = cont_position[1]
        cur_listing_pos = 0
        self.save_update_scrap_position(str(cur_search_string), str(cur_page), str(cur_listing_pos))
    
    def get_page_to_scrap(self, max_scroll_page, cur_page):
        continue_next_page = True
        # if index > int(page_link.get_attribute("data-page")) or 
        logger.info('Maximum scroll page {}'.format(max_scroll_page))
        if(max_scroll_page is not None):
            if int(cur_page) > int(max_scroll_page):
                logger.info('maximum page scroll reached')
                continue_next_page = False
                self.read_scrap_position()
                cont_position = self.last_position.split(';')
                cur_search_string = cont_position[0]
                cur_page = 1
                cur_listing_pos = 0
                self.save_update_scrap_position(str(cur_search_string), str(cur_page), str(cur_listing_pos))
                logger.info('updating position done')
                return continue_next_page
        logger.info('looking for start position')
        
        while True:
            sleep(6)
            logger.info('looking for pagination')
            current_selected_page = WebDriverWait(self.driver, 10).until(lambda x: x.find_element_by_css_selector('div.unified.pagination div.pageNumbers span.current'))
            pagination_pages = WebDriverWait(self.driver, 10).until(lambda x: x.find_elements_by_css_selector('div.unified.pagination div.pageNumbers a.pageNum'))
            logger.info('looking for pagination done')
            for indx, page_link in enumerate(pagination_pages):
                logger.info('page link {}'.format(page_link.get_attribute("data-page-number")))
                last_page = int(pagination_pages[len(pagination_pages) - 1].get_attribute("data-page-number"))
                
                if  int(current_selected_page.text) == int(cur_page):
                    return continue_next_page
                
                if(int(cur_page) > last_page):
                    continue_next_page = False
                    logger.info('updating position')
                    self.read_scrap_position()
                    cont_position = self.last_position.split(';')
                    cur_search_string = cont_position[0]
                    cur_page = 1
                    cur_listing_pos = 0
                    self.save_update_scrap_position(str(cur_search_string), str(cur_page), str(cur_listing_pos))
                    logger.info('updating position done')
                    return continue_next_page
                
                if(int(page_link.get_attribute("data-page-number")) == int(cur_page)):
                    sleep(5)
                    try:
                        # page_link.click()
                        self.driver.execute_script("$(arguments[0]).click();", page_link)
                    except Exception, e:
                        try:
                            pagination_pags = WebDriverWait(self.driver, 10).until(lambda x: x.find_elements_by_css_selector('div.unified.pagination div.pageNumbers a.pageNum'))
                            # pagination_pags[indx].click()
                            self.driver.execute_script("$(arguments[0]).click();", pagination_pags[indx])
                        except Exception, e:
                            logger.info('Last click page link retry')
                            sleep(3)
                            if(int(cur_page) != last_page):
                                pagination_pags = WebDriverWait(self.driver, 10).until(lambda x: x.find_elements_by_css_selector('div.unified.pagination div.pageNumbers a.pageNum'))
                                # pagination_pags[indx + 1].click()
                                self.driver.execute_script("$(arguments[0]).click();", pagination_pags[indx + 1])
                                cur_page = cur_page + 1
                                cont_position = self.last_position.split(';')
                                cur_search_string = cont_position[0]
                                cur_listing_pos = cont_position[2]
                                self.save_update_scrap_position(str(cur_search_string), str(cur_page), str(cur_listing_pos))
                                        
                    logger.info('starting at page {}'.format(cur_page))
                    sleep(6)
                    return continue_next_page
                
            sleep(4)
            # this section is only reached if pagination being searched is not found in first pagination selector
            try:
                logger.info("clicking pagination number {}".format(pagination_pages[len(pagination_pages) - 2].get_attribute("data-page-number")))
                self.driver.execute_script("$(arguments[0]).click();", pagination_pages[len(pagination_pages) - 2])
                # pagination_pages[len(pagination_pages) - 2].click()
            except Exception, e:
                sleep(5)
                paginatn_pages = WebDriverWait(self.driver, 10).until(lambda x: x.find_elements_by_css_selector('div.unified.pagination div.pageNumbers a.pageNum'))
                sleep(3)
                self.driver.execute_script("$(arguments[0]).click();", paginatn_pages[len(paginatn_pages) - 2])
                # paginatn_pages[len(paginatn_pages) - 2].click()
            sleep(7)
        return continue_next_page
    
    def parse_document(self, max_scroll_page=None):
        max_scroll_page = max_scroll_page
        sleep(7)
        order_by_availability_tab = WebDriverWait(self.driver, 10).until(lambda x: x.find_element_by_css_selector('li#availability.ui_tab.availability'))
        self.driver.execute_script("$(arguments[0]).click();", order_by_availability_tab)
        sleep(3)
        # order_by_availability_tab.click()
        # search_text = search_text.encode('utf-8').strip()
        self.read_scrap_position()
        if(len(self.last_position) == 0):
            cur_page = 1
            cur_listing_pos = 0
        else:
            cont_position = self.last_position.split(';')
            cur_page = cont_position[1]
            cur_listing_pos = cont_position[2]

        while True:
            continue_next_page = True
            continue_next_page = self.get_page_to_scrap(max_scroll_page, cur_page)
            if(continue_next_page):
                sleep(7)
                self.read_scrap_position()
                cont_position = self.last_position.split(';')
                cur_page = cont_position[1]
                cur_listing_pos = cont_position[2]
                
                self._parse(cur_listing_pos, cur_page)
                
                logger.info('Parsing page')
                logger.info('updating position')
                self.read_scrap_position()
                cont_position = self.last_position.split(';')
                cur_search_string = cont_position[0]
                cur_page = int(cont_position[1]) + 1
                cur_listing_pos = cont_position[2]
                self.save_update_scrap_position(str(cur_search_string), str(cur_page), str(cur_listing_pos))

            else:
                break
            
        cont_position = self.last_position.split(';')            
        cur_search_string = int(cont_position[0]) + 1
        cur_page = 1
        cur_listing_pos = 0
        self.save_update_scrap_position(str(cur_search_string), str(cur_page), str(cur_listing_pos))

    def save_update_scrap_position(self, cur_search_string, cur_page_pos, cur_item_pos):
        logger.info('updating position')
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
            # os.system("pkill geckodriver") #if usign fire fox, change accordingly
        except WebDriverException, e:
            pass
    
    def reset_position(self):
        position = open("position.txt", 'w')
        position.write('0;1;0')
        position.close()
    
    def run_automation(self, max_scroll_page=None):
        start_url = self.start_url[0]
        start_url = start_url.encode('utf-8')
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
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename=full_pth,
                    filemode='w')
    logger = logging.getLogger("scraper")
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.setLevel(logging.DEBUG)
    
    browser = BrowserAutomation()

    try:

        if os.path.isdir(LOG_PATH):

            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(formatter)
            logger.addHandler(ch)

        else:

            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(formatter)
            logger.addHandler(ch)
            
        logger.info("====================================================================")
        logger.info("Script Started At : " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        logger.info("====================================================================")

        try: 
            max_scroll_page = sys.argv[1]
        except IndexError:
            pass
        
        # start scraping
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

