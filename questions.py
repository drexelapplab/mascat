# -*- coding: utf-8 -*-

import os
import question_node as qn
import linked_list
import re

from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build
from httplib2 import Http

import datetime

class questioncard(linked_list.linkedlist):
	def __init__(self):
		self.card0 = qn.questionnode("Need an access card? Is it for just ExCITe or is it for the building? _A building card is only neccessary if you need access between 8:00 PM and 8:00 AM, or on Sundays._",['excite', 'building'])
		self.card1 = qn.questionnode("What is your first name?")
		self.card2 = qn.questionnode("What is your last name?")
		self.card3 = qn.questionnode("If you have a Drexel ID, what is it? _The 8 digit ID_",['\d{8}'])
		#confirm = qn.questionnode("REPLACE ME")
		self.card0.next_node = self.card1
		self.card1.next_node = self.card2
		self.card2.next_node = self.card3
		#card3.setNextNode(confirm)
		self.head = self.card0
		self.answer_box = []
		self.extra_box = []
		self.confused_count = 0

class questionconferencestart(linked_list.linkedlist):
	def __init__(self):
		self.q0 = qn.questionnode("Need a conference room? Do you want to make a new reservation or edit an old one?",['new','edit'],self.finish)
		self.head = self.q0
		self.answer_box = []
		self.extra_box = []
		self.confused_count = 0

	def finish(self):
		if self.answer_box[0].lower() == "new":
			#STARTQUESTIONCONFERENCE
			print "new"
		elif self.answer_box[0].lower() == "edit":
			#STARTQUESTIONCONFERENCEEDIT
			print "edit"
		else:
			return 0

class questionconferenceedit(linked_list.linkedlist):
	CONFERENCE_CALENDAR_DICT = \
	{
		'orange':'3356ejp7m6494c2eaipsb4tnjk@group.calendar.google.com',
		'gray':'sm2h0b5q9eljcn7gbgcgpsl4fg@group.calendar.google.com',
		'call':'2sa29nliesjsodri8ss2ug80e4@group.calendar.google.com',
	}

	scopes = ['https://www.googleapis.com/auth/calendar']
	credentials = ServiceAccountCredentials.from_json_keyfile_name('Mascat-c45fe465c3ab.json', scopes=scopes)
	http_auth = credentials.authorize(Http())
	calendar_client = build('calendar', 'v3', http=http_auth)

	def __init__(self):
		self.q0 = qn.questionnode("Say 'yeah' if you're ready to edit!",['yeah'],self.getReservations)
		self.q1 = qn.questionnode("What do you ")
		self.head = self.q0
		self.answer_box = []
		self.extra_box = []
		self.confused_count = 0

	def getReservations(self):
		user_id = self.user_id
		event_box = []

		#dates should be from the current day, to the next year.
		date = datetime.date.today()
		date_plus_year = datetime.date(int(date.year)+1,date.month,date.day)

		date = str(date)
		date_plus_year = str(date_plus_year)

		print date
		print date_plus_year

		for room in self.CONFERENCE_CALENDAR_DICT:
			events = self.calendar_client.events().list(calendarId=self.CONFERENCE_CALENDAR_DICT[room], timeMin=date+"T08:00:00-05:00", timeMax=date_plus_year+"T19:59:59-05:00").execute()
			
			for event in events['items']:
				if event['summary'] == user_id:
					event_box.append(event)

		out = "You have reservations at: \n"
		for i in event_box:
			out += str(i['start']['dateTime'] + " to " + i['end']['dateTime'] + "\n")

		return [out]





