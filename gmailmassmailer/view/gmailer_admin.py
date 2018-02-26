'''
Created on Feb 24, 2018

@author: duncan
'''
from datetime import datetime
import logging
import os
import sys
from setuptools.command.easy_install import sys_executable
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parentdir) 
from controller.control import controller
from service.crawler import LOG_PATH


logger = logging.getLogger(__name__)

print "===================================================================="
print "Script Started At : " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print "===================================================================="


def print_help_text():
    print "gmailer syntax\n"
    print "gmailer {command} {options}\n"
    print "Availble commands: \ngmailer mail {options} \ngmailer report {options} \ngmailer verify {options} \ngmailer help - to  get this help message\n"
    print '***************************************'
    print "options in square brackets '[]' are optional\n"
    print '1. mail command:\n'
    print "gmailer mail recipient_list accounts_file [message_file] [account_threashold]\n"
    print '2. verify\n'
    print "Use this option to manually fix google authentication when phone authentication is required for a single account"
    print 'syntax: gmailer mail user_name pass_word\n'
    print '[options]'
    print '----------'
    print 'a. mail command options'
    print '1. recipient_list: csv file of recipient lists with one column only containing recipients email addresses'
    print '2. accounts_file: csv file of accounts with two columns, first column should be user name, second should be password'
    print '3. message_file: text file of the message to be delivered to recipients'
    print '4. account_threashold: This is the maximum recipients you want an account to send per each sending cycle, default is 50(max) recipients(bcc) per mail\n'
    print '\na. Verify command options'
    print '1. user_name: account to manually authenticate user_name'
    print  '2. password: account to manually authenticate password'
    print '\nNote:'
    print '------------'
    print '* provide csv file for both recipients list and accounts list\n'
    print '* if message_file is not specified, gmailer forwards the first message in gmail inbox to given recipients\n'
    print '* if account_threashold is not specified, gmailer uses google maximum threashold which is 50\n'


command=''
recipient_list = ''
accounts_file = ''
account_threashold=0
message_file = ''
message_file_given=False
try:
    command = sys.argv[1] 
    recipient_list = sys.argv[2]    
    accounts_file = sys.argv[3]
    message_file = sys.argv[4]
    account_threashold=sys.argv[5]
except IndexError:
    pass


if len(command)==0:
    print_help_text()
    sys.exit()
elif command=='verify':
    cont=controller()        
    user_name=recipient_list
    password = accounts_file
    if len(user_name.strip()) == 0 or len(password.strip()) == 0 :
        print '\nplease check the provided credentials are correct\n'
        sys.exit()
    cont.fix_google_phone_very(user_name, password)
elif command.strip()=='help': 
    print_help_text()
    sys.exit()
elif command.strip()=='mail':
    if len(recipient_list.strip()) == 0 or len(accounts_file) == 0 :
        print_help_text()
        sys.exit()
    try:
        if os.path.exists(recipient_list):
            print 'Recipients file found: {}'.format(os.path.basename(recipient_list))
            if not os.access(recipient_list, os.R_OK):
                sys.exit()
        else:
            print 'Could not read recipient file given'
            
        if os.path.exists(accounts_file):
            print 'Accounts file found: {}'.format(os.path.basename(accounts_file))
            if not os.access(accounts_file, os.R_OK):
                sys.exit()
        else:
            print 'Could not read accounts file given'   
    
        if len(message_file)!=0:
            if os.path.exists(message_file):
                print 'Message file found: {}'.format(os.path.basename(accounts_file))
                if not os.access(message_file, os.R_OK):               
                    sys.exit()
                message_file_given=True
            else:
                print 'Could not read message file given'   
        cont=controller()
        cont.add_recipients(recipient_list)
        cont.add_accounts(accounts_file)
        if message_file_given:
            cont.set_mail_message(message_file)
        if account_threashold!=0:
            cont.set_account_threshhold(account_threashold)
        cont.start_crawler()  
    except Exception, e:
        print e
else:
    print_help_text()
    
print '\n'
print "===================================================================="
print "Script End At : " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print "===================================================================="
