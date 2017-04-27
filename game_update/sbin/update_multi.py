#!/usr/bin/env python
# -*- coding: utf8 -*-
# This script used to start game servers.
import sys,time,os
sys.path.append("..")
from model.base import *
from conf.config import *
import Queue


#### Configure #######
flush_screen = "FLUSH_MEMORY"

flush_memory = [
	"for i in  `sudo screen -ls|grep %s|awk -F'.' '{print $1}'`;do sudo kill $i;done" % flush_screen,
	"sudo screen -dmS %s" % flush_screen ,
	"sudo screen -r %s -p 0 -X stuff 'cd /data/yuqi/app/'" % flush_screen ,
	"sudo screen -r %s -p 0 -X stuff $'\n'" % flush_screen ,
	"sudo screen -r %s -p 0 -X stuff 'python start.egg --servertype=flushmemory'" % flush_screen ,
	"sudo screen -r %s -p 0 -X stuff $'\n';sudo screen -ls" % flush_screen ,
]

flush_redis = [
	"sudo kill `ps aux | grep redis.conf | grep -v grep | awk '{print $2}'`;sleep 3;sudo /bin/rm.py /data/redis/dump.rdb",
	"sleep 2;ps aux | grep redis-server | grep -v grep",
	"sudo /usr/sbin/redis-server /data/redis/redis.conf",
	"ps aux | grep redis-server | grep -v grep;ls -l /data/redis/",
]

#py_script = ["sudo python xx.py dbname root 20000 127.0.0.1","CHECK_PY_SCRIPT"]
py_script = ["sudo /data/upadte/upgrade_env.sh","CHECK_PY_SCRIPT"]

# Release files by tar
# tar czf update.tar.gz  script config start.egg
# tar xf  update.tar.gz -C /data/yuqi*/
tar_release = ["sudo tar xf tarfilepath -C despath", "CHECK_TAR_RELEASE"]


#["command","just check whether is mysql list."]
mysql = ["python /data/install/tools/import_sql_update.pyo database sqlfilepath ","CHECK_MYSQL"]

#copy file
copy_file = ["sudo \cp -rf sourcepath despath","CHECK_COPY"]

# file md5 checksum 




######################

class MultiSSHRunCommandForMd5(threading.Thread):
	def __init__(self,ssh_user,ssh_key,queue,cmd_list):
		threading.Thread.__init__(self)
		self.ssh_user = ssh_user
		self.ssh_key = ssh_key
		self.queue = queue
		self.cmd_list = cmd_list

	def run(self):
		while True:
			if self.queue.empty():
				break
			server = self.queue.get()
				
			multiGetResultInServerForMd5(self.ssh_user, self.ssh_key, server, self.cmd_list)
			self.queue.task_done()


def multiGetResultInServerForMd5(ssh_user,ssh_key,server,cmd_list):
	name,addr,port = server[0],server[1],server[2]
	msg = "\033[1;33;40mMd5 Checksum results: %s(%s)\033[0m\n" % (name,addr)
		
	result = runCommandsBySSH(ssh_user,ssh_key,addr,port,cmd_list)

	if result:
		# Example:[['ls /home',('ok','error')], ]
		for i in result:
			if i[1][1] =='':
				msg = msg + "\033[1;32;40m>>SUCESS:\033[0m [%s] -- {\n%s}.\n" % (i[0],i[1][0])
			else:
				msg = msg + ">>\033[1;31;40mERROR:\033[0m [%s] -- {\n%s}.\n" % (i[0],i[1][1].rstrip('\n'))
	else:
		msg = msg + ">>\033[1;31;40mERROR:\033[0m Connection Failed."
	
	print msg




class MultiSSHRunCommandForUpdate(threading.Thread):
	def __init__(self,ssh_user,ssh_key,queue,cmd_list):
		threading.Thread.__init__(self)
		self.ssh_user = ssh_user
		self.ssh_key = ssh_key
		self.queue = queue
		self.cmd_list = cmd_list

	def run(self):
		while True:
			if self.queue.empty():
				break
			server = self.queue.get()
				
			multiGetResultInServerForUpdate(self.ssh_user, self.ssh_key, server, self.cmd_list)
			self.queue.task_done()