class questionconference(linked_list.linkedlist):
	CONFERENCE_CALENDAR_DICT = \
	{
		'orange':'3356ejp7m6494c2eaipsb4tnjk@group.calendar.google.com',
		'gray':'sm2h0b5q9eljcn7gbgcgpsl4fg@group.calendar.google.com',
		'call':'2sa29nliesjsodri8ss2ug80e4@group.calendar.google.com',
	}

	scopes = ['https://www.googleapis.com/auth/calendar']
	credentials = ServiceAccountCredentials.from_json_keyfile_name('Mascat-c45fe465c3ab.json', scopes=scopes)
	http_auth = credentials.authorize(Http())
	calendar_client = build('calendar', 'v3', http=http_auth)

	def __init__(self):
		self.conference0 = qn.questionnode("Ok, let's set you up with a reservation then. Do you want Call(seats 4), Orange(seats 6), or Gray(seats 14)?",['orange','gray','call'])
		self.conference1 = qn.questionnode("What date do you want the room? *(MM/DD/YYYY)* _The date must be within now and next year._",['\d{2}/\d{2}/\d{4}'],self.checkDate)
		self.conference2 = qn.questionnode("How long do you need the room for? _(HH:MM) Minutes will be rounded off to the nearest 30 minutes._",['\d{1,2}:\d{2}'],self.getTimes) 
		self.conference3 = qn.questionnode("When do you want to start your meeting? _HH:MM AM/PM_",['\d{1,2}:\d{2}\s(am|pm)'],self.checkTime)
		self.conference0.next_node = self.conference1
		self.conference1.next_node = self.conference2
		self.conference2.next_node = self.conference3
		self.head = self.conference0
		self.answer_box = []
		self.extra_box = []
		self.confused_count = 0

	def postTime(self, i):
		out = ""
		if (i/2) == 0:
			out += "12"
		elif (i/2) > 12:
			out += str(i/2-12)
		else:
			out += str(i/2)
		if i % 2 != 0:
			out += ":" + "30 "
		else:
			out += ":" + "00 "
		if (i/2) < 12 or (i/2) == 24:
			out += "AM"
		else:
			out += "PM"
		return out

