# -*- coding: utf-8 -*-
# Config file
# Author Steven

# SSH Connect
ssh_user = 'checkhealth'
ssh_key = '../conf/sshkey'

ftp_user = 'steven'
ftp_pwd = 'aadfasdf'
ftp_port = 21
ftp_timeout = 120
	



# Max thread
thread_num = 50

# Channel
channel_dict = {0:"All Channel", 1:'jianyi', 2:'tishen', 99:'other', 100:'test', 101:'Will open',102:'hequ', 103:'fengce'}

# Server list rule: ['zoneid.channelid.serverid~ip~sshport',]

#<><><><><><><><><<><><><><><><><> JIANYI <><><><><><><><><><><><><><><><><><><>
server_list = [
	#>>>>>>>>>>>> Channel jianyi <<<<<<<<<<<<<<
	'1.1.8~115xxxxx~23004',
	'81.1.53~1asdf.109.80~23004',
	'83.1.62~12asdfdf8.138~23004',
	# Will open

	# Hequ
	# Game update test
	'201.100.48~121asdfasdff4.68~23004',

	# Tishen 

	# Other
	'82.99.61~121.4xxxx9~23004',
]