def multiGetResultInServerForUpdate(ssh_user,ssh_key,server,cmd_list):
	name,addr,port = server[0],server[1],server[2]
	msg = "\033[1;33;40mRun results: %s(%s)\033[0m\n" % (name,addr)
		
	if "CHECK_MYSQL" in cmd_list:
		sql_cmd = ["sudo python /data/install/tools/exec_sql_root.pyo yqsanguo%s %s" % (name.split('.')[0], remote_sql_file_path)]
		#sql_cmd = ["sudo python /data/install/tools/import_sql_update.pyo yqsanguo%s %s" % (name.split('.')[0], remote_sql_file_path)]
		result = runCommandsBySSH(ssh_user,ssh_key,addr,port,sql_cmd)
	
	elif "CHECK_COPY" in cmd_list:
		copy_cmd = ["sudo \cp -rf %s %s" % (source_file_path, des_file_path)]
		result = runCommandsBySSH(ssh_user,ssh_key,addr,port,copy_cmd)
	
	elif "CHECK_TAR_RELEASE" in cmd_list:
		tar_release_cmd = ["sudo tar xf %s -C %s" % (tar_file_path, des_path)]
		result = runCommandsBySSH(ssh_user,ssh_key,addr,port,tar_release_cmd)

	elif "CHECK_PY_SCRIPT" in cmd_list:
		py_screen = "PY_SCRIPT"
		py_cmd = "python %s yqsanguo%s root 20000 127.0.0.1" % (remote_pyscript_file_path, name.split('.')[0])
		#py_cmd = ["sudo /data/updte/upgrade_env.sh"]
		py_script_cmd = [
			"for i in  `sudo screen -ls|grep %s|awk -F'.' '{print $1}'`;do sudo kill $i;done" % py_screen ,
			"sudo screen -dmS %s" % py_screen ,
			"sudo screen -r %s -p 0 -X stuff '%s'" % (py_screen,py_cmd) ,
			"sudo screen -r %s -p 0 -X stuff $'\n';sudo screen -ls" % py_screen ,
		]

		D_py_script_cmd = ["python %s yqsanguo%s root 20000 127.0.0.1" % (remote_pyscript_file_path, name.split('.')[0])]

		result = runCommandsBySSH(ssh_user,ssh_key,addr,port,py_script_cmd)
	else:
		result = runCommandsBySSH(ssh_user,ssh_key,addr,port,cmd_list)

	if result:
		# Example:[['ls /home',('ok','error')], ]
		for i in result:
			if i[1][1] =='':
				msg = msg + "\033[1;32;40m>>SUCESS:\033[0m [%s] -- {\n%s}.\n" % (i[0],i[1][0])
			else:
				msg = msg + ">>\033[1;31;40mERROR:\033[0m [%s] -- {\n%s}.\n" % (i[0],i[1][1].rstrip('\n'))
	else:
		msg = msg + ">>\033[1;31;40mERROR:\033[0m Connection Failed."
	
	print msg




if __name__ == '__main__':
	from conf.config import *
	#Check
	isRoot()

	new_server_list = []
	for s in server_list:		
		item = s.split('~')
		new_server_list.append(item)

	server_list = getServerListByInput(channel_dict,new_server_list)

	print "Command list: \n[\033[1;32mflushmemory\033[0m]: %s\n[\033[1;32mflushredis\033[0m]: %s\n[\033[1;32mpyscript\033[0m]: %s\n[\033[1;32mmysql\033[0m]: %s\n[\033[1;32mcopyfile\033[0m]: %s\n[\033[1;32mtar\033[0m]: %s\n" % (flush_memory,flush_redis,py_script,mysql,copy_file,tar_release)

	select_cmd = raw_input("\033[1;35mSelect a command execution: \033[0m")
	if select_cmd == "flushmemory":
		cmd_list = flush_memory
	elif select_cmd == "flushredis":
		cmd_list = flush_redis
	elif select_cmd == "mysql":
		cmd_list = mysql
		global remote_sql_file_path
		remote_sql_file_path = raw_input("\033[1;35mPlease enter remote sql file path: \033[0m")
	elif select_cmd == "pyscript":
		cmd_list = py_script
		global remote_pyscript_file_path
		remote_pyscript_file_path = raw_input("\033[1;35mPlease enter remote python script file path: \033[0m")

	elif select_cmd == "copyfile":
		global source_file_path
		global des_file_path
		source_file_path = raw_input("\033[1;35mPlease enter Source file path: \033[0m")
		source_file_md5 = raw_input("\033[1;35mPlease enter Source file md5checksum value: \033[0m")
		des_file_path = raw_input("\033[1;35mPlease enter to be overwritten file path(/data/yuqi/app/): \033[0m")
		cmd_list = copy_file
	elif select_cmd == "tar":
		global tar_file_path
		global des_path
		tar_file_path = raw_input("\033[1;35mPlease enter tar file path: \033[0m")
		des_path = raw_input("\033[1;35mPlease enter to be overwritten file path(/data/yuqi/app/): \033[0m")
		if des_path == "":
			des_path = "/data/yuqi/app/"
		cmd_list = tar_release
	else:
		sys.exit("Without this option [%s]. exit !!!" % select_cmd)
		

	print "Server list: "
	for s in server_list:
		print "   ",s

	input = raw_input("\033[1;35mThese game servers will run this command \033[0m[\033[1;32m%s\033[0m]\033[1;35m, are you sure? (yes/no)\033[0m " % select_cmd)
	if input != "yes":
		sys.exit("Exit...")
	
	
	start = time.time()
	que = Queue.Queue()

	if len(server_list) > 50:
		thread_num = thread_num
	else: 
		thread_num = len(server_list)
	
	for s in server_list:
		que.put(s)

	for t in range(thread_num):
		a = MultiSSHRunCommandForUpdate(ssh_user,ssh_key, que,cmd_list)
		a.setDaemon(True)
		a.start()

	que.join()


	if "CHECK_COPY" in cmd_list:
		print "----- Md5 check sum--------"
		que_md5 = Queue.Queue()

		for s in server_list:
			que_md5.put(s)


		remote_path = os.path.dirname(des_file_path)
		file = os.path.basename(des_file_path)
		if file == '':
			file = os.path.basename(source_file_path)

		for t in range(thread_num):
			a = MultiMd5(ssh_user,ssh_key,que_md5,source_file_md5.strip(),remote_path,file)
			a.setDaemon(True)
			a.start()

		que_md5.join()


	end = time.time()
	print "%s hosts, Completed in %s seconds"  % (len(server_list),str(end - start))

