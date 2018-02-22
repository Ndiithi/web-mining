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
        cur.execute("insert into error(detail,time_created) values('%s','%s')" %(msg,cur_time))
        dbcon.commit()