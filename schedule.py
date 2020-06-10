
#myapi is Mark's modified REST script
import myapi

import datetime
import dateutil.parser
import json
import StringIO
import time
import traceback
import daemon

from dateutil.tz import tzlocal, tzwinlocal
import sys
import sched
from parse_config import Parse
import syslog
import argparse

count = 0


# def custom_time():
# 	temp_time = 0
# 	temp_time = time.gmtime(time.time())
# 	return time.mktime(temp_time)



def run_schedule(eachtask, name, eachssid, eachcron):
	global count
	count += 1
	print
	print("Main reached", count)
	print ("NOW: %s" % time.ctime(time.time()))
	print ("TASK: ", str(name))
	print ("SSID: ", str(eachssid["name"]))
	print ("Result URL: ")

	#reschedule should be sent an offset time
	#s.reschedule(eachtask, name, eachssid)
	myapi.main(eachtask["TASK"])
	print




class Schedule:

	def __init__(self, parsed_file):
		self.p = parsed_file
		self.s = sched.scheduler(time.time, time.sleep)


	

	#this function should be called right after testing loop is reached
    #reschedule needs an offset
    #reschedule takes care of specific specific ssid for a specific task
	def reschedule(self,given_task, given_ssid, given_cron, given_time=time.time()):
		set_time = time.time()
		if given_time > time.time():
			set_time = given_time
		
		name = given_task["Name"]
		schedule_time =  set_time  + given_cron.next(set_time)

		self.s.enterabs(schedule_time, 1, run_schedule, argument = (given_task,name,given_ssid,given_cron))


	def print_event(self, event, prefix=""):
		print_syslog = prefix + time.ctime(event.time) + \
			" SSID: " + event.argument[2]["name"] + \
			" Test: " + event.argument[1]

		print (print_syslog)

		syslog.openlog("SCHEDULE", 0, syslog.LOG_LOCAL3)
		syslog.syslog(syslog.LOG_DEBUG, print_syslog)
		syslog.closelog()


	def print_queue(self):
		for i in self.s.queue:
			self.print_event(event=i)

	#schedules for all tasks at the start
	#"main" needs to be replaced with loop that tests each SSID
	#returns schedule queue
	#if this is called again insted of rschedule, the task that have not run will be scheduled twice for the same time
	def initial_schedule(self, given_time=time.time()):
		TASKS = self.p.pSSID_task_list()

		for eachtask in TASKS:
			cron_list = eachtask["Sched"]
			ssid_list = eachtask["SSIDs"]
			name = eachtask["Name"]

			for eachssid in ssid_list:
				for eachcron in cron_list:
					self.reschedule(eachtask, eachssid, eachcron, given_time)

		self.s.queue
    	
	


	def initial_print(self, given_time=time.time()):
		#print self.s.queue
		print ("Now: %s" % time.ctime(time.time()))
		print ("start: %s" % time.ctime(given_time))
		

		#the next scheduled run for unique task/ssid comb
		temp = {}
		for i in self.s.queue:
			if i.argument[1] not in temp:
				temp[i.argument[1]] = []
				temp[i.argument[1]].append(i.argument[2]["name"])
				self.print_event(i, "First: ")
			elif i.argument[2]["name"] not in temp[i.argument[1]]:
				temp[i.argument[1]].append(i.argument[2]["name"])
				self.print_event(i, "First: ")

	


	def duration_print(self, given_time, duration):
		#both need to be in seconds
		end_time = time.time() + 3600

		#create a custom dict where each task has additional
		#attribut 'prev', previously scheduled time

		temp2 = []
		for i in self.s.queue:
				test = {}
				test["i"] = i
				test["prev"] = i.time
				temp2.append(test)

		
		#treat temp2 i.time as prev		
		fake_time = 0
		print("ENDTIME: ", time.ctime(end_time))
		while fake_time < end_time:
			min_time = end_time
			for test in temp2:

				curr_time = test["prev"] + test["i"].argument[3].next(test["prev"])
				test["prev"] = curr_time
				min_time = min(min_time, curr_time)

				if curr_time <= end_time:
					print("FAKESCHED: ", time.ctime(curr_time))
					self.s.enterabs(curr_time, 1, run_schedule, argument = test["i"].argument)
			
			fake_time = min_time


		#print
		temp = {}
		for i in self.s.queue:
			if i.argument[1] not in temp:
				temp[i.argument[1]] = []
				temp[i.argument[1]].append(i.argument[2]["name"])
				self.print_event(i, "First: ")
			elif i.argument[2]["name"] not in temp[i.argument[1]]:
				temp[i.argument[1]].append(i.argument[2]["name"])
				self.print_event(i, "First: ")
			else:
				self.print_event(i, "Next: ")

	
	@property
	def get_queue(self):
		return self.s.queue

	
	def empty(self):
		return self.s.empty()

	def pop(self, event):
		self.s.cancel(event)


	def run(self):
		print("RUN")
		self.s.run()

		


def time_input_error():
	print ("please provide a valid time: \
			\"[yyyy-mm-dd-hh-min]\" ")



def main():

	parser = argparse.ArgumentParser(description='output options')
	parser.add_argument('file', action='store',
	  help='json file')
	parser.add_argument('--start', action='store',
	  help='start time')
	parser.add_argument('--duration', action='store',
	  help='duration/timelength')

	args = parser.parse_args()


	

	if(args.duration == None):
		duration = 3600 #default 1 hour for now
	else:
		duration= args.duration #assuming entered as seconds
	

	if(args.start == None):
		start = time.time()
	else:
		#check for valid time range and parse it
		start_time = args.start

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




	config_file = open(args.file, "r")
	p = Parse(config_file)
	s = Schedule(p)
	s.initial_schedule(start)

	if(args.duration == None):
		s.initial_print(start)
	else:
		s.duration_print(start, duration)
		
	
	s.run()

	exit(0)


if __name__ == '__main__':
	with daemon.DaemonContext(stdout=sys.stdout, stderr=sys.stderr, working_directory='/home/vagrant'):
		main()


