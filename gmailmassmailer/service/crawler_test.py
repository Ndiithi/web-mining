'''
Created on Feb 24, 2018

@author: duncan
'''

import crawler
from model.dto import account
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
recipients=['duncanndiithi@gmail.com','duncanndiithi@yahoo.com','duncan.ndiithi@inmobia.com']
        
acc1=account('duncanndiithi','elizabeth@wairimu26',498)
#acc2=account('willyadobe','seku@senior26')

account_list=[]
account_list.append(acc1)
#account_list.append(acc2)


crawler.start_campaign(recipients, account_list, 2, "Hi men,\njust ticking if gmail ticks")


