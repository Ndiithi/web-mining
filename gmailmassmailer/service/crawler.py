from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import csv
import os
import logging
from model.dto import account
from service import lg
from model.dao import account as account_dao
from model.dao import campaign as campaign_dao
from model.dao import message as message_dao
from model.dto import recipient
from model.dao import recipient as recipient_dao
import sys



logger = logging.getLogger(__name__)

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parentdir) 
from model.dao import error
from model.dto import single_campaign

start_url = 'https://mail.google.com'
# start_url = 'http://139.59.4.7:8080/settings/'
GMAIL_SEND_LIMIT = 500
LOG_PATH = os.path.abspath('./logs')
LOG_PATH = LOG_PATH + "/"


class Gmail:
    
    def __init__(self, verify=False): 
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        if not verify:
            options.add_argument("--headless")
            options.add_argument('--disable-gpu')
        
        options.add_argument("--log-level=3");
        options.add_argument("--silent");
        options.add_argument('--no-sandbox')
        options.add_argument("--test-type")
        options.add_argument("--window-size=1420,780")
        self.driver = webdriver.Chrome(chrome_options=options)
        # self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(5)  # seconds
        self.accounts = {}
        self.recipients = []
        self.send_count = 1
    
    
    def check_if_there_exists_pending_verification_accounts(self):
        logger.info('Checking if exists accounts marked pending verification')
        acc_dao=account_dao()
        accounts_list=acc_dao.select(self.campaign_id)
        list_of_names_to_verify=[]
        try:
            slicer=self.slicer
            for inx in range(len(slicer.accounts_list)):
                for acc_lst in accounts_list:
                    if acc_lst.user_name==slicer.accounts_list[inx].user_name  and  acc_lst.password == slicer.accounts_list[inx].password:
                        if acc_lst.verify==1:
                            list_of_names_to_verify.append(acc_lst.user_name)
            return list_of_names_to_verify
        except Exception:
            return list_of_names_to_verify
    
    
    def fix_unusable_accounts(self):
        acc_dao=account_dao()
        logger.debug('Fix accounts campaignid {}'.format(self.campaign_id))
        accounts_list=acc_dao.select(self.campaign_id)
        fixed=False
        try:
            slicer=self.slicer
            for inx in range(len(slicer.accounts_list)):
                for acc_lst in accounts_list:
                    if acc_lst.user_name==slicer.accounts_list[inx].user_name  and  acc_lst.password == slicer.accounts_list[inx].password:
                        if acc_lst.verify==0 and slicer.accounts_list[inx].verify==1:
                            logger.info('found account(s) to be fixed, fixing..')
                            acct=slicer.accounts_list[inx]
                            acct.verify=0
                            slicer.accounts_list[inx]=acct
                            slicer.acounts_list_to_use.append(acct)
                            fixed=True
            return fixed
        except Exception,e:
            logger.debug(e,exc_info=True)
            return fixed
        
                            
        
    def open_compose_mail_page(self, user_name):
        log_in_susccesful = False
        try:
            # url to switch to basic view after login
            logger.info('Switching to basic view')
            self.open_url('https://mail.google.com/mail/u/0/h/1pq68r75kzvdr/?v%3Dlui')
            sleep(15)
            if 'Do you really want to use HTML Gmail' in self.driver.page_source:
                logger.info('Gmail prompted if we want to use basic version, accepting')
                accept_basic_html_btn = WebDriverWait(self.driver, 10).until(lambda x: x.find_element_by_css_selector('#maia-main > form > p > input'))
                accept_basic_html_btn.click()
                sleep(15)
              
            logger.info('Composing mail')    
            self.driver.find_element_by_xpath("//*[contains(text(), 'Compose')]").click()
            log_in_susccesful = True
        except Exception, e:
            logger.debug(e, exc_info=True)       
            self.driver.save_screenshot(LOG_PATH + user_name + 'mail_compose_error.png')
            error_msg = 'Error during mail composition for account user: {}'.format(user_name)
            error_msg = error_msg + ' please see error image at {}'.format(LOG_PATH + user_name + '_after_log_in.png')
            logger.error(error_msg)
            err = error()
            err.save_error(error_msg + '\n' + str(e))
        return log_in_susccesful
        
    
    def save_very_phone_error(self, user_name):     
        error_msg = 'Need to manually verify phone account for user: {}\n'.format(user_name)
        error_msg = error_msg + '''To fix this, please run this gmailer crawler providing only this account 
                                username and password. Run command: gmailer verify {user_name} {password} \n'''
        error_msg = error_msg + ' please see error image at {}'.format(LOG_PATH + user_name + '_after_log_in.png')
        logger.error(error_msg)
        err = error()
        err.save_error(error_msg)
    
    
    def remove_acount_from_usable_list(self, account, slicer):
        try:
            # remove this account from account to use
            for inx in range(len(slicer.acounts_list_to_use)):
                if account == slicer.acounts_list_to_use[inx]:
                    slicer.acounts_list_to_use.remove(account)
            acc_dao=account_dao()
            for inx in range(len(slicer.accounts_list)):
                if account == slicer.accounts_list[inx]:
                    acc=slicer.accounts_list[inx]                
                    acc.verify=1
                    slicer.accounts_list[inx]=acc
                    logger.info('Marking account as to be verified')
                    acc_dao.update_verify(slicer.accounts_list[inx])
        except Exception,e:
            logger.error(e,exc_info=True) 
                
                
    def login_to_gmail(self, account , slicer=None, fix_veryfy=False):
        user_name = account.user_name
        password = account.password
        '''
            fix_veryfy when called with this set true, it opens up the browser to fix googles phone authentication
        '''
        log_in_susccesful = False
        try:
            self.driver.save_screenshot(LOG_PATH + user_name + 'one_account_login_username.png')
            # user name
            self.driver.find_element_by_xpath('//*[@id="Email"]').send_keys(user_name)
            logger.info('logging in to gmail: One account')
            logger.info('sent filled user name')
            # next
            sleep(2)
            
            self.driver.execute_script("document.querySelector('input[id=\"next\"]').click(); ")
            sleep(9)
            # Passwd
            self.driver.save_screenshot(LOG_PATH + user_name + '_login_password.png')
            self.driver.find_element_by_xpath('//input[@name="Passwd"]').send_keys(password)
            
            sleep(2)
            # sign in  signIn
            self.driver.execute_script("document.querySelector('input[id=\"signIn\"]').click(); ")
            sleep(12)
            self.driver.save_screenshot(LOG_PATH + user_name + '_after_log_in.png')
            try:
                img = WebDriverWait(self.driver, 10).until(lambda x: x.find_element_by_css_selector('div img'))
                veryfy_phone_text = img.get_attribute('src')
                # check if the veryfy phone page shows up
                if 'signin_tapyes' in veryfy_phone_text or 'embedded' in veryfy_phone_text:
                    self.save_very_phone_error(user_name)
                    if not fix_veryfy:
                        # remove this account from account to use
                        self.remove_acount_from_usable_list(account, slicer)
                    log_in_susccesful = False
                    if not fix_veryfy:
                        return log_in_susccesful
            except Exception, e:
                
                # logger.error(e, exc_info=True)
                pass
            if not fix_veryfy:
                log_in_susccesful = self.open_compose_mail_page(user_name)
        except Exception:
            try:
                self.driver.save_screenshot(LOG_PATH + user_name + '_login_username.png')
                logger.info('logging in to gmail standard interface')
                self.driver.find_element_by_xpath('//input[@name="identifier"]').send_keys(user_name)
                self.driver.execute_script(" document.querySelector('div[id=\"identifierNext\"]').click(); ")
                sleep(9)
                self.driver.save_screenshot(LOG_PATH + user_name + '_login_password.png')
                self.driver.find_element_by_xpath('//*[@id="password"]/div[1]/div/div[1]/input').send_keys(password)
                self.driver.find_element_by_xpath('//*[@id="passwordNext"]/content/span').click()
                sleep(12)
                try:
                    img = WebDriverWait(self.driver, 10).until(lambda x: x.find_element_by_css_selector('div img'))
                    veryfy_phone_text = img.get_attribute('src')
                    # check if the veryfy phone page shows up
                    if 'signin_tapyes' in veryfy_phone_text or 'embedded' in veryfy_phone_text:
                        self.save_very_phone_error(user_name)
                        if not fix_veryfy:
                            # remove this account from account to use
                            self.remove_acount_from_usable_list(account, slicer)
                            log_in_susccesful = False
                            return log_in_susccesful
                except Exception, e:
                    # logger.error(e, exc_info=True)
                    pass
                if not fix_veryfy:
                    log_in_susccesful = self.open_compose_mail_page(user_name)
            except Exception, e:
                logger.error(e, exc_info=True)       
                self.driver.save_screenshot(LOG_PATH + user_name + '_login_error.png')
                error_msg = 'Could not log in to gmail for account user: {} password: {}'.format(user_name, password)
                error_msg = error_msg + ' please see error image at {}'.format(LOG_PATH + user_name + '_after_log_in.png')
                logger.error(error_msg)
                err = error()
                err.save_error(error_msg + '\n' + str(e))
        self.driver.save_screenshot(LOG_PATH + user_name + '_login.png')
        return log_in_susccesful
        
    def open_url(self, url):
        self.driver.get(url)

    def _send(self, single_campaign, slicer):
        account = single_campaign.account
        recipients_list = single_campaign.recipients_list
        message = single_campaign.message
        user_name = account.user_name
        password = account.password
        subject=single_campaign.subject
        logger.info('Login to gmail for user: {}'.format(user_name))
        self.open_url(start_url)
        sleep(10)
        
        log_in_susccesful = self.login_to_gmail(account, slicer)
        if not log_in_susccesful:
            retry_count = 2
            for retry in range(retry_count):
                logger.info('login not successfull, retry count ={}'.format(retry+1))
                self.tear_down()
                sleep(60)
                self.__init__()
                self.open_url(start_url)
                sleep(13)
                log_in_susccesful = self.login_to_gmail(account, slicer)
                if log_in_susccesful:
                    break
                if retry == 1:
                    logger.error('Unable to sign in for account: {}, removing from list of usable accounts'.format(account.user_name))
                    self.remove_acount_from_usable_list(account, slicer)
        try:
            if  log_in_susccesful:
                sleep(10)
                bcc = ''
                if len(recipients_list) > 1:
                    for x in range(1, len(recipients_list)):
                        if len(bcc) == 0:
                            bcc = bcc + recipients_list[x].email
                        else:
                            bcc = bcc + ',' + recipients_list[x].email
                    WebDriverWait(self.driver, 10).until(lambda x: x.find_element_by_css_selector('input#bcc')).send_keys(bcc)
                sleep(5)
                WebDriverWait(self.driver, 10).until(lambda x: x.find_element_by_css_selector('textarea#to')).send_keys(recipients_list[0].email)
                sleep(5)
                WebDriverWait(self.driver, 10).until(lambda x: x.find_element_by_xpath('//input[@name="subject"]')).send_keys(subject)
                sleep(5)
                WebDriverWait(self.driver, 10).until(lambda x: x.find_element_by_xpath('//textarea[@title="Message Body"]')).send_keys(message)
                sleep(10)
                logger.info('Sending mail') 
                self.driver.execute_script("document.querySelector('input[value=\"Send\"]').click(); ")
    #             self.driver.find_element_by_xpath('//*[@id="password"]/div[1]/div/div[1]/input').send_keys(password)
    #             self.driver.find_element_by_xpath("//input[@value='Send')]").click()
                sleep(20)
                self.driver.find_element_by_xpath("//*[contains(text(), 'Sign out')]").click() 
                sleep(7)
                acc_update = account_dao()
                logger.info('Updating account on total remaining recipients spaces to use')
                for inx in range(len(slicer.acounts_list_to_use)):
                    if account == slicer.acounts_list_to_use[inx]:
                        replace_ment_acc = slicer.acounts_list_to_use[inx]
                        incremented_send_val = slicer.acounts_list_to_use[inx].total_sent + len(recipients_list)  # update the amount of mails an account has sent today
                        replace_ment_acc.total_sent = incremented_send_val
                        acc_update.update(replace_ment_acc)
                        slicer.acounts_list_to_use[inx] = replace_ment_acc
                for inx in range(len(slicer.accounts_list)):
                    if account == slicer.accounts_list[inx]:
                        replace_ment_acc = slicer.accounts_list[inx]
                        incremented_send_val = slicer.accounts_list[inx].total_sent + len(recipients_list)  # update the amount of mails an account has sent today
                        replace_ment_acc.total_sent = incremented_send_val
                        slicer.accounts_list[inx] = replace_ment_acc
                        
                recip_dao = recipient_dao()
                for inx in range(len(recipients_list)):
                    recip_dao.update(recipients_list[inx])  # update that recipient was sent email
            else:
                slicer.pending_mails = True
                for x in range(len(recipients_list)):
                    slicer.pending_recipients_list.append(recipients_list[x])
                # #return recipients to pending queue coz it did not send
                pass
        except Exception, e:    
            self.driver.save_screenshot(LOG_PATH + user_name + 'mail_compose_error.png')
            error_msg = 'Error during mail composition for account user: {}'.format(user_name, password)
            error_msg = error_msg + ' please see error image at {}'.format(LOG_PATH + user_name + '_after_log_in.png')
            logger.error(error_msg, exc_info=True)
            err = error()
            err.save_error(error_msg + '\n' + str(e))
        self.driver.save_screenshot(LOG_PATH + user_name + 'mail_compose.png')
        
    def _loop_send_list(self, accountList_to_recipientsList_map, message, slicer,subject):
        logger.debug("Type of accout_list given {}".format(type(accountList_to_recipientsList_map)))
        logger.info('Extracting account and recipients to send after slicing')
        
        for account, recipient in accountList_to_recipientsList_map.iteritems():
            single_camp = single_campaign(account, recipient, message)
            single_camp.subject=subject
            if self.send_count == 1:  # to close allow to close browser for every mail sent with one account and sleep for 260 secs thereafter
                self._send(single_camp, slicer)
                self.send_count = self.send_count + 1
                logger.info('Tearing down crawler')
                self.tear_down()
                logger.info('crawler sleeping for {} minutes'.format(258 / 60))
                sleep(258)
            else:
                logger.info('Reinitializing sequence, initializing parameters')
                self.__init__()
                sleep(4)
                self._send(single_camp, slicer)
                logger.info('Tearing down crawler')
                self.tear_down()
                self.send_count = self.send_count + 1
                logger.info('crawler sleeping for {} minutes'.format(258 / 60))
                sleep(258)
            self.fix_unusable_accounts() #checks every other time if accounts previously marked as unusable are respolved
            logger.debug('Finished looping on list to send')
            
    def send_mail(self, recipients_list, account_list, account_threashhold, message,subject):
        logger.info('Processing mail slicing')
        self.slicer=mails_slicer(account_list, account_threashhold)
        slicer = self.slicer
        logger.debug('Created mail slicer object')
        accountList_to_recipientsList_map = slicer.slice(recipients_list, account_list)
        logger.debug("The acc-recip_list map has {}".format(accountList_to_recipientsList_map))
        if len(accountList_to_recipientsList_map) != 0:
            logger.info('Sending mail from mail slicer')
            self._loop_send_list(accountList_to_recipientsList_map, message, slicer,subject)
            logger.debug('Return from _loop_send_list method call')
        logger.info('Check if pending mails')
        logger.info('Pending status: {}'.format(slicer.pending_mails))
        while slicer.pending_mails:
            logger.info('Fetching pending mails')
            accountList_to_recipientsList_map = self.slicer.get_next_campaign()
            to_verify_user_name=self.check_if_there_exists_pending_verification_accounts()
            if len(accountList_to_recipientsList_map) == 0 and len(to_verify_user_name)!=0:
                while True:
                    logger.info('The following accounts need to be verified for crawler to proceed')
                    for acc_name in to_verify_user_name:
                            logger.info(acc_name)
                    logger.info('If you do not need to proceed hit "ctrl c" to terminate crawler')
                    fixed=self.fix_unusable_accounts()
                    if fixed: 
                        accountList_to_recipientsList_map = self.slicer.get_next_campaign()
                        break
                    else: 
                        sleep(20)
            elif len(accountList_to_recipientsList_map) == 0:        
                logger.info('All accounts maximum limit reached while unsent mails exist')
                break            
            logger.info('Sending pending mails')
            self._loop_send_list(accountList_to_recipientsList_map, message, slicer,subject)


    def read_accounts_list(self, account_list, campaign_id):
        try:       
            accounts = []
            acc_dao = account_dao()
            with open(account_list) as csvfile:
                readCSV = csv.reader(csvfile)
                for row in readCSV:
                    acc = account(row[0], row[1])
                    acc.campaign_id = campaign_id
                    was_account_save=acc_dao.save(acc)
                    if was_account_save:
                        accounts.append(acc)
            return accounts
        except Exception, e:
            logger.error(e, exc_info=True)
            err = error()
            err.save_error('Failed to read accounts list file \n' + str(e))
    
    def read_recepients_list(self, recipients_list, campaign_id):
        try:     
            recipients = []           
            with open(recipients_list) as csvfile:
                readCSV = csv.reader(csvfile)
                for row in readCSV:
                    rcp = recipient()
                    rcp.campaign_id = campaign_id
                    rcp.email = row[0]
                    rcp_dao = recipient_dao()
                    rcp_dao.save(rcp)
                    recipients.append(rcp)
            return recipients
        except Exception, e:
            logger.error('Failed to read recipients list file {}')
            logger.error(e, exc_info=True)
            err = error()
            err.save_error('Failed to read recipients list file \n' + str(e))

    def tear_down(self):
        logger.info("terminating gmailmassmailer crawler, shutting down web driver")
        self.driver.quit()
    
    
