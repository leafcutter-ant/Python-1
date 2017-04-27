#!/usr/bin/env python
# -*- coding: utf8 -*-
# This script used to Run commands on servers
import sys,time
sys.path.append("..")
from model.base import *
from conf.config import *
import Queue

#### Configure ##########################
cmd_list = ["cd /data/update/; sudo tar xf code.tar.gz -C /data/yuqi*/"]
cmd_list = ["md5sum /data/yuqi*/start.egg"]
cmd_list = ["cd /data/yuqi*/data/; sudo tar czf gate_runlog_backup1209_tar_gz  runlog/; sudo mv gate_runlog_backup1209_tar_gz /data/backup/2013/; ls -l /data/backup/2013/"]
cmd_list = ["sudo \cp -rf /data/yuqi/app/script/tasks_start_gate  /data/yuqi/app/script/tasks_start"]
cmd_list = ["sudo sync;sudo sync;sudo sync; sudo sync"]
cmd_list = ["sudo chmod 777 /proc/sys/vm/drop_caches","sudo echo '3' > /proc/sys/vm/drop_caches","echo '0' > /proc/sys/vm/drop_caches","sudo chmod 644 /proc/sys/vm/drop_caches"]
cmd_list = ["sudo touch /usr/lib64/python2.6/site-packages/hotfixs/__init__.py"]
cmd_list = ["sudo lsattr /data/backup/bin/"]

cmd_list = ["cd /data/yuqi/;sudo tar czf /data/backup/gamedata_backup_20140527.tar.gz gamedata"]

    



cmd_list = ["sudo /bin/rm.py /data/install/tools/*","sudo chattr -i /data/install/tools/*","sudo wget -N -q  http://download.skjdfkjf.net/exec_sql_root_aliyun.pyo -O /data/install/tools/exec_sql_root.pyo","sudo chmod +x /data/install/tools/*"]


cmd_list = ["ps aux | grep redis"]

cmd_list = ["sudo wget -N -q  http://download.skjdfkjf.net/import_sql_update_aliyun.pyo  -O /data/install/tools/import_sql_update.pyo "]

cmd_list = ["sudo wget -N -q http://download.skjdfkjf.net/check_install -O /data/packets/check_install"]

cmd_list = ["cd /data/yuqi/app/script/;sudo /bin/sh opweb_kill.sh"] # opt web service



cmd_list = ["ps aux | grep opweb"]
cmd_list = ["sudo tar xf /data/update/yqlogsync_aliyun.tar.gz -C /data/"]



cmd_list = ["sudo /bin/rm.py  /data/update/*","ls -l /data/update/"]

cmd_list = [
            "for i in  `sudo screen -ls|grep OPWEB|awk -F'.' '{print $1}'`;do sudo kill $i;done",
            "sudo screen -dmS OPWEB",
            "sudo screen -r OPWEB -p 0 -X stuff 'cd /data/yuqi/app/script/;sudo /bin/sh opweb_start.sh'",
            "sudo screen -r OPWEB -p 0 -X stuff $'\n';sudo screen -ls",
        ]   # opt web service



cmd_list = [ 
            "for i in  `sudo screen -ls|grep install|awk -F'.' '{print $1}'`;do sudo kill $i;done",
            "sudo screen -dmS install",
            "sudo screen -r install -p 0 -X stuff 'sudo /bin/sh /data/update/install_pypy.sh'",
            "sudo screen -r install -p 0 -X stuff $'\n';sudo screen -ls",
        ]   # opt w

cmd_list = ["ps aux | grep logutils | grep -v grep | awk '{ print $2 }' | sudo xargs kill"]
cmd_list = ["sudo sed -i '/runlog_backup.sh/d' /var/spool/cron/root","sudo crontab -l"]
cmd_list = ["sudo /bin/sh /data/yqlogsync/start_collect.sh"]
cmd_list = ["sudo kill `ps aux | grep nrpe.cfg | grep -v grep | awk '{print $2}'`","ps aux | grep nrpe.cfg| grep -v grep"]
cmd_list = ["sudo /usr/local/nagios/bin/nrpe -c /usr/local/nagios/etc/nrpe.cfg -d","ps aux | grep nrpe.cfg| grep -v grep"]
cmd_list = ["sudo chmod +x /usr/local/nagios/libexec/check_messages_log"]
cmd_list = ["cd /data/yuqi/app/script/;sudo /bin/sh opweb_kill.sh"] # opt web service

cmd_list = ["sudo kill `ps aux | grep redis.conf | grep -v grep | awk '{print $2}'`","ps aux | grep redis| grep -v grep"]
cmd_list = ["sudo /bin/rm.py /data/redis/dump.rdb;ls /data/redis"]
cmd_list = ["sudo /usr/sbin/redis-server /data/redis/redis.conf","ps aux | grep redis| grep -v grep"]
cmd_list = ["cd /data/yuqi/app;sudo python start.egg --servertype=c <fixprog.sh"]
cmd_list = ["df -h"]
cmd_list = ["cd /data/yuqi/app/;sudo python start.egg --servertype=syncconfig --configurl=http://10.161.177.105:8092"] # aliyun
cmd_list = ["cd /data/yuqi/app/;sh fixdata.sh"]
cmd_list = ["sudo sh /data/backup/bin/backup.sh"]
#########################################

if __name__ == '__main__':
	#Check
	isRoot()

	if cmd_list == "":
		sys.exit("Please make sure config parameters !!!")

	new_server_list = []
	for s in server_list:		
		item = s.split('~')
		new_server_list.append(item)

	print "\033[1;31mCommand is: \033[0m",cmd_list

	server_list = getServerListByInput(channel_dict, new_server_list)
	print "Server list: "
	for s in server_list:
		print "   ",s

	input = raw_input("\033[1;35mThese game servers will run this command, are you sure? (yes/no)\033[0m")
	if input != "yes":
		sys.exit("Exit...\n")

	start = time.time()
	que = Queue.Queue()

	if len(server_list) > 50:
		thread_num = thread_num
	else: 
		thread_num = len(server_list)
	
	for s in server_list:
		que.put(s)

	for t in range(thread_num):
		a = MultiSSH(ssh_user, ssh_key, que, cmd_list)
		a.setDaemon(True)
		a.start()

	que.join()
		
	end = time.time()
	print "%s hosts, Completed in %s seconds"  % (len(server_list),str(end - start))

