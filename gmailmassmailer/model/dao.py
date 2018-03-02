'''
Created on Feb 16, 2018

@author: duncan
'''
import time

import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir) 
from util.dbutils import dbConnection
from model.dto import account as account_dto
import logging
from service import lg
from sqlite3 import IntegrityError
logger = logging.getLogger(__name__)

class error():
    
    def save_error(self,msg):
        cur_time=time.strftime("%Y/%m/%d %H:%M:%S")
        dbcon=dbConnection()
        cur = dbcon.get_cursor()
        cur.execute("insert into error(detail,time_created) values(?,?)", (msg,cur_time))
        dbcon.commit()

class account:
    
    def __init__(self):
        pass
    
    def save(self,account):
        user_name=account.user_name
        password=account.password
        total_sent=account.total_sent
        campaign=account.campaign_id
        was_account_save=False
        try:#unique constraint exception
            dbcon=dbConnection()
            cur = dbcon.get_cursor()
            cur.execute("insert into Account(user_name,password,total_sent,campaign) values(?,?,?,?)", (user_name,password,total_sent,campaign))
            dbcon.commit()
            was_account_save=True
            return was_account_save
        except IntegrityError:
            logger.error("Duplicate user name and passsword for user {}".format(account.user_name))
            return was_account_save
    
    def select(self,campaign_id):
        dbcon=dbConnection()
        cur = dbcon.get_cursor()
        cur.execute("select * from Account where campaign=?",(campaign_id,))
        accounts = cur.fetchall()
        account_list=[]
        logger.debug('Accounts list returned  from db')
        for accnt in accounts:
            acc=account_dto(accnt[1],accnt[2])
            acc.total_sent=accnt[3]
            acc.campaign_id=accnt[4]
            acc.verify=accnt[5]
            account_list.append(acc)
            logger.debug('username {} pass{}'.format(accnt[1],accnt[2]))
        dbcon.close_db_connection()
        logger.debug("the returned list:")
        logger.debug(account_list)
        return account_list
    
    
    def update(self,account):
        user_name=account.user_name
        password=account.password
        total_sent=account.total_sent
        verify=account.verify
        campaign=account.campaign_id
        dbcon=dbConnection()
        cur = dbcon.get_cursor()
        cur.execute("update Account set total_sent=? where campaign=? and user_name=? and password=? and verify=?", (total_sent,campaign,user_name,password,verify))
        dbcon.commit()
        
        
    def update_verify(self,account):
        user_name=account.user_name
        password=account.password
        verify=account.verify
        logger.info('Updating verify state for account name: {} to verify value: {}'.format(user_name,verify))
        dbcon=dbConnection()
        cur = dbcon.get_cursor()
        cur.execute("update Account set verify=? where  user_name=? and password=?", (verify,user_name,password))
        dbcon.commit()
        
        
class recipient:
    
    def __init__(self):
        pass
    
    def save(self,recipient):
        dbcon=dbConnection()
        cur = dbcon.get_cursor()
        cur.execute("insert into recipient(email,campaign,sent_status) values(?,?,?)", (recipient.email,recipient.campaign_id,0))
        dbcon.commit()
    
    def update(self,recipient):
        dbcon=dbConnection()
        cur = dbcon.get_cursor()
        cur.execute("update recipient set sent_status=?  where email=? and campaign=?", (1,recipient.email,recipient.campaign_id))
        dbcon.commit()


class campaign:
    
    def __init__(self):
        pass
    
    def create_new_campaign(self):
        cur_time=time.strftime("%Y/%m/%d %H:%M:%S")
        dbcon=dbConnection()
        cur = dbcon.get_cursor()
        cur.execute("insert into campaign(date) values(?)", (cur_time,))
        dbcon.commit()
        generated_campaign_id=cur.lastrowid
        return generated_campaign_id
        
class message:
    
    def __init__(self):
        pass
    
    def save(self,message,campaign_id):
        dbcon=dbConnection()
        cur = dbcon.get_cursor()
        cur.execute("insert into Message(text,campaign) values(?,?)", (message,campaign_id))
        dbcon.commit()

    
        