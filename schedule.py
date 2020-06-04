# queue strategy
# foreach task
#  schedule it at the appropriate time
#  use schedule.py
#  schedule.py sub-main will take a config and by default print the next occurance
# of each task.  Should also include an optional time duration, if so, print the schedule
# for the given duration


#myapi is Mark's modified REST script
import myapi

import datetime
import dateutil.parser
import json
import StringIO
import time
import traceback

from dateutil.tz import tzlocal, tzwinlocal
import sys
import sched
from parse_config import Parse

count = 0

def main(eachtask, name, eachssid):
	global count
	count += 1
	print
	print("Main reached", count)
	print ("NOW: %s" % time.ctime(time.time()))
	print "TASK: ", str(name)
	print "SSID: ", str(eachssid["name"])
	print "Result URL: "

	#reschedule should be sent an offset time
	#s.reschedule(eachtask, name, eachssid)
	myapi.main(eachtask["TASK"])
	print




class Schedule:

	def __init__(self, config_file):
		self.p = Parse(config_file)
		self.s = sched.scheduler(time.time, time.sleep)


	#schedules for all tasks at the start
	#"main" needs to be replaced with loop that tests each SSID
	#returns schedule queue
	
	def initial_schedule(self, given_time=time.time()):
		TASKS = self.p.pSSID_task_list()

		for eachtask in TASKS:
			cron_list = eachtask["Sched"]
			ssid_list = eachtask["SSIDs"]
			name = eachtask["Name"]

			for eachssid in ssid_list:				
				for eachcron in cron_list:
					schedule_time = time.time() + eachcron.next(given_time)
					self.s.enterabs(schedule_time, 1, main, argument = (eachtask,name,eachssid,))

    	
		


    #this function should be called right after testing loop is reached
    #reschedule needs an offset

	def reschedule(self,given_task, name, given_ssid, given_time=time.time()):
		print("reschedule")
		cron_list = given_task["Sched"]
		name = given_task["Name"]
		for eachcron in cron_list:
			schedule_time = time.time() + eachcron.next(given_time)
			self.s.enterabs(schedule_time, 1, main, argument = (given_task,name,given_ssid,))




	def print_queue(self, given_time=time.time()):
		#print self.s.queue

		print
		print
		print
		print "Now: ", time.ctime(time.time())
		print "given_time: ", time.ctime(given_time)
		print
		print
		
		# task = []
		# ssid = []

		#the next scheduled run for unique task/ssid comb
		temp = {}
		for i in self.s.queue:
			if i.argument[1] not in temp:
				temp[i.argument[1]] = []
				temp[i.argument[1]].append(i.argument[2]["name"])
				print ("%s: " % time.ctime(i.time))
				print("----Task: %s" % i.argument[1])
				print("----SSID: %s" % i.argument[2]["name"])
				print
			elif i.argument[2]["name"] not in temp[i.argument[1]]:
				temp[i.argument[1]].append(i.argument[2]["name"])
				print ("%s: " % time.ctime(i.time))
				print("----Task: %s" % i.argument[1])
				print("----SSID: %s" % i.argument[2]["name"])
				print

	def run(self):
		print("RUN")
		self.s.run()

		






if __name__ == '__main__':

	def time_input_error():
		print "please provide a valid time: \
			\"[yyyy-mm-dd-hh-min]\" "


	start = time.time()


	if len(sys.argv) < 2:
		print "ERROR: Provide JSON file and optional start time"
		print "USAGE: python %s filename.json [yyyy-mm-dd-hh-min]" % sys.argv[0]
		exit(1)
	elif len(sys.argv) == 3: 
		#check for valid time range and parse it
		start_time = sys.argv[2]

		#TODO: check number of options provided
		#num_opts = time_range.count("-")

		try:
			#all strings	
			year = (start_time.split("-")[0]).lstrip().rstrip()
			month = (start_time.split("-")[1]).lstrip().rstrip()
			day = (start_time.split("-")[2]).lstrip().rstrip()
			hour = (start_time.split("-")[3]).lstrip().rstrip()
			minute = (start_time.split("-")[4]).lstrip().rstrip()
		except:
			time_input_error()
			print(traceback.print_exc())
			exit(1)
		
		
		#TODO: are they all digits?


		start_str = year+" "+month+" "+day+" "+hour+" "+minute

		try:
			start = time.strptime(start_str, "%Y %m %d %H %M")
			start = time.mktime(start)
			print("start", time.ctime(start))
		except:
			time_input_error()
			print(traceback.print_exc())
			exit(1)

		time_given = True




	config_file = open(sys.argv[1], "r")
	s = Schedule(config_file)
	s.initial_schedule(start)
	s.print_queue(start)
	s.run()

	exit(0)
