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
from model.dto import single_campaign
from model.dto import multi_campaign

#start_url = 'https://mail.google.com'
start_url = 'http://139.59.4.7:8080/settings/'
LOG_PATH = os.path.abspath('./logs')
LOG_PATH = LOG_PATH + "/"

logger = logging.getLogger("GmailMassMailer")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger.setLevel(logging.DEBUG)

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
    
    
    def logout_to_gmail(self):
        pass
    
    
    def _send(self,mail):
        recipients_list=mail.recipients_list
        user_name=mail.user_name
        password=mail.password
        message=mail.message
        
        self.open_url(start_url)
        sleep(5)
        retry_count=1
        for retry in range(retry_count):
            log_in_susccesful=self.login_to_gmail(user_name,password)  #####change how we check success
            if log_in_susccesful:
                break
            self.tear_down()
            sleep(15)
            self.open_url(start_url)
            sleep(5)
            self.login_to_gmail(user_name,password)
        
        
    def send_mail(self,recipients_list, account_list, account_threashhold):
        slicer=mails_slicer()
        slicer.slice(recipients_list, account_list, account_threashhold)
        while slicer.pending_mails:
            mail=slicer.get_next_campaign()
            self._send(mail)
        
        
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
    
    
class mails_slicer:

    def __init__(self,accounts_list):
        self.accounts_list
        self.pending_recipients_list=[]
        self.acounts_list_to_use=[]
        self.pending_mails=False
        self.account_threashhold=1
        self.campaingn_to_use

    def _allocate_recipients_to_account(self,account_list,account_threashhold,recipients_list):
        '''
            allocates each account recipients for mail with each account allocated a maximum recipients - account_threashhold
        '''
        campaingn_to_use={}
        for account in account_list:
            campaingn_to_use[account]=recipients_list[-account_threashhold:]
            recipients_list=recipients_list[:-account_threashhold]
        self.pending_recipients_list=recipients_list
        return campaingn_to_use
        
    
    def slice(self,recipients_list,account_list,account_threashhold):
        '''
            custom mail slicing algorihtm
        '''
        R=len(recipients_list)
        A=len(account_list)
        M=account_threashhold
        self.account_threashhold=account_threashhold
        
        RA=R/A #recipeients per account
        
        if RA>M:
            XD=(RA-M)*A # XD is number of total recipients that will be pushed to pending  list
            if XD>M:
                self.campaingn_to_use=self._allocate_recipients_to_account(account_list,account_threashhold,recipients_list)
                self.pending_mails=True
                # allocate accounts max no(M) equally and mark not finished 
                # send() -  emails
            elif XD<=M:
                if len(self.accounts_list)-len(self.acounts_list_to_use) > 0:
                    for acc in self.accounts_list:
                        if acc not in self.acounts_list_to_use:
                            self.acounts_list_to_use.append(acc)
                            break
                    self.campaingn_to_use=self._allocate_recipients_to_account(account_list,account_threashhold,self.acounts_list_to_use)
                    return self.campaingn_to_use
                    # allocate remaining recipeints
                    #send()  - emails
                else:
                    self.campaingn_to_use=self._allocate_recipients_to_account(account_list,account_threashhold,recipients_list)
                    self.pending_mails=True
                    # allocate accounts max no(M) equally and mark not finished
                    #send()  - emails
        if RA<=M:
            if len(self.acounts_list_to_use) != 1:
                self.acounts_list_to_use=self.acounts_list_to_use[:len(self.acounts_list_to_use)-1]
                self.slice(recipients_list,self.acounts_list_to_use,account_threashhold)
                #  recurse - recusrion
                # can
            else:
                self.campaingn_to_use=self._allocate_recipients_to_account(account_list,account_threashhold,recipients_list)
                return self.campaingn_to_use
                #send()
                
    def get_next_campaign(self):
        self.slice(self.pending_recipients_list, self.acounts_list_to_use, self.account_threashhold)
        return self.campaingn_to_use


def start_campaign(recipients_list, account_list, account_threashhold):
    
    if not os.path.isdir(LOG_PATH):
        try:
            os.mkdir(LOG_PATH)                
        
        except Exception, e:
            pass
    
    log_file = "gmailmailer.log"
    full_pth = os.path.join(LOG_PATH, log_file)
    
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
        gmail = Gmail()
        gmail.send_mail(recipients_list, account_list, account_threashhold)
        
        gmail.driver.save_screenshot(LOG_PATH + 'end.png')
        sleep(120)
    except Exception as e:
        logger.error(e)
        logger.error(e, exc_info=True)
    finally:
        gmail.tear_down()
        
        
