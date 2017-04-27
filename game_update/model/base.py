import threading,sys,os

def writeLog(file,content):
	f = open(file,'aw')
	f.write(content)
	f.close()

def isRoot():
	import commands
	if commands.getoutput('whoami') != 'root':
		sys.exit('\033[1;31;40mMust be root run this script !!!\033[0m')

def isConfigure():
	input = raw_input("\033[5;31;40mPlease make sure the configure , are you sure?(yes/no)\033[0m")
	if input != "yes":
		sys.exit('exit')

def runCommandsBySSH(user,key,host,port,cmd_list):
	import paramiko
	try:
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		rsa_key = paramiko.RSAKey.from_private_key_file(key)
		ssh.connect(hostname=host,port=int(port),username=user,pkey=rsa_key)
	
		result = []	
		for c in cmd_list:
			stdin,stdout,stderr = ssh.exec_command(c)
			output = stdout.read(),stderr.read()
			a = []
			a.append(c)
			a.append(output)
			result.append(a)
		
		# Example:[['ls /home',('ok','error')], ]
		return result
		s.close()
	except Exception,e:
		#raise e
		print e
		return False


def getServerListByInput(channel_dict,server_list):
	prompt = []
	input_list = []
	for key,value in channel_dict.items():
		str = "%s: %s\n" % (key,value)
		prompt.append(str)

	#> Channel select.
	input = raw_input("\033[1;32m%s\033[0m\n\033[1;35mSelect a Channel that you want to operate, Number(1&2&3):\033[0m" % ''.join(prompt))

	if "&" in input:
		input_list = input.split('&')	
	else:
		input_list.append(input)

	for i in input_list:
		try:
			o = int(i)
		except:
			sys.exit("Channel id must be integer. Exit !")

		if o not in channel_dict.keys():
			sys.exit("Without this Channel [%s]. exit !!!" % o)

	new_server_list = []
	for select in input_list:
		if select == '0':
			new_server_list = server_list
			break
		else:
			channel_id = select
			for s in server_list:
				cid = s[0].split('.')[1]
				if channel_id == cid:
					new_server_list.append(s)

	server_list = new_server_list

	#> Server select.
	input = raw_input("\033[1;32m1: All servers.\n2: All gate servers.\n3: All battle servers.\033[0m\n\033[1;35mSelect the server that you want to operate, Number:\033[0m")

	if input == "1":
		return server_list

	elif input == "2":
		gate_server_list = []
		for s in server_list:
			server_num = s[0].split('.')[2]
			if int(server_num) % 2 == 1:
				gate_server_list.append(s)
		return gate_server_list

	elif input == "3":
		battle_server_list = []
		for s in server_list:
			server_num = s[0].split('.')[2]
			if int(server_num) % 2 == 0:
				battle_server_list.append(s)
		return battle_server_list
	else:
		sys.exit("Without this option [%s]. exit !!!" % input)

def getResultInServers(cmd_list,server_list,ssh_user,ssh_key):
	print ">\033[1;31;46mRun Command Start\033[0m >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
	for s in server_list:
		name,addr,port = s[0],s[1],s[2]
		print "\033[1;33;40mRun results: %s(%s)\033[0m\n" % (name,addr)

		result = runCommandsBySSH(ssh_user,ssh_key,addr,port,cmd_list)

		if result:
			# Example:[['ls /home',('ok','error')], ]
			#print result
			for i in result:
				if i[1][1] =='':
					print "\033[1;32;40m>>SUCESS:\033[0m [%s] -- {\n%s}." % (i[0],i[1][0])
					print 
				else:
					print ">>\033[1;31;40mERROR:\033[0m [%s] -- {\n%s}." % (i[0],i[1][1].rstrip('\n'))
					print
					
		else:
			print ">>\033[1;31;40mERROR:\033[0m Connection Failed."

	print "<\033[5;31;40mRun Command END \033[0m<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
	


