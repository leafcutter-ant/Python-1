#!/usr/bin/env python
# -*- coding: utf8 -*-
# This scripts is used to check servers health status.
# Author steven
# Write 2011-12-12

### First: cat /etc/logrotate.d/syslog 
#/var/log/cron
#/var/log/maillog
#/var/log/messages
#/var/log/secure
#/var/log/spooler
#{
#    sharedscripts
#    create 0644 root root
#    postrotate
#        /bin/kill -HUP `cat /var/run/syslogd.pid 2> /dev/null` 2> /dev/null || true
#    endscript
#}

### Last: service rsyslog restart

import os, datetime, sys, paramiko,commands
os.chdir(os.path.dirname(sys.argv[0]))
sys.path.append("..")
from conf.config import server_list
#if commands.getoutput('whoami') != 'root':
#        sys.exit('Must be root run this script!')


today = datetime.date.today().strftime('%Y%m%d')

user = 'checkhealth'
#port = 23004
sshlog = 'ssh.log'
key = '../conf/health_keys'



def writeLog(file,content):
	f = open(file,'w')
	f.write(content)
	f.close()

def sshConn(host,user,key,log,content,port=22):    
    global today
    try:
        #paramiko.util.log_to_file(log)
        rsakey = paramiko.RSAKey.from_private_key_file(key)
        s = paramiko.SSHClient()
        s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        s.connect(hostname=host,port=port,username=user,pkey=rsakey)
        stdin,stdout,stderr = s.exec_command(content)
        return stdout.read()
        s.close()
    except Exception:
        return today + "--" + host + "Connect failed!"


if __name__ == '__main__':
    file = 'health-' + today +".log"
    pathname = '/data/checkhealth/'
    logfile = pathname + file
    if not os.path.exists(pathname):
		os.mkdir(pathname)

    f = open(logfile,'aw')
    for s in server_list:
		addr = s.split('~')[1]
		port = s.split('~')[2]
		#sys.exit('debug')
	
		f.write("############## Check " + addr + " Start ###############\n\n")
		f.write("------------------- Check messages --------------------\n")
		msg=sshConn(addr,user,key,sshlog,'grep -E "ERROR|error|Error|Fail|fail|FAIL|debug|DEBUG|conntrack|segfault" /var/log/messages',port)
		f.write(msg)

		f.write("\n\n------------------ Check Super user -------------------\n")
		su=sshConn(addr,user,key,sshlog,'/usr/bin/awk -F: \'$3==0{print $1}\' /etc/passwd',port)
		f.write(su)
		
		f.write("\n\n-------------------- Check  passwd --------------------\n")
		login=sshConn(addr,user,key,sshlog,'cat /etc/passwd | grep home | awk -F \':\' \'{print $1}\'',port)
		f.write(login)


		f.write("\n\n------------------ Check secure login -------------------\n")
		sshd=sshConn(addr,user,key,sshlog,'cat /var/log/secure|awk \'/Failed password/{print $(NF-3)}\'|sort|uniq -c|awk \'{print "sshd: "$2"="$1;}\'',port)
		f.write(sshd)
		vsftpd=sshConn(addr,user,key,sshlog,'cat /var/log/secure | awk \'/failure/{print $14}\' | sort | uniq -c | awk \'{print $2"="$1}\' | sed \'s/rhost=/vsftpd: /g\' ',port)
		f.write(vsftpd)

		f.write("\n\n------------------ Check rc.local   ---------------------\n")
		rc=sshConn(addr,user,key,sshlog,'cat /etc/rc.d/rc.local | grep -v ^#',port)
		f.write(rc)


		f.write("\n\n------------------ Check last login -------------------\n")
		login=sshConn(addr,user,key,sshlog,'/usr/bin/last | head -n 10',port)
		f.write(login)

f.close()

cmd="find /data/checkhealth -mtime +15 -name '*.log' -exec /bin/rm -f {} \;"
os.system(cmd)



