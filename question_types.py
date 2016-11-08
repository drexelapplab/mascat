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


class choice(question_node.questionnode):

	__init__(self,choices,variant):
		self.choices = choices
		self.variant = variant