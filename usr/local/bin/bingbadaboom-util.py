#! /usr/bin/env python


import time\
import optparse\
import sys\
import yaml\
import os
from bingbadaboom_module import *


parser = optparse.OptionParser()

parser.usage="%prog [options]\n\nThis tool allows you to calculate the Markus-index (stability index) for your system based on the hours it has been running and the crashes it has in the same time. Why Markus-Index? Markus is the person that cares about that your systems don't crash and if, that it is called out. Shows shitty buggy OS code.\nWritten by Markus Bawidamann D20130901."


options, args = parser.parse_args()

total_file = "/etc/bingbadaboomd/bingbadaboomd_total.yml"

#total_runtime= options.duration			#total runtime in hours

def load_stats_file():
	#load file 1
	f = open(total_file, "r")
	total_yaml=f.read()
	total = yaml.load(total_yaml)
	f.close()
	return total
	

#check if yaml config file is already there
if os.path.isfile(total_file):
	#load it, continue where we left off
	total = load_stats_file()
else:
	#file is not there, not loading from yaml, so we create an empty object
	total = {"total_hours": 11, "minutes": 0, "total_crashes": 1, "crash_dates": ['2013', '08', '27', '23', '52']}


if total["total_crashes"] == 0:
	crashes = 1
else:
	crashes = total["total_crashes"]
hours = float(total["total_hours"])



h = float(hours)
d = float(hours/24)
w = float(d/7)
m = float(w/4)
y = float(m/12)



print("Statistics:")
print("=======================")
print("Your system was running a total of " + str(hours) + " hours")
if d >= 1:
	print "or " +str(d) +" days"
	
if w >= 1:
	print "or " +str(w) +" weeks"

if m >= 1:
	print "or " +str(m) +" months"

if y >= 1:
	print "or " +str(y) +" years" 


print "You experienced " + str(total["total_crashes"]) + " crash(es) in that time."
print "That is an average of "
print str(total["total_crashes"]/d) + " crashes per day"
print str(total["total_crashes"]/w) + " crashes per week"
print str(total["total_crashes"]/m) + " crashes per month"
print str(total["total_crashes"]/y) + " crashes per year"

print "Your Markus-index (stability index) is " + str(hours/crashes+1)
