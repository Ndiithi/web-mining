from service import lg
from service.crawler import start_campaign
from service.crawler import start_url
from  service.crawler import Gmail
import io
from model.dto import account
from model.dao import account as account_dto

class controller:
    
    def __init__(self):
        self.message = None
        self.account_threshhold = 50
    
    def add_recipients(self, f):
        self.recipient_file = f
    
    def set_mail_message(self, f):
        fle = io.open(f, 'r', encoding="utf-8")
        self.message = fle.readlines()
    
    def add_accounts(self, f):
        self.accounts_file = f
    
    def start_crawler(self):
        start_campaign(self.recipient_file, self.accounts_file, self.account_threshhold, self.message)

    def stop_crawler(self):
        pass
    
    def resume_crawler(self):
        pass
    
    def set_error_email(self):
        '''
            email to which any errors or alerts will be sent to.

        ''' 
        pass
    
    def set_account_threshhold(self, threshhold):
        try:
            if int(threshhold) > 50 or int(threshhold) <= 0:
                print 'account_threshhold provided not permited, defaulting to 50' 
            else:
                self.account_threshhold = int(threshhold)
        except Exception:
            pass
        
    def fix_google_phone_very(self, user_name, password):
        try:
            from time import sleep
            acc = account(user_name, password)
            gmail_obj = Gmail(verify=True)
            gmail_obj.open_url(start_url)
            gmail_obj.login_to_gmail(acc,fix_veryfy=True)
            acc.verify=0
            acc_dao=account_dto()
            acc_dao.update_verify(acc)
            print 'Account returned to usable accounts list now'
            sleep(30)
            gmail_obj.tear_down()
            
            #gmail_obj.tear_down()
        except Exception,e:
            print e
    def get_current_status(self, campaign):
        pass
    
    def get_errors(self, campaign):
        pass