def getMd5InServers(ssh_user, ssh_key, server_list, md5, remote_path, file):
	print ">\033[1;31;46mUpload file Md5 Checksum\033[0m"
	for s in server_list:
		name,addr,port = s[0],s[1],s[2]
		print "\n\033[1;33;40mMd5 results: %s(%s)\033[0m" % (name,addr)

		cmd_list = ["cd %s;sudo md5sum %s" % (remote_path,file)]
		result = runCommandsBySSH(ssh_user,ssh_key,addr,port,cmd_list)

		if result:
			# Example:[['ls /home',('ok','error')], ]
			for i in result:
				if i[1][1] =='':
					remote_file_md5 = i[1][0].split(' ')[0].strip() # md5value  filename
					if remote_file_md5 == md5:
						print "\033[1;32;40m>>SUCESS:\033[0m [%s] - %s%s." % (remote_file_md5,remote_path,file)
					else:
						print "\033[1;31;40m>>ERROR:\033[0m [%s] - %s%s." % (remote_file_md5,remote_path,file)
				else:
					print ">>\033[1;31;40mERROR:\033[0m [%s] -- {\n%s}." % (i[0],i[1][1].rstrip('\n'))
					print
		else:
			print ">>\033[1;31;40mERROR033[0m Connection Failed."
	



def multiGetResultInServer2(ssh_user,ssh_key,server,cmd_list):
	name,addr,port = server[0],server[1],server[2]
	msg = "\033[1;33;40m%s(%s)\033[0m   " % (name,addr)

	result = runCommandsBySSH(ssh_user,ssh_key,addr,port,cmd_list)

	if result:
		# Example:[['ls /home',('ok','error')], ]
		#print result
		for i in result:
			if i[1][1] =='':
				msg = "\033[1;32;40mSUCESS\033[0m{%s}" % msg
				msg = msg.replace(' ',"")
			else:
				msg = msg + ">>\033[1;31;40mERROR:\033[0m [%s] -- {\n%s}.\n" % (i[0],i[1][1].rstrip('\n'))
				
	else:
		msg = msg + ">>\033[1;31;40mERROR:\033[0m Connection Failed."

	print msg,


def multiGetResultInServer(ssh_user,ssh_key,server,cmd_list):
	name,addr,port = server[0],server[1],server[2]
	msg = "\033[1;33;40mRun results: %s(%s)\033[0m\n" % (name,addr)

	result = runCommandsBySSH(ssh_user,ssh_key,addr,port,cmd_list)

	if result:
		# Example:[['ls /home',('ok','error')], ]
		#print result
		for i in result:
			if i[1][1] =='':
				msg = msg+ "\033[1;32;40m>>SUCESS:\033[0m [%s] -- {\n%s}.\n" % (i[0],i[1][0])
			else:
				msg = msg + ">>\033[1;31;40mERROR:\033[0m [%s] -- {\n%s}.\n" % (i[0],i[1][1].rstrip('\n'))
				
	else:
		msg = msg + ">>\033[1;31;40mERROR:\033[0m Connection Failed."

	print msg,
	
	


def multiGetMd5InServer(ssh_user,ssh_key,server,md5,remote_path,file):
	name,addr,port = server[0],server[1],server[2]
	msg = "\033[1;33;40m%s(%s)\033[0m" % (name,addr)

	cmd_list = ["cd %s;sudo md5sum %s" % (remote_path,file)]
	result = runCommandsBySSH(ssh_user,ssh_key,addr,port,cmd_list)
	
	if result:
		# Example:[['ls /home',('ok','error')], ]
		for i in result:
			if i[1][1] =='':
				remote_file_md5 = i[1][0].split(' ')[0].strip() # md5value filename
				if remote_file_md5 == md5:
					msg = "\033[1;32;40mSUCESS\033[0m ~ " + msg
				else:
					msg = msg + "\033[1;31;40m>>ERROR:\033[0m [%s] - %s%s." % (remote_file_md5,remote_path,file)
			else:
				msg = msg + ">>\033[1;31;40mERROR:\033[0m [%s] -- {\n%s}.\n" % (i[0],i[1][1].rstrip('\n'))
	else:
		msg = msg + ">>\033[1;31;40mERROR033[0m Connection Failed."

	print msg,


