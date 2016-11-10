# -*- coding: utf-8 -*-

import os
import re

class questionnode:
	question = ""
	acceptable_answers = None
	next_node = None
	to_run = None

	def __init__(self,question,aanswers=[],to_run=None):
		self.question = question
		self.acceptable_answers = aanswers
		self.to_run = to_run


	# -1: EXIT request
	#  0: No answer to read
	#  1: Success answer
	#  2: Failure answer
	def handleAnswer(self,sin,lout):
		if sin == "EXIT":
			return -1
		r = []
		for i in range(0,len(self.acceptable_answers)):
			r.append(re.compile(self.acceptable_answers[i]))
		if sin == None:
			return 0
		elif len(r) == 0:
			lout.append(sin)
		else:
			for i in range(0,len(r)):
				if r[i].search(sin.lower()) != None:
					lout.append(sin)
					#if self.to_run != None:
						#return self.to_run()
					return 1
			return 0
