#!/usr/bin/env python
# -*- coding: utf8 -*-
# This script used to stop game server
# Author Steven
import sys,time
sys.path.append("..")
from model.base import *
from conf.config import *
import Queue

#### Configure #######
close = ['cd /data/yuqi/app/script/; sudo sh tasks_close.sh']
check = ["ps aux | grep start.egg | grep -v grep | awk '{print $14}' | awk -F'=' '{print $2}'"]
######################

if __name__ == '__main__':
	from conf.config import *
	#Check
	isRoot()

	new_server_list = []
	for s in server_list:		
		item = s.split('~')
		new_server_list.append(item)

	server_list = getServerListByInput(channel_dict,new_server_list)

	print "Command list: \n[\033[1;32mclose\033[0m]: %s\n[\033[1;32mcheck\033[0m]: %s\n" % (';'.join(close),';'.join(check))
	select_cmd = raw_input("\033[1;35mSelect a command  execution: \033[0m")

	if select_cmd == "close":
		cmd_list = close
	elif select_cmd == "check":
		cmd_list = check
	else:
		sys.exit("Without this command [%s]. exit !" % select_cmd)

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
		a = MultiSSH(ssh_user,ssh_key,que,cmd_list)
		a.setDaemon(True)
		a.start()

	que.join()
		
	end = time.time()
	print "%s hosts, Completed in %s seconds"  % (len(server_list),str(end - start))

	
