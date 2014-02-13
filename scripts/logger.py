from subprocess import Popen, PIPE
import smtplib
import time
import redis
import sys

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
p1 = Popen(["ps", "-eF"], stdout = PIPE)
p2 = Popen(["grep", "scrapy"], stdin = p1.stdout, stdout = PIPE)
out = p2.communicate()[0]

if out.find("/usr/bin/python") == -1 and not r.get("USER_PROMPTED"):
	sendMail()
	r.set("USER_PROMPTED", "Y")
sendMail(s)
