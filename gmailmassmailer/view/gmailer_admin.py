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
import argparse


print "===================================================================="
print "Script Started At : " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print "===================================================================="

s='''
\ngmailer syntax\n
gmailer {command} {options}\n
Availble commands: \ngmailer mail {options} \ngmailer report {options} \ngmailer verify {options} \ngmailer help - to  get this help message\n
***************************************\n
options in square brackets '[]' are optional\n
1. mail command:\n
------------------
gmailer mail -R recipient_list  -A accounts_file -msg [message_file] -thresh [account_threashold] -subject [subject]\n
2. verify\n
Use this option to manually fix google authentication when phone authentication is required for a single account\n
syntax: gmailer mail -U user_name -P password\n\n

[command options]
-----------------
A. mail command options\n
1. recipient_list: csv file of recipient lists with one column only containing recipients email addresses\n
2. accounts_file: csv file of accounts with two columns, first column should be user name, second should be password\n
3. message_file: text file of the message to be delivered to recipients\n
4. account_threashold: This is the maximum recipients you want an account to send per each sending cycle, default is 50(max) recipients(bcc) per mail\n
5. subject: The subject to use in the mail\n

B. Verify command options
-----------------------------
1. user_name: account to manually authenticate user_name\n
2. password: account to manually authenticate password\n
\n\nNote:
------------
* provide csv file for both recipients list and accounts list\n\n
* if message_file is not specified, gmailer forwards the first message in gmail inbox to given recipients\n\n
* if account_threashold is not specified, gmailer uses google maximum threashold which is 50\n\n
'''


parser = argparse.ArgumentParser(prog='gmailer',usage=s)
parser.add_argument('command')
parser.add_argument('-R',dest='recipient_list')
parser.add_argument('-A',dest='accounts_file')
parser.add_argument('-M',dest='message_file')
parser.add_argument('-thresh',type=int)  
parser.add_argument('-subject')
parser.add_argument('-U',dest='user_name') 
parser.add_argument('-P',dest='password')
args=parser.parse_args()


try:
    command = args.command

except IndexError:
    pass

if len(command) == 0:
    print s
    sys.exit()
elif command == 'verify':

    user_name = args.user_name
    password = args.password
    cont = controller()        
    if  password==None or user_name==None or len(user_name.strip()) == 0 or len(password.strip()) == 0:
        print '\nPlease check the provided credentials are correct\n'
        print 'The syntax should be: gmailer verify -U {user_name} -P {password} without the braces\n'
        sys.exit()
    cont.fix_google_phone_very(user_name, password)
elif command.strip() == 'help': 
    print s
    sys.exit()
elif command.strip() == 'mail':
    
    recipient_list=args.recipient_list
    accounts_file=args.accounts_file
    message_file=args.message_file
    account_threashold = args.thresh
    subject = args.subject
    
    if recipient_list==None or accounts_file==None or len(recipient_list.strip()) == 0 or len(accounts_file) == 0 :
        print s
        sys.exit()
    
    try:
        if os.path.exists(recipient_list):
            print 'Recipients file found: {}'.format(os.path.basename(recipient_list))
            if not os.access(recipient_list, os.R_OK):
                sys.exit()
        else:
            print 'Could not read recipient file given'
            sys.exit()
            
        if os.path.exists(accounts_file):
            print 'Accounts file found: {}'.format(os.path.basename(accounts_file))
            if not os.access(accounts_file, os.R_OK):
                sys.exit()
        else:
            print 'Could not read accounts file given'   
            sys.exit()
        
        message_file_given=False
        if message_file != None:
            if os.path.exists(message_file):
                print 'Message file found: {}'.format(os.path.basename(message_file))
                if not os.access(message_file, os.R_OK):    
                    print 'No message file found'           
                    sys.exit()
                message_file_given = True
            else:
                print 'Could not read message file given, will forward mail from mailbox'   
        else:
            print 'No message file given, will forward mail from mailbox'   
            sys.exit()
            
        cont = controller()
        cont.add_recipients(recipient_list)
        cont.add_accounts(accounts_file)
        
        if message_file_given:
            cont.set_mail_message(message_file)
        
        if subject==None:
            print 'Did not include subject, proceeding without mail subject'
        else:
            print 'Subject is {}'.format(subject)
            cont.set_subject(subject)
        if account_threashold!=None:
            if account_threashold >= 1 and account_threashold <= 50:
                cont.set_account_threshhold(account_threashold)
                print 'account thresh-hold {}'.format(account_threashold)
        cont.start_crawler()  
    except Exception, e:
        print e
else:
    print s
    
print '\n'
print "===================================================================="
print "Script End At : " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print "===================================================================="
