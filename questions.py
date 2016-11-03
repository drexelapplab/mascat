# -*- coding: utf-8 -*-

import os
import question_node as qn
import linked_list
import re

class questioncard(linked_list.linkedlist):
	card0 = qn.questionnode("Need an access card? Is it for just ExCITe or is it for the building?",['excite', 'building'])
	card1 = qn.questionnode("What is your first name?")
	card2 = qn.questionnode("What is your last name?")
	card3 = qn.questionnode("If you have a Drexel ID, what is it?")
	#confirm = qn.questionnode("REPLACE ME")
	card0.setNextNode(card1)
	card1.setNextNode(card2)
	card2.setNextNode(card3)
	#card3.setNextNode(confirm)

	def __init__(self):
		self.head = self.card0

class questionconference(linked_list.linkedlist):
	conference0 = qn.questionnode("Trying to book a conference room? Do you want Call(seats 4), Orange(seats 6), or Gray(seats 14)?",['orange','gray','call'])
	conference1 = qn.questionnode("What day do you want the room? _(MM/DD/YYYY)_",['\d{2}/\d{2}/\d{4}'])
	conference2 = qn.questionnode("How long do you need the room for? _(HH:MM) Minutes will be rounded of to the nearest 30 minutes._",['\d{2}:\d{2}']) 
	conference0.setNextNode(conference1)
	conference1.setNextNode(conference2)

	def __init__(self):
		self.head = self.conference0

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

	def getTimes(self,service,date,calendar,time_needed):
		time_table = [True] * 48
		events = service.events().list(calendarId=calendar, timeMin=date+"T00:00:00-05:00", timeMax=date+"T23:59:59-05:00").execute()
		
		#FIRST PASS Checks only if a room is open or closed.
		for event in events['items']:
			start = event['start']['dateTime']
			end = event['end']['dateTime']

			start = re.sub('^\d{4}-\d{2}-\d{2}T', '', start)
			start = re.sub('$:\d{2}-\d{2}:\d{2}', '', start)

			end = re.sub('^\d{4}-\d{2}-\d{2}T', '', end)
			end = re.sub('$:\d{2}-\d{2}:\d{2}', '', end)

			s = start.split(':')
			e = end.split(':')

			ss = int(s[0])*2
			if s[1] == "30":
				ss += 1

			ee = int(e[0])*2
			if e[1] == "30":
				ee += 1

			for i in range(ss,ee):
				time_table[i] = False

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
		out = "You can start your meeting any time from "
		i = 0
		while i < len(time_table)-1:
			if time_table[i] == True:
				out += self.postTime(i) + " "
				while time_table[i] == True and i < len(time_table)-1:
					i += 1
				if (time_table[i] == False):
					out += "to " + self.postTime(i-1) + ", "
				else:
					out += "to " + self.postTime(i) + ", "
			else:
				while time_table[i] == False and i < len(time_table)-1:
					i += 1
		out.rstrip(', ')
		out += ". Any of these starting times look good to you?"
		print out

		return [time_table,out]

class questionconference2(linked_list.linkedlist):
	conference0 = qn.questionnode(carry_over[1],['yes','no'])
	conference1 = qn.questionnode("What day do you want the room? _(MM/DD/YYYY)_",['\d{2}/\d{2}/\d{4}'])
	conference2 = qn.questionnode("How long do you need the room for? _(HH:MM) Minutes will be rounded of to the nearest 30 minutes._",['\d{2}:\d{2}']) 
	conference0.setNextNode(conference1)
	conference1.setNextNode(conference2)

	def __init__(self):
		self.head = self.conference0
		