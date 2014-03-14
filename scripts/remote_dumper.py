import paramiko
import time
import sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.1.99.15', username='coep', password='coep4')

command = "echo coep4 | bash /home/coep/Documents/dumptruck.sh " + sys.argv[1]
stdin, stdout, stderr = ssh.exec_command(command)
print stderr.readlines()

ssh.close()

del ssh

print "Sleeping"

time.sleep(600)