class MultiMd5(threading.Thread):
	def __init__(self,ssh_user,ssh_key,que,md5,remote_path,file):
		threading.Thread.__init__(self)
		self.ssh_user = ssh_user
		self.ssh_key = ssh_key
		self.queue = que
		self.md5 = md5
		self.remote_path = remote_path
		self.file = file

	def run(self):
		while True:
			if self.queue.empty():
				break
			server = self.queue.get()
			multiGetMd5InServer(self.ssh_user, self.ssh_key, server, self.md5, self.remote_path, self.file)
			self.queue.task_done()



class MultiSSH(threading.Thread):
	def __init__(self,ssh_user,ssh_key,que,cmd_list):
		threading.Thread.__init__(self)
		self.ssh_user = ssh_user
		self.ssh_key = ssh_key
		self.queue = que
		self.cmd_list = cmd_list

	def run(self):
		while True:
			if self.queue.empty():
				break
			server = self.queue.get()
				
			multiGetResultInServer(self.ssh_user, self.ssh_key, server, self.cmd_list)
			self.queue.task_done()

class MultiSSH2(threading.Thread):
	def __init__(self,ssh_user,ssh_key,que,cmd_list):
		threading.Thread.__init__(self)
		self.ssh_user = ssh_user
		self.ssh_key = ssh_key
		self.queue = que
		self.cmd_list = cmd_list

	def run(self):
		while True:
			if self.queue.empty():
				break
			server = self.queue.get()
				
			multiGetResultInServer2(self.ssh_user, self.ssh_key, server, self.cmd_list)
			self.queue.task_done()



def ftpConnect(host,user,pwd,port,timeout):
	import ftplib
	ftp=ftplib.FTP()
	#ftp.set_debuglevel(2)
	try:
		ftp.connect(host,port,timeout)
	except:
		return '\033[1;31;40mERROR:\033[0m Cannot connect [%s]' % (host)

	try:
		ftp.login(user,pwd)
	except ftplib.error_perm,e:
		ftp.quit()
		return "ERROR: %s [%s]" % (e,host)
	else:
		return ftp


def downloadFile(remote_file,save_path,host,user,pwd,port,timeout):
	name = host[0]
	addr = host[1]
	ftp = ftpConnect(addr,user,pwd,port,timeout)
	bufsize = 1024
	file_name = remote_file.split('/')[-1]
	save_file = "%s/%s" % (save_path,file_name)
	fp = open(save_file,'wb')
	try:
		ftp.retrbinary('RETR ' + remote_file,fp.write,bufsize)
	except:
		os.unlink(save_file)
		fp.close()
		ftp.quit()
		print '\033[1;31;40mERROR(%s):\033[0m Cannot read file [%s]' % (name,remote_file)
	else:
		fp.close()
		ftp.quit()
		print "\033[1;32;40mSUCESS(%s):\033[0m Download complete. Save to [%s]" % (name,save_file)
	

def uploadFile(local_file,remote_path,host,user,pwd,port,timeout):
	name = host[0]
	addr = host[1]
	ftp = ftpConnect(addr,user,pwd,port,timeout)
	bufsize = 1024
	file_name = local_file.split('/')[-1]
	remote_file = "%s/%s" % (remote_path, file_name)
	fp = open(local_file,'rb')
	try:
		ftp.storbinary('STOR ' + remote_file, fp, bufsize)
	except:
		fp.close()
		ftp.quit()
		print '\033[1;31;40mERROR(%s):\033[0m Cannot upload file [%s]' % (name,local_file)
	else:
		fp.close()
		ftp.quit()
		print "\033[1;32;40mSUCESS(%s):\033[0m Upload complete. Save to [%s]" % (name,remote_file)
