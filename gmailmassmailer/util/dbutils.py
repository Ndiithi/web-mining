'''
Created on Feb 16, 2018

@author: duncan
'''

import os.path

import sqlite3 as lite


class dbConnection:
    def __init__(self):
        
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "gmailmassmailer.db")
        self.__con = lite.connect(db_path)
        self.__cur = self.__con.cursor()
        self.__cur.execute('''
            create table IF NOT EXISTS error ( error_id INTEGER, detail TEXT(200),
            time_created TEXT(100),  PRIMARY KEY(error_id) )
        ''')
#         self.__cur.execute('''
#             create table IF NOT EXISTS subscription( subscriber_id INTEGER, 
#             site_id INTEGER, keyword_id INTEGER, page_limit INTEGER NOT NULL DEFAULT 1, minimum_alert 
#             INTEGER NOT NULL DEFAULT 1,subscription_group_id INTEGER,
#             PRIMARY KEY(subscriber_id,site_id,keyword_id) )
#         ''')
#         self.__cur.execute(''' 
#             create table IF NOT EXISTS cookie ( icookie_id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT, value TEXT, site_id INTEGER, group_key INTEGER )
#         ''')
#         self.__cur.execute(''' 
#             create table IF NOT EXISTS group_id_sequence ( Field1 INTEGER PRIMARY KEY AUTOINCREMENT )
#         ''')
#         self.__cur.execute(''' 
#             create table IF NOT EXISTS retry_counter ( counter_id INTEGER PRIMARY KEY AUTOINCREMENT, retry INTEGER, site_id INTEGER )
#         ''')
#         self.__cur.execute('''create table IF NOT EXISTS sent_jobs ( subscriber_id INTEGER NOT NULL, 
#                             job_id INTEGER NOT NULL, timestamp TEXT, PRIMARY KEY(subscriber_id,job_id), 
#                             FOREIGN KEY(subscriber_id) 
#                             REFERENCES subscriber(subsriber_id) ON DELETE CASCADE ON UPDATE NO ACTION, 
#                             FOREIGN KEY(job_id) REFERENCES jobs(job_id) ON DELETE CASCADE ON UPDATE NO ACTION )                      
#         ''')
#         self.__cur.execute("create table IF NOT EXISTS  subscriber(subscriber_id INTEGER PRIMARY KEY ASC,email TEXT(100) UNIQUE)")
#         self.__cur.execute("create table IF NOT EXISTS  keyword(keyword_id INTEGER PRIMARY KEY ASC,keyword TEXT(100) UNIQUE)")  
#         self.__cur.execute('''create table IF NOT EXISTS site ( site_id INTEGER, name TEXT(100) UNIQUE, alias TEXT(100),
#             user_agent TEXT, no_of_pages INTEGER,
#             minimum_jobs_alert INTEGER, PRIMARY KEY(site_id) )''')  
#         self.__cur.execute("delete from jobs where (julianday('now') - julianday(time_created)) >= 10")
#         self.__cur.execute("delete from sent_jobs where (julianday('now') - julianday(timestamp)) >= 14")
        self.__con.commit()
     
    
    def get_cursor(self):
        return self.__cur
    
    def close_db_connection(self):
        self.__con.close()
        
    def commit(self):
        self.__con.commit()
    
    def rollback(self):
        self.__con.rollback()
