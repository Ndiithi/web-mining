'''
Created on Feb 22, 2018

@author: duncan
'''

class single_campaign:
    
    def __init__(self,account,recipients_list,message):
        self.account=account
        self.recipients_list=recipients_list
        self.message=message
        
class multi_campaign:
    
    def __init__(self,accounts_list,recipients_list):
        self.accounts_list=accounts_list
        self.recipients_list=recipients_list
        
class account:
    
    def __init__(self,user_name,password):
        self.user_name=user_name
        self.password=password
        self.total_sent=0
        self.campaign_id=0
        
class campaign:
    
    def __init__(self):
        self.date=None
        self.campaign_id=None
        
class message:
    
    def __init__(self):
        self.text=None

class recipient:
    
    def __init__(self):
        self.email=None
        self.campaign_id=0
        
    