'''
from subprocess import Popen, PIPE
'''
import smtplib
import time
import sys
from pymongo import MongoClient

def sendMail(subject = "ERROR", body = "FAILED"):
	 to = 'add.harry@gmail.com'
	 gmail_user = 'js128793817@gmail.com'
	 gmail_pwd = 'abcd1234!@#$'
	 smtpserver = smtplib.SMTP("smtp.gmail.com",587)
	 smtpserver.ehlo()
	 smtpserver.starttls()
	 smtpserver.ehlo()
	 smtpserver.login(gmail_user, gmail_pwd)
	 header = 'To:' + to + '\n' + 'From: ' + gmail_user + '\n' + 'Subject:%s \n' % subject
	 msg = header + '\n%s\n (%s) \n' % (body, time.ctime())
	 smtpserver.sendmail(gmail_user, to, msg)

	 sys.stderr.write('done!\n')
	 smtpserver.close()

client = MongoClient()
cr = client['SPIDER_DB']['CRAWLER_DATA']
result = str(cr.find_one())

'''
p1 = Popen(["ps", "-eF"], stdout = PIPE)
p2 = Popen(["grep", "scrapy"], stdin = p1.stdout, stdout = PIPE)
out = p2.communicate()[0]

if out.find("/usr/bin/python") == -1:
	sendMail()
'''
sendMail("STATUS_UPDATE", result)
