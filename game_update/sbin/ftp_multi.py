#!/usr/bin/env python
# -*- coding: utf8 -*-
# Author Steven
# This script used to download file from game servers.
# Last modify 20140619

import os,sys,time
sys.path.append("..")
from model.base import *
from conf.config import *
import Queue


save_path_prefix = '../download'

class MultiDownloadFile(threading.Thread):
	def __init__(self,remote_files,server_que,ftp_user,ftp_pwd,ftp_port,ftp_timeout):
		threading.Thread.__init__(self)
		self.remote_files = remote_files
		self.server_que = server_que
		self.ftp_user = ftp_user
		self.ftp_pwd = ftp_pwd
		self.ftp_port = ftp_port
		self.ftp_timeout = ftp_timeout
		
	def run(self):
		while True:
			if self.server_que.empty():
				break
			server = self.server_que.get()
			zone_id  = server[0].split('.')[0]
			channel_id = server[0].split('.')[1]
			ftp_host = server[1]
			save_path = "%s/%s/%s/%s/" % (save_path_prefix,channel_id,zone_id,ftp_host)
			if not os.path.exists(save_path):
				os.makedirs(save_path)
			
			downloadFile(self.remote_files,save_path,server,self.ftp_user,self.ftp_pwd,self.ftp_port,self.ftp_timeout)
	
			self.server_que.task_done()


class MultiUploadFile(threading.Thread):
	def __init__(self,local_file,remote_path,server_que,ftp_user,ftp_pwd,ftp_port,ftp_timeout):
		threading.Thread.__init__(self)
		self.local_file = local_file
		self.remote_path = remote_path
		self.server_que = server_que
		self.ftp_user = ftp_user
		self.ftp_pwd = ftp_pwd
		self.ftp_port = ftp_port
		self.ftp_timeout = ftp_timeout
		
	def run(self):
		while True:
			if self.server_que.empty():
				break
			server = self.server_que.get()
			uploadFile(self.local_file,self.remote_path,server,self.ftp_user,self.ftp_pwd,self.ftp_port,self.ftp_timeout)
			self.server_que.task_done()




if __name__ == '__main__':
	#Check
	isRoot()

	new_server_list = []
	for s in server_list:		
		item = s.split('~')
		new_server_list.append(item)

	server_list = getServerListByInput(channel_dict,new_server_list)

	print "Command list: \n[\033[1;32mupload\033[0m]: Upload file to servers.\n[\033[1;32mdownload\033[0m]: Download file from servers.\n"
	select_cmd = raw_input("\033[1;35mSelect a command to execution: \033[0m")

	
	start = time.time()
	server_que = Queue.Queue()

	if len(server_list) > 50:
		thread_num = thread_num
	else: 
		thread_num = len(server_list)
	
	for s in server_list:
			server_que.put(s)

	if select_cmd == "download":
		remote_files = raw_input("\033[1;35mPlease enter the remote_file_path: \033[0m")
		if remote_files == "":
			sys.exit("Not input, Exit...")
		
		print "Server list: "
		for s in server_list:
			print "   ",s

		input = raw_input("\033[1;35mDownload file from this game server, are you sure? (yes/no)\033[0m")
		if input != "yes":
			sys.exit("Exit...")
		print

		for t in range(thread_num):
			a = MultiDownloadFile(remote_files,server_que,ftp_user,ftp_pwd,ftp_port,ftp_timeout)
			a.setDaemon(True)
			a.start()

	elif select_cmd == "upload":
		local_file = raw_input("\033[1;35mPlease enter the local file to upload: \033[0m")
		if not os.path.isfile(local_file):
			sys.exit("Error:[%s] not a file !" % local_file)
		remote_path = raw_input("\033[1;35mPlease enter remote path: \033[0m")
		if remote_path == "":
			sys.exit("Exit...")

		print "Server list: "
		for s in server_list:
			print "   ",s

		input = raw_input("\033[1;35mUpload file to this game server, are you sure? (yes/no)\033[0m")
		if input != "yes":
			sys.exit("Exit...")
		print

		for t in range(thread_num):
			a = MultiUploadFile(local_file,remote_path,server_que,ftp_user,ftp_pwd,ftp_port,ftp_timeout)
			a.setDaemon(True)
			a.start()
	else:
		sys.exit("Without this command [%s]. exit !" % select_cmd)
	




	server_que.join()
	end = time.time()
	print "\n%s hosts, Completed in %s seconds"  % (len(server_list),str(end - start))
	

