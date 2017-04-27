#!/usr/bin/env python
# -*- coding: utf8 -*-
# This script used to upload files to  servers
# Author Steven
import sys,time
sys.path.append("..")
from model.base import *
from conf.config import *
import Queue

#### Configure #######
#cmd=['cd /data/update/;sudo wget http://10.161.164.177/download/public/20131113/start.egg']
######################
remote_default_path = "/data/update/"


if __name__ == '__main__':
	from conf.config import *
	#Check
	isRoot()

	new_server_list = []
	for s in server_list:		
		item = s.split('~')
		new_server_list.append(item)

	# Upload file
	server_list = getServerListByInput(channel_dict,new_server_list)

	remote_path = raw_input("\033[1;35mPlease enter the remote host directory(/data/update/): \033[0m")
	if remote_path == "":
		remote_path = remote_default_path
	file_url = raw_input("\033[1;35mPlease enter the file url|md5: \033[0m")
	url = file_url.split('|')[0]
	md5 = file_url.split('|')[1].strip()

	print "Server list: "
	for s in server_list:
		print "   ",s

	input = raw_input("\033[1;35mWill upload files to list above servers, are you sure? (yes/no)\033[0m")
	if input != "yes":
		sys.exit("Exit...")

	cmd_list = ['cd %s;sudo wget -N -q %s' % (remote_path, url)]

	start = time.time()
	que_server = Queue.Queue()
	que_md5 = Queue.Queue()

	if len(server_list) > 50:
		thread_num = thread_num
	else: 
		thread_num = len(server_list)
	
	for s in server_list:
		que_server.put(s)
		que_md5.put(s)
		

	for t in range(thread_num):
		a = MultiSSH2(ssh_user, ssh_key, que_server, cmd_list)
		a.setDaemon(True)
		a.start()

	que_server.join()
		
	print
	print
	print "------------- Md5 Checksum ---------------"


	for t in range(thread_num):
		a = MultiMd5(ssh_user, ssh_key, que_md5, md5, remote_path, url.split('/')[-1])
		a.setDaemon(True)
		a.start()

	que_md5.join()

	end = time.time()
	print
	print "%s hosts, Completed in %s seconds"  % (len(server_list),str(end - start))
