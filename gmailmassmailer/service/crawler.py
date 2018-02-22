import logging
from time import sleep
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import csv
import os
import logging.handlers
from logging import Logger
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir) 
from model.dao import error


#start_url = 'https://mail.google.com'
start_url = 'http://139.59.4.7:8080/settings/'
LOG_PATH = os.path.abspath('./logs')
LOG_PATH = LOG_PATH + "/"

class Gmail:

    def __init__(self):

        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--no-sandbox')
        options.add_argument("--test-type")
        options.add_argument("--window-size=1420,780")
        self.driver = webdriver.Chrome(chrome_options=options)
        # self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(5)  # seconds
        self.accounts={}
        self.recipients=[]
    
    def login_to_gmail(self, user_name, password):
        from __builtin__ import str
        log_in_susccesful=False
        try:
            self.driver.save_screenshot(LOG_PATH +user_name +'_login_username.png')
            logger.info('logging in to gmail')
            self.driver.find_element_by_xpath('//input[@name="identifier"]').send_keys(user_name)
            self.driver.execute_script(" document.querySelector('div[id=\"identifierNext\"]').click(); ")
            sleep(5)
            self.driver.save_screenshot(LOG_PATH +user_name +'_login_password.png')
            self.driver.find_element_by_xpath('//*[@id="password"]/div[1]/div/div[1]/input').send_keys(password)
            self.driver.find_element_by_xpath('//*[@id="passwordNext"]/content/span').click()
            sleep(5)
            log_in_susccesful=True
        except Exception,e:
            logger.error(e)       
            self.driver.save_screenshot(LOG_PATH +user_name +'_login_error.png')
            error_msg='Could not log in to gmail for account user: {} password: {}'.format(user_name,password)
            error_msg=error_msg+' please see error image at {}'.format(LOG_PATH +user_name +'_login_error.png')
            logger.error(error_msg)
            err=error()
            err.save_error(error_msg+'\n'+str(e))
        self.driver.save_screenshot(LOG_PATH +user_name + '_login.png')
        return log_in_susccesful
        
        
    def open_url(self, url):
        self.driver.get(url)

        
        
    def parse_page(self, web_page=None):
            try:
                logger.info("Parsing category menu")
                category_list = WebDriverWait(self.driver, 100).until(lambda x: x.find_elements_by_css_selector("div.wn-Classification"))
                for menu in category_list:
                    if(menu.text == 'Soccer'):
                        sleep(5)
                        menu.click()
                        break
                elite_euro_list = WebDriverWait(self.driver, 100).until(lambda x: x.find_elements_by_css_selector("div.sm-CouponLink div.sm-CouponLink_Label "))
                for elem in elite_euro_list:
                    if(elem.text == 'Elite Euro List'):
                        sleep(5)
                        elem.click()
                        break
                with open("persons.csv", "wb") as csvfile:
                    filewriter = csv.writer(csvfile, delimiter=',',
                                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    filewriter.writerow(['Name', 'Profession'])
                    filewriter.writerow(['Derek', 'Software Developer'])
                    filewriter.writerow(['Steve', 'Software Developer'])
                    filewriter.writerow(['Paul', 'Manager'])
                    print('File writting done')
            except Exception, e:
                logger.info(e)
    
    
    def logout_to_gmail(self):
        pass
    
    
    def send_mail(self,recipients,username,password):
        self.open_url(start_url)
        sleep(5)
        retry_count=1
        for retry in range(retry_count):
            log_in_susccesful=self.login_to_gmail(username,password)  #####change how we check success
            if log_in_susccesful:
                break
            self.tear_down()
            sleep(15)
            self.open_url(start_url)
            sleep(5)
            self.login_to_gmail(username,password)
        
        
    def read_accounts_list(self,account_list):
        try:                
            with open(account_list) as csvfile:
                readCSV = csv.reader(csvfile)
                for row in readCSV:
                    print(row[0] +' '+row[1])
            self.accounts[row[0]]=row[1]
            self.recipients=[]
        except Exception,e:
            err=error()
            err.save_error('Failed to read accounts list file \n'+str(e))
    
    
    def read_recepients_list(self,recipients_list):
        try:                
            with open(recipients_list) as csvfile:
                readCSV = csv.reader(csvfile)
                for row in readCSV:
                    self.recipients.append(row[0])
        except Exception,e:
            logger.error('Failed to read recipients list file {}')
            Logger.error(e)
            err=error()
            err.save_error('Failed to read recipients list file \n'+str(e))
        
        
    def tear_down(self):
        logger.info("terminating gmailmassmailer crawler, shutting down web driver")
        self.driver.quit()


if __name__ == "__main__":
    
    if not os.path.isdir(LOG_PATH):
        try:
            os.mkdir(LOG_PATH)                
        
        except Exception, e:
            pass
    
    log_file = "gmailmailer.log"
    full_pth = os.path.join(LOG_PATH, log_file)
    logger = logging.getLogger("GmailMassMailer")
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.setLevel(logging.DEBUG)
    
    gmail = Gmail()

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
            
        logger.info("Crawler started")  
        gmail.driver.save_screenshot(LOG_PATH + 'end.png')
        sleep(120)
    except Exception as e:
        logger.error(e)
        logger.error(e, exc_info=True)
    finally:
        gmail.tear_down()
        
        
