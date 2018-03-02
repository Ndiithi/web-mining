'''
Created on Feb 24, 2018

@author: duncan
'''

import logging, logging.handlers
import os
import sys
from setuptools.command.easy_install import sys_executable



formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(funcName)s:%(lineno)d  - %(message)s')
LOG_PATH = os.path.abspath('./logs')
LOG_PATH = LOG_PATH + "/"

if not os.path.isdir(LOG_PATH):
    try:
        os.mkdir(LOG_PATH)                
    
    except Exception, e:
        pass

log_file = "gmailer.log"
full_pth = os.path.join(LOG_PATH, log_file)


if os.path.isdir(LOG_PATH):

    fh = logging.handlers.RotatingFileHandler(full_pth, maxBytes=5242880, backupCount=5)

else:
    
    fh = logging.handlers.RotatingFileHandler(log_file, maxBytes=5242880, backupCount=5)
       

fh.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
fh.setFormatter(formatter)
ch.setFormatter(formatter)


root = logging.getLogger()
root.setLevel(logging.DEBUG)
root.addHandler(fh)
root.addHandler(ch)
 
 