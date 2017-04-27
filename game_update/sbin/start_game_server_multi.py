#!/usr/bin/env python
# -*- coding: utf8 -*-
# This script used to start game servers.
# Author Steven
import sys,time
sys.path.append("..")
from model.base import *
from conf.config import *
import Queue

#### Configure #######
screen_name = "YUQI_SERVER"
script_path = "/data/yuqi/app/script/"

start = [
	"for i in  `sudo screen -ls|grep %s|awk -F'.' '{print $1}'`;do sudo kill $i;done" % screen_name,
	"sudo screen -dmS %s" % screen_name,
	"sudo screen -r %s -p 0 -X stuff 'cd %s'" % (screen_name,script_path) ,
	"sudo screen -r %s -p 0 -X stuff $'\n'" % screen_name ,
	"sudo screen -r %s -p 0 -X stuff 'date;sh tasks_start.sh'" % screen_name ,
	"sudo screen -r %s -p 0 -X stuff $'\n';sudo screen -ls" % screen_name ,
]

bind = ["cd %s;sudo sh tasks_bind.sh" % script_path]

check = ["sudo /usr/local/nagios/libexec/check_game_process"]
######################
if __name__ == '__main__':
	#Check
	isRoot()

	new_server_list = []
	for s in server_list:		
		item = s.split('~')
		new_server_list.append(item)

	server_list = getServerListByInput(channel_dict,new_server_list)

	print "Command list: \n[\033[1;32mstart\033[0m]: %s\n[\033[1;32mbind\033[0m]: %s\n[\033[1;32mcheck\033[0m]: %s\n" % (start,bind,check)
	select_cmd = raw_input("\033[1;35mSelect a command  execution: \033[0m")

	if select_cmd == "start":
		cmd_list = start
	elif select_cmd == "bind":
		cmd_list = bind
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
