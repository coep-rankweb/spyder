from subprocess import Popen, PIPE
import smtplib
import time
import sys

def sendMail(body):
	 to = 'add.harry@gmail.com'
	 gmail_user = 'js128793817@gmail.com'
	 gmail_pwd = 'abcd1234!@#$'
	 smtpserver = smtplib.SMTP("smtp.gmail.com",587)
	 smtpserver.ehlo()
	 smtpserver.starttls()
	 smtpserver.ehlo()
	 smtpserver.login(gmail_user, gmail_pwd)
	 header = 'To:' + to + '\n' + 'From: ' + gmail_user + '\n' + 'Subject:Line Count \n'
	 msg = header + '\n %s\n(%s) \n\n' % (body, time.ctime())
	 smtpserver.sendmail(gmail_user, to, msg)

	 sys.stderr.write('done!\n')
	 smtpserver.close()


s = "\n".join(sys.stdin)
sendMail(s)
