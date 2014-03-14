import time
import os
import psutil
import signal
import redis
import paramiko

processes = psutil.process_iter()

for p in processes:
	if ' '.join(p.cmdline).rfind("indexer") >= 0:
		# found indexer
		#print "Found indexer, getting ready to wait!"
		p.wait()
		#print "Hello, I was waiting for indexer to wake up! Lazy SOB."
		os.kill(29818, signal.SIGKILL)

		r = redis.Redis(host = "10.1.99.15")
		r.shutdown()

		#print "ssh'ing into the other comp and shutting its ass down"

		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect("10.1.99.15", username = "coep", password = "coep4")
		ssh.exec_command("echo coep4 | sudo -S -k cp /var/lib/redis/6379/dump.rdb /home/coep/Downloads/snapshot/save_12_03/after_indexer.rdb")
		ssh.exec_command("echo coep4 | sudo -S -k cp /home/coep/Downloads/snapshot/save_12_03/dump.rdb /var/lib/redis/6379/dump.rdb")
		ssh.exec_command("echo coep4 | sudo -S -k service redis_6379 start")
		ssh.close()

		os.system("echo elonmusk | sudo -S -k service redis start")
		time.sleep(600)
		os.system("python /home/nvidia/Documents/save_28_02/rankmap.py")
		break
else:
	# could not find indexer
	print "Where the hell is indexer?"
	pass

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("10.1.99.15", username = "coep", password = "coep4")
ssh.exec_command("echo coep4 | sudo -S -k poweroff")

os.system("echo elonmusk | sudo -S -k poweroff")
