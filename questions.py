# -*- coding: utf-8 -*-

import os
import question_node as qn
import linked_list

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
	conference0 = qn.questionnode("Trying to book a conference room? Do you want Orange, Gray, or Call?")
	conference1 = qn.questionnode("What day do you want the room? (MM/DD/YYYY)",['\d{2}/\d{2}/\d{4}'])
	conference2 = qn.questionnode("How long do you need the room for?",['\d{2}:\d{2}\s*(AM|PM)'])
	conference0.setNextNode(conference1)
	conference1.setNextNode(conference2)

	def __init__(self):
		self.head = self.conference0

	def getTimes(service,date):
		events = service.events().list(calendarId='primary', timeMin=date+"T08:00:00-05:00", timeMax=date+"T20:00:00-05:00", pageToken=page_token).execute()


		