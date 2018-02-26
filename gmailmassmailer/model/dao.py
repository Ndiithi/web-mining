'''
Created on Feb 16, 2018

@author: duncan
'''
import time

import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir) 
from util.dbutils import dbConnection


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
        dbcon=dbConnection()
        cur = dbcon.get_cursor()
        cur.execute("insert into Account(user_name,password,total_sent,campaign) values(?,?,?,?)", (user_name,password,total_sent,campaign))
        dbcon.commit()
    
    def update(self,account):
        user_name=account.user_name
        password=account.password
        total_sent=account.total_sent
        campaign=account.campaign_id
        dbcon=dbConnection()
        cur = dbcon.get_cursor()
        cur.execute("update Account set total_sent=? where campaign=? and user_name=? and password=?", (total_sent,campaign,user_name,password))
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

    
        