#room = CONFERENCE_CALENDAR_DICT[answer_box[0]]
#split = answer_box[1].split("/")
#date = split[2] + "-" + split[0] + "-" + split[1]
#cont = linked_question.getTimes(calendar_client,date,room,answer_box[2])

	def checkDate(self):
		date_in = self.answer_box[1]

		list = date_in.split("/")
		date_wanted = datetime.date(int(list[2]),int(list[0]),int(list[1]))

		if date_wanted.year - datetime.datetime.today().date().year > 0 or date_wanted < datetime.datetime.today().date():
			return [0]
		else:
			return [1]

	def getTimes(self):
		starting_hours = 24 # amount of XX:00 or XX:30 times in our available timeslot. (8AM to 8PM)
		
		calendar = self.CONFERENCE_CALENDAR_DICT[self.answer_box[0].lower()]
		
		split = self.answer_box[1].split("/")
		date = split[2] + "-" + split[0] + "-" + split[1]


		time_needed = self.answer_box[2]



		time_table = [True] * starting_hours
		events = self.calendar_client.events().list(calendarId=calendar, timeMin=date+"T08:00:00-05:00", timeMax=date+"T19:59:59-05:00").execute()
		
		#FIRST PASS Checks only if a room is open or closed at a given time.
		for event in events['items']:

			# Get the start and end dateTimes from google calender and strip them so only the time remains.
			start = event['start']['dateTime']
			end = event['end']['dateTime']

			start = re.sub('^\d{4}-\d{2}-\d{2}T', '', start)
			start = re.sub('$:\d{2}-\d{2}:\d{2}', '', start)

			end = re.sub('^\d{4}-\d{2}-\d{2}T', '', end)
			end = re.sub('$:\d{2}-\d{2}:\d{2}', '', end)


			# Split the times into hours and minutes
			s = start.split(':')
			e = end.split(':')

			ss = int(s[0])*2
			if s[1] == "30":
				ss += 1

			ee = int(e[0])*2
			if e[1] == "30":
				ee += 1

			for i in range(ss,ee):
				time_table[i-16] = False

		#SECOND PASS Checks if the room is open for the time requested.
		t = time_needed.split(':')
		hours = int(t[0])
		minutes = int(t[1])
		thirtyblocks = (hours*2) + (minutes/30) #an hour counts as 2 thirty minute blocks, 30 minutes counts as 1 thirty minute block. Add them together.
		for i in range(0,len(time_table)):
			if time_table[i] == False:
				pass
			else:
				if(i+thirtyblocks > len(time_table)):
					for j in range(i,len(time_table)):
						time_table[j] = False
				else:
					ceiling = i+thirtyblocks
					for j in range(i,ceiling):
						if time_table[j] == True:
							pass
						else:
							for k in range(i,ceiling):
								time_table[k] = False

		#OUTPUT BUILDING
		out = "You can start your meeting at these times:\n "
		i = 0
		while i < len(time_table)-1:
			if time_table[i] == True:
				out += "*" + self.postTime(i+16)
				start_i = i
				while time_table[i] == True and i < len(time_table)-1:
					i += 1
				if (time_table[i] == False):
					if i-1 == start_i:
						out += "*,\n"
					else:
						out += " to " + self.postTime(i-1+16) + "*" + ",\n"
				else:
					out += " to " + self.postTime(i+16) + "*" + ",\n"
			else:
				while time_table[i] == False and i < len(time_table)-1:
					i += 1
		out = out[:-2]
		out += "."


		self.extra_box.append(time_table)
		return [out,time_table]
		

	def checkTime(self):
		time_start = self.answer_box[3]
		time_duration = self.answer_box[2]

		time_table = self.extra_box[0]

		start_split = time_start.split(":")
		ss_hour = int(start_split[0])
		ss_split = start_split[1].split(" ")
		ss_minute = ss_split[0]
		ss_meridiem = ss_split[1]

		if ss_meridiem.lower() == "pm" and ss_hour != 12:
			ss_hour += 12

		time_start_index = (ss_hour*2)-16

		if ss_minute == "30":
			time_start_index += 1


		t = time_duration.split(':')
		hours = int(t[0])
		minutes = int(t[1])
		thirtyblocks = (hours*2) + (minutes/30) #an hour counts as 2 thirty minute blocks, 30 minutes counts as 1 thirty minute block. Add them together.

		if time_table[time_start_index] == False:
			return [0]
		elif time_table[time_start_index] == True:
			self.calendarAddEvent()
			return [1]



	def calendarAddEvent(self):
		# event_info: [summary, location, start, end]

		event_info = self.answer_box
		room = self.CONFERENCE_CALENDAR_DICT[event_info[0].lower()]
		user_id = self.user_id

		split0 = event_info[1].split("/")
		date = split0[2] + "-" + split0[0] + "-" + split0[1]

		split1 = event_info[3].split(" ")
		time_prelim = split1[0].split(":")
		hour = int(time_prelim[0])
		minute = int(time_prelim[1])

		if split1[1].lower() == "pm" and hour != 12:
			hour += 12

		split2 = event_info[2].split(":")
		ehour = int(split2[0])
		eminute = int(split2[1])

		end_minute = minute + eminute
		end_hour = hour + ehour

		if end_minute == 60:
			end_minute = 0
			end_hour += 1

		if end_hour > 23:
			end_hour += -24


		time_start = "T" + str(hour) + ":" + str(minute) + ":00-05:00"
		time_end = "T" + str(end_hour) + ":" + str(end_minute) + ":00-05:00"

		event = {
		  'summary': user_id,
		  'location': event_info[0].lower(),
		  'description': 'Conference Room Reservation',
		  'start': {
		    'dateTime': date+time_start,
		    'timeZone': 'America/New_York',
		  },
		  'end': {
		    'dateTime': date+time_end,#'2016-10-28T19:00:00-05:00'
		    'timeZone': 'America/New_York',
		  },
		  'recurrence': [
		    'RRULE:FREQ=DAILY;COUNT=1'
		  ],
		  #'attendees': [
		    #{'email': 'lpage@example.com'},
		    #{'email': 'sbrin@example.com'},
		  #],
		  #'colorId':'6',
		  'reminders': {
		    'useDefault': False,
		    'overrides': [
		      {'method': 'email', 'minutes': 24 * 60},
		      {'method': 'popup', 'minutes': 10},
		    ],
		  },
		}
		event = self.calendar_client.events().insert(calendarId=room, body=event).execute()

		#tsvFile = open("conference_reservations.tsv", "a")
		#out = csv.writer(tsvFile, delimiter='\t')
		#out.writerow([user_id,event['id']])
		#tsvFile.close()