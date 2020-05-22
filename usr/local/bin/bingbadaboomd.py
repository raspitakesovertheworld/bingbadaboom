#! /usr/bin/env python
import os, signal, sys, time, psutil, yaml, syslog
from bingbadaboom_module import *


#Bingbadaboomd crash notifier daemon, written by Markus Bawidamann 2013
#Don't let any OS get away with fatal crashes anymore, know your 
#Markus-Index (system stability index) and compare it with other systems
#Use bingbadaboom-util to see calculate Markus-Index
#Authors notice:
#Yes, I'm using tabs. Convert to spaces if you want that. I always write my scripts with tabs 
#as that is why tabs are for, welcome in the 21st century! ;-)
#Systematically more correct way for me, even if in violation of Python PEP

#I wrote bingbadaboom because I got tired of systems crashing on me and people pretenting 
#OS were more stable than I knew they were. NOW you can go and compare them, 
#see the hours to fatal crash ratio (Markus-Index)
#I value system stability over all else, how can you use a tool to work when you 
#can't rely on it? That is why I love Debian and use it everywhere. I'm so curious 
#about the Ubuntu VS Debian Markus-Index comparison.
#Yes, Debian uses older code, BUT it does not let you down!
#In a fickle uncertain and unstable world, there are a few things that you can count on!

#functional description: 
#maintain total object in memory, and write them out via yaml (and reload them 
#on program start). Count the minutes and hours real runtime (allows for hibernation and sleep mode) and 
#notes the crashes that occur

#Android:
#lockfile="/sdcard/sl4a/bingbadaboomd/bingbadaboomd.lock"
#total_file = "/sdcard/sl4a/bingbadaboomd/bingbadaboomd_total.yml"
#log_file = "/sdcard/sl4a/bingbadaboomd/bingbadaboom.log"

#TODOS:
#include standard BW functions, load and save yml config file, put that into an external module, all input and output
#has to be contained...
#create debug_print(debug) function to be dependent on debug flag


#Linux:
lockfile="/etc/bingbadaboomd/bingbadaboomd.lock"
pidfile = "/var/run/bingbadaboomd.pid"
total_file = "/etc/bingbadaboomd/bingbadaboomd_total.yml"
log_file = "/var/log/bingbadaboom.log"


def touch_lock_file():
	os.utime(lockfile, None)

def handler(signum, frame):
	print 'Bingbadaboom: Signal handler called with signal', signum
	print "Removing lock file..."
	os.remove(lockfile)
	os.remove(pidfile)
	log_event(syslog.LOG_NOTICE,"Bingbadaboom: clean shutdown")
	sys.exit(0)

def write_stats_file():
	total_yaml=yaml.dump(total)

	#critical: write first file
	f = open(total_file,"w")
	f.write(total_yaml)
	f.close()
	
def load_stats_file():
	#load file 1
	f = open(total_file, "r")
	total_yaml=f.read()
	total = yaml.load(total_yaml)
	f.close()


	return total
	
def log_event(priority, log_string):
	#todo: use syslogd, create custom log file, a lot more trickier than expected
	#so writing logs by hand for now
	f=open(log_file,"a")
	converted_time=time.strftime("D%Y%m%d.%H%M", time.localtime())
	f.write(converted_time+" "+ log_string+"\n")
	f.close()
	
	#syslog logging
	syslog.openlog("bingbadaboom",syslog.LOG_KERN)
	syslog.syslog(priority, converted_time+" "+ log_string)

def do_heartbeat(netdevice,netmodule):
	#this flashes the NIC LED for 2 seconds as a heart beat
	#do this whole bit 6 times
	start_time=time.time()
	for cnt in range(0,6):
	
		#try opening netdev, if fail, remove and load module again
		returncode = os.system("ethtool -p "+ netdevice + " 2")
	
		if returncode != 0:
			print "could not open netdevice, trying module "+ netmodule + " and then opening netdevice "+ netdevice
			os.system("modprobe -r "+netmodule+ "; modprobe "+netmodule +" ; ethtool -p "+netdevice+" 2")
		time.sleep(8)
	end_time=time.time()


#startup

#register signal handler, to terminate gracefully
signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGINT, handler)



#check if yaml config file is already there
if os.path.isfile(total_file):
	#load it, continue where we left off
	total = load_stats_file()
else:
	#file is not there, not loading from yaml, so we create an empty object
	total = {"total_hours": 0, "minutes": 0, "total_crashes": 0, "crash_dates": [],"heartbeat":True,"netdevice":"etho","netmodule":"e1000e"}



#pid handling, is the daemon running already?
pid = str(os.getpid())

if os.path.isfile(pidfile):
	print "pidfile already exists"
	pf = open(pidfile)
	pidstr = pf.read()
	print pidstr
	if psutil.pid_exists(int(pidstr)):
		print "process is already running, abort!"
		sys.exit()
	else:
		print "pid file exists, but process crapped up and left it, erasing it"
		os.remove(pidfile)
		file(pidfile, 'w').write(pid)
else:
	file(pidfile, 'w').write(pid)




#check if lock file is there
if os.path.exists(lockfile):
	log_event(syslog.LOG_NOTICE,"Bingbadaboom: System Startup")
	print "We had a crash!"
	mod_time_float = os.path.getmtime(lockfile)
	
	#log the crash in the log
	
	mod_time_real = time.ctime(mod_time_float)
	mod_time_struct = time.strptime(mod_time_real)
	
	mod_time_string = time.strftime("D%Y%m%d.%H%M", mod_time_struct)
	
	
	log_event(syslog.LOG_EMERG,"System crashed on or around "+mod_time_string)
	total["total_crashes"]= total["total_crashes"]+1



	#make an empty list and then add all time fields of the crash date
	l1 = []
	l1.append(time.strftime("%Y", mod_time_struct))
	l1.append(time.strftime("%m", mod_time_struct))
	l1.append(time.strftime("%d", mod_time_struct))
	l1.append(time.strftime("%H", mod_time_struct))
	l1.append(time.strftime("%M", mod_time_struct))
	
	l_tmp = total["crash_dates"]
	l_tmp.append(l1)
	
	#add the new list to the dict
	total["crash_dates"]=l_tmp

	print total

#If lock file is missing, there was no crash

else:
	print "Lockfile was not there = no crash"
	print "Creating file..."
	log_event(syslog.LOG_NOTICE,"CrashNotifier: System Startup")
	f= open(lockfile,"w")
	f.close()

#main daemon loop
while True == True:
	
	touch_lock_file()
	
	#is heartbeat even wanted, let's check
	
	if total["heartbeat"]== True:
		do_heartbeat(total["netdevice"],total["netmodule"])
	else:
		#no heartbeat wanted, we just wait one minute
		time.sleep(60)
	
	total["minutes"] = total["minutes"] + 1

	if total["minutes"] == 60:
		total["total_hours"]= total["total_hours"]+1
		total["minutes"] = 1
	write_stats_file()





