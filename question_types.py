# -*- coding: utf-8 -*-

import os
import question_node
import linked_list
import re

class seriesform(linked_list.linkedlist):

	__init__(self,questions,variant,confirm=True):
		self.questions = questions
		self.variant = variant
		self.confirm = confirm

		if self.confirm == True:
			choice("Does this look correct?")

	def confirmForm(self):
		print "AOSDF"

	def send(self):
		if self.variant == "toUser":
			out = "Hello, I got a card request.\n" \
			+ "*Type:* " + answer_box[0] + "\n" \
			+ "*First Name:* " + answer_box[1] + "\n" \
			+ "*Last Name:* " + answer_box[2] + "\n" \
			+ "*Drexel ID:* " + answer_box[3]
			messageOne(out,"U0G0CFKB2")#U04JCJPLY U0G0CFKB2


class choice(question_node.questionnode):

	__init__(self,choices,variant):
		self.choices = choices
		self.variant = variant