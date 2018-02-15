'''
Created on Feb 10, 2018

@author: duncan
'''

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import base64
import time
import sys
from selenium.webdriver.common.by import By
from datetime import datetime
from json import dumps
from selenium.webdriver.common.keys import Keys
import os
import random
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import user
from numpy import genfromtxt
import signal
import re
from selenium.webdriver.support.ui import WebDriverWait
from passlib.utils import sys_bits
import csv
import urllib
import io

IMAGE_PATH = os.path.abspath('./images')
IMAGE_PATH = IMAGE_PATH + "/"

print IMAGE_PATH
count = 0


class BrowserAutomation(object):
    """
    Instantiate a BrowserAutomation
    """
    def __init__(self):
        """
        Constructor for BrowserAutomation class
        """
        
        service_args = [
            '--ssl-protocol=any',
            '--ignore-ssl-errors=true'
        ]
        # "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/8.0.7 Safari/600.7.12"
        capabilities = DesiredCapabilities.PHANTOMJS
        capabilities["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/8.0.7 Safari/600.7.12"
        )    
        
        if not os.path.isfile("searchtext.txt") or not os.path.isfile("submittext.txt"):
            print "'Search text' or 'submit text' file does not exist" 
            sys.exit()
        else:
       
            f = io.open('searchtext.txt', 'r', encoding="latin-1")
            self.search_texts = f.readlines()
            
            f = io.open('submittext.txt', 'r', encoding="latin-1")
            qst_text = f.readlines()
            self.question_text = qst_text[0]
                
        try:
            position = open("position.txt", 'r')
            self.last_position = position.readline()
            self.last_position = self.last_position.strip()
        except IOError:
            position = open("position.txt", 'w')
            position.write('0;1;0')
            position.close()
            position = open("position.txt", 'r')
            self.last_position = position.readline()
            self.last_position = self.last_position.strip()
            position.close()
            
        options = webdriver.ChromeOptions()
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


    def launch_browser(self):
        print 'Launching Browser'
        self.driver.get("https://www.gmail.com")
        time.sleep(5)
        self.driver.save_screenshot(IMAGE_PATH + 'mainScreen.png')
        print "Browser launch successfully."


    def login_to_gmail(self, user_name, password):
        print 'Search shopping'
        self.driver.find_element_by_xpath('//input[@name="identifier"]').send_keys(user_name)
        ele = self.driver.find_element_by_xpath('//*[@id="identifierNext"]/content/span')
        self.driver.execute_script(" document.querySelector('div[id=\"identifierNext\"]').click(); ")
        time.sleep(5)
        self.driver.save_screenshot(IMAGE_PATH + 'first.png')
        self.driver.find_element_by_xpath('//*[@id="password"]/div[1]/div/div[1]/input').send_keys(password)
        self.driver.find_element_by_xpath('//*[@id="passwordNext"]/content/span').click()
        time.sleep(5)
        
        self.driver.save_screenshot(IMAGE_PATH + 'login.png')


    def send_review(self, max_scroll_page=None):
        from time import sleep
        break_all_count = 0
        max_scroll_page = max_scroll_page
        sleep(3)
        cont = True
        # for index,search_text in enumerate(self.search_texts):
        srch_index = 0
        submit_text_len = len(self.search_texts)
        initial_req = True
        
        # for each search term loop
        while cont: 
            search_text = self.search_texts[srch_index]
            search_text = search_text.encode('utf-8')
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
            print 'current search term --->'
            print search_text
            # find search input 
            
            start_url = 'https://www.google.com/search?'
            _search_term = {'q':search_text}
            srch = urllib.urlencode(_search_term)
            start_url = start_url + '&' + srch
            self.driver.get(start_url)
            time.sleep(7)
            # Retry opening places page if first attemp fails
            retry_places_open = 1
            for retry in range(retry_places_open):
                try:
                    places_page = self.driver.find_element_by_css_selector('#rso > div:nth-child(1) > div > div > div > div > div > a')
                    places_page.click()
                    break
                except Exception:
                    print 'Could not open places page'
                    sleep(3)
            time.sleep(7)
            search_elem = self.driver.find_element_by_xpath('//input[@id="lst-ib"]')
            search_elem.clear()
            search_elem.send_keys(search_text)
            sleep(7)
            
            
            print 'looking for pagination'
            pagination_pages = self.driver.find_elements_by_css_selector('#nav > tbody:nth-child(1) > tr:nth-child(1) > td')
            sleep(9)
            print 'looking for pagination done'
            break_all = False
            for index, page_link in enumerate(pagination_pages):
                if index > int(max_scroll_page) or int(cur_page) > int(max_scroll_page):
                    print cur_page > int(max_scroll_page)
                    print 'XX'
                    print index > int(max_scroll_page)
                    print 'index {}'.format(index)
                    print 'max_scroll_page {}'.format(max_scroll_page)
                    print 'cur_page {}'.format(cur_page)
                    break
                if index != int(cur_page):
                    continue
                try:
                    # avoid clicking on first pagination link (no. 1) as is the default selected on initial browser boot
                    if initial_req and int(cur_page) == 1:
                        initial_req = False
                        pass
                    else:
                        page_link.find_element_by_css_selector('a').click()
                        sleep(7)
                # Retry search and clicking item in pagination before doing a refresh
                except Exception, e:
                    try:
                        print 'Retry looking for pagination'
                        p = self.driver.find_elements_by_css_selector('#nav > tbody:nth-child(1) > tr:nth-child(1) > td')                    
                        p[index].find_element_by_css_selector('a').click()
                        sleep(7)                
                    except Exception, e:
                        # else break all loops and refresh page
                        break_all = True
                        sleep(7)
                        break
                        
                # get all items list after search
                print 'looking for list item'
                listings = WebDriverWait(self.driver, 10).until(lambda x: x.find_elements_by_css_selector('div.rlfl__tls div div div div  a:nth-child(1)'))
                print 'looking for list item done'
                for index, listing in enumerate(listings):
                    print 'stats, item on loop {}, item to scrap {}'.format(index, cur_listing_pos)
                    if(index != int(cur_listing_pos)):
                        print 'loop to item to scrap'
                        continue
                    try:
                        print 'Opening listing Number: -->'
                        print cur_listing_pos
                        if "http" in listing.get_attribute("href"):
                            cont_position = self.last_position.split(';')
                            cur_search_string = cont_position[0]
                            cur_page = cont_position[1]
                            cur_listing_pos = int(cont_position[2]) + 1
                            self.save_update_scrap_position(str(cur_search_string), str(cur_page), str(cur_listing_pos))
                            continue
                        listing.click()
                        sleep(7)
                    # retry searching and click again
                    except Exception, e:
                        try:
                            print 'Failed to click item'
                            print 'Retrying search & click item'
                            l = WebDriverWait(self.driver, 10).until(lambda x: x.find_elements_by_css_selector('div.rlfl__tls div div div div  a:nth-child(1)'))
                            l[index].click()
                            sleep(7)
                        except Exception, e:
                            # break all to refresh listing after failed click, max set to 1 (break_all_count==1)
                            break_all = True
                            if int(cur_page) == 1:
                                initial_req = True
                            # if true skip current listing
                            if break_all_count == 1:
                                cont_position = self.last_position.split(';')
                                cur_search_string = cont_position[0]
                                cur_page = cont_position[1]
                                cur_listing_pos = int(cont_position[2]) + 1
                                self.save_update_scrap_position(str(cur_search_string), str(cur_page), str(cur_listing_pos))
                                break_all_count = 0
                            else:
                                break_all_count = break_all_count + 1
                            break
                        
                    # collect name and address and submit question
                    #--------------------------------------------
                    name = ''
                    address = ''
                    asked_qstn = False
                    try:
                        # retry fetch name once if first attempt fails.(it occurs)
                        retry_name_fetch = 1
                        for x in range(retry_name_fetch):
                            try:
                                print 'looking for name'
                                name = self.driver.find_element_by_css_selector('.kno-ecr-pt > span:nth-child(1)').text
                                print 'found name as: {}'.format(name)
                                break
                            except Exception:
                                sleep(2)
                                pass
                        try:
                            print 'looking for address'
                            address = self.driver.find_element_by_css_selector('.kp-header + div > div > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > span:nth-child(2)').text
                        except Exception:
                            try:
                                address = self.driver.find_element_by_css_selector('.kp-header + div > div > div:nth-child(3) > div:nth-child(1) > div:nth-child(1) > span:nth-child(2)').text
                            except Exception:
                                address = self.driver.find_element_by_css_selector('.kp-header + div + div > div > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > span:nth-child(2)').text
                        print 'found address as: {}'.format(address)
                    except Exception, e:
                        print ''      
                    sleep(4)
                    print "Number of open windows : " + str(len(self.driver.window_handles))
                    if len(name) != 0 and len(address) != 0:
                        try:
                            print('Switching window handle')
                            self.driver.switch_to_window(self.driver.window_handles[0])
                            time.sleep(10)
                            # click question button
                            self.driver.find_element_by_css_selector('._Luu > a:nth-child(1)').click()
                            time.sleep(4)
                            # (put question in opened dialog box in the text area)
                            self.driver.find_element_by_xpath('//div[@id="pqaWqD"]/div/div/div/div[2]/div[2]/div[1]/textarea').send_keys(self.question_text)
                            time.sleep(7)
                            self.driver.save_screenshot(IMAGE_PATH + 'review.png')
                            self.driver.find_element_by_xpath('//*[@id="pqaWqD"]/div/div/div/div[2]/div[8]/span[1]/a').click()
                            asked_qstn = True
                            time.sleep(5)
                            # self.driver.switch_to_window(self.driver.window_handles[0])
                            print('Exiting success window')
                            ActionChains(self.driver).move_by_offset(100, 100).click().perform()
                            # WebDriverWait(self.driver, 15).until(lambda x: x.find_element_by_css_selector('._Khg')).click()
                            self.driver.switch_to_window(self.driver.window_handles[0])  
                        except Exception, e:
                            print ''
                    
                    cont_position = self.last_position.split(';')
                    cur_search_string = cont_position[0]
                    cur_page = cont_position[1]
                    cur_listing_pos = int(cont_position[2]) + 1
                    self.save_update_scrap_position(str(cur_search_string), str(cur_page), str(cur_listing_pos))
                    self.save_item_details(search_text, name, address, asked_qstn)
                    
                if break_all:
                    break
                
                cont_position = self.last_position.split(';')
                cur_search_string = cont_position[0]
                cur_page = int(cont_position[1]) + 1
                cur_listing_pos = 0
                self.save_update_scrap_position(str(cur_search_string), str(cur_page), str(cur_listing_pos))

                
            if not break_all:
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
        
    def safeStr(self, obj):
        try: 
            return str(obj.encode('utf-8'))
        except UnicodeEncodeError:
            return obj.encode('utf-8', 'ignore').decode('utf-8')
        return obj
    
    
    def reset_position(self):
        position = open("position.txt", 'w')
        position.write('0;1;0')
        position.close()
    
    
    def run_automation(self, user_name, password, max_scroll_page):
        print "============================="
        print "     Starting automation     "
        print "============================="
        self.launch_browser()
        self.login_to_gmail(user_name, password)
        self.send_review(max_scroll_page)
        self.reset_position()


proxy_counter = 0
user_agent_counter = 0

print "===================================================================="
print "Script Started At : " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print "===================================================================="


user_name = ''
password = ''
max_scroll_page = ''
try: 
    user_name = sys.argv[1]    
    password = sys.argv[2]
    max_scroll_page = sys.argv[3]
except IndexError:
    pass

if len(user_name.strip()) == 0 or len(max_scroll_page) == 0:
    print "Usage: pyhton {} [username] [password] [max_scroll_page]".format(sys.argv[0])
    sys.exit()
    
browser = ''
try:
    browser = BrowserAutomation()
    browser.run_automation(user_name, password, max_scroll_page)
    browser.driver.service.process.send_signal(signal.SIGTERM)  # kill the specific phantomjs child proc
    browser.driver.quit()  # quit the node proc
except Exception as e:
    print "Error occured "
    print str(e)
    browser.driver.save_screenshot(IMAGE_PATH + 'end.png')
    browser.driver.service.process.send_signal(signal.SIGTERM)  # kill the specific phantomjs child proc
    browser.driver.quit()  # quit the node proc

print "===================================================================="
print "Script End At : " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print "===================================================================="
