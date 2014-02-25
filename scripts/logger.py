import smtplib
import time
import redis
import sys
import psutil

sys.exit(1)

def sendMail(body = "FAILED"):
	 to = 'add.harry@gmail.com'
	 gmail_user = 'js128793817@gmail.com'
	 gmail_pwd = 'abcd1234!@#$'
	 smtpserver = smtplib.SMTP("smtp.gmail.com",587)
	 smtpserver.ehlo()
	 smtpserver.starttls()
	 smtpserver.ehlo()
	 smtpserver.login(gmail_user, gmail_pwd)
	 header = 'To:' + to + '\n' + 'From: ' + gmail_user + '\n' + 'Subject:Error \n'
	 msg = header + '\n%s\n (%s) \n' % (body, time.ctime())
	 smtpserver.sendmail(gmail_user, to, msg)

	 sys.stderr.write('done!\n')
	 smtpserver.close()

r = redis.Redis()


s = "\n".join(sys.stdin)

if not any(["scrapy" in i.name for i in psutil.process_iter()]):
	sendMail("shutting down!")
	sys.exit(1)

sendMail(s)
sys.exit(0)