class mails_slicer:

    def __init__(self, accounts_list, account_threashhold):
        mails_slicer.accounts_list = list(accounts_list)
        self.pending_recipients_list = []
        self.acounts_list_to_use = accounts_list
        self.pending_mails = False
        self.account_threashhold = account_threashhold

    def _allocate_recipients_to_account(self, account_list, account_threashhold, recipients_list):
        '''
            allocates each account recipients for mail with each account allocated a maximum recipients - account_threashhold
        '''
        campaingn_to_use = {}
        for account in account_list:
            total_sent = account.total_sent
            logger.info('Total sent for account {} is: {}'.format(account.user_name, total_sent))
            # 500 is gmails fixed recipients per day
            recipients_to_add = GMAIL_SEND_LIMIT - (total_sent + 1)
            logger.info("space remaining for extra recipients {}".format(recipients_to_add))
            if recipients_to_add >= account_threashhold:
                campaingn_to_use[account] = recipients_list[-account_threashhold:]
                recipients_list = recipients_list[:-account_threashhold]
            elif recipients_to_add < account_threashhold and recipients_to_add <= 0:
                campaingn_to_use[account] = recipients_list[-recipients_to_add:]
                recipients_list = recipients_list[:-recipients_to_add]
            else:
                self.acounts_list_to_use.remove(account)
        logger.info('Recipients list length after allocation to accounts {}'.format(len(recipients_list)))
        self.pending_recipients_list = recipients_list
        return campaingn_to_use
    
    def remove_exhausted_accounts(self, acct_list):
        pass
    
    def slice(self, recipients_list, account_list):
        '''
            custom mail slicing algorithm
        '''
        R = len(recipients_list)
        A = len(account_list)
        M = self.account_threashhold
        
        if  A == 0:  # avoid dividing by zero to allow normal flow so as to terminate crawler gracefully
            A = 1
            logger.info('account list is currently empty, check if there are other usable accounts')
            for acc in self.accounts_list:
                if acc.verify==0:
                    account_list.append(acc)
                    A = len(account_list)
            
        
        logger.info('Recipients list length: {}'.format(R))
        logger.info('Accounts list length: {}'.format(A))
        logger.info('Account_threashhold list length: {}'.format(M))
        
        RA = R / A  # recipeients per account
        
        if RA > M:  # if recipient per account greater than account threashhold
            
            XD = (RA - M) * A  # XD is the number  recipients that wount fit in account to be sent thus will be pushed to pending
            if XD > M:
                campaingn_to_use = self._allocate_recipients_to_account(account_list, self.account_threashhold, recipients_list)
                if(len(self.pending_recipients_list) == 0 or len(self.acounts_list_to_use) == 0):
                    self.pending_mails = False
                else:
                    self.pending_mails = True
                return campaingn_to_use
                # allocate accounts max no(M) equally and mark not finished 
                # send() -  emails
            elif XD <= M:
                if len(self.accounts_list)-len(account_list) > 0:
                    logger.info("There exists unused accounts, allocating remaining recipients, send list now empty")
                    for acc in self.accounts_list:
                        if acc not in account_list and acc.verify==0:
                            self.acounts_list_to_use.append(acc)
                            break
                    campaingn_to_use = self._allocate_recipients_to_account(self.acounts_list_to_use, self.account_threashhold, recipients_list)
                    if(len(self.pending_recipients_list) == 0 or len(self.acounts_list_to_use) == 0):
                        self.pending_mails = False
                    else:
                        self.pending_mails = True
                    return campaingn_to_use
                    # check if we have unused account and add to accounts to be used for sending mail  
                    # send()  - emails
                else:
                    logger.info("No unused accounts, allocating & putting remaining in pending list")
                    campaingn_to_use = self._allocate_recipients_to_account(account_list, self.account_threashhold, recipients_list)
                    if(len(self.pending_recipients_list) == 0 or len(self.acounts_list_to_use) == 0):
                        self.pending_mails = False
                    else:
                        self.pending_mails = True
                    return campaingn_to_use
                    # allocate accounts max no(M) equally and mark not finished
                    # send()  - emails
        if RA <= M:
            if len(account_list) != 1 and len(account_list)>0:
                logger.info("Recipients to send can fit in less accounts, splicing account list & Recursing mail sclicer")
                self.acounts_list_to_use = self.acounts_list_to_use[:len(self.acounts_list_to_use) - 1]
                campaingn_to_use = self.slice(recipients_list, self.acounts_list_to_use)
                return campaingn_to_use
                #  recurse - recusrion # if recipients to send is less or equal a singles account threshhold, then strip accounts & remain with one for sending 
                # can
            else:
                logger.info("Recipients to send can fit in accounts, send  list now empty")
                campaingn_to_use = self._allocate_recipients_to_account(account_list, self.account_threashhold, recipients_list)
                if(len(self.pending_recipients_list) == 0 or len(self.acounts_list_to_use) == 0):
                    self.pending_mails = False
                else:
                    self.pending_mails = True

                return campaingn_to_use
                # send()
                
    def get_next_campaign(self):
        campaingn_to_use = self.slice(self.pending_recipients_list, self.acounts_list_to_use)
        return campaingn_to_use



def start_campaign(recipients_list, account_list, account_threashhold, message, subject):
    try:
        logger.info("Crawler started") 
        gmail = Gmail()
        msg = message_dao()
        camp = campaign_dao()
        campaign_id = camp.create_new_campaign()
        msg.save(message[0], campaign_id)
        gmail.campaign_id=campaign_id
        recipients_lt = gmail.read_recepients_list(recipients_list, campaign_id)
        account_lt = gmail.read_accounts_list(account_list, campaign_id)
        gmail.send_mail(recipients_lt, account_lt, account_threashhold, message,subject)
        logger.info('Finished sending all mails, exiting completely')
        sleep(7)
    except Exception,e:
        pass
        logger.debug(e, exc_info=True)
    finally:
        try:
            gmail.tear_down()
        except Exception:
            sys.exit()
        
