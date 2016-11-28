# -*- coding: utf-8 -*-

import os
import re

class binarynode:
	question = ""
	acceptable_answers = None
	left_child = None
	right_child = None

	def __init__(self,question,aanswers={}):
		self.question = question
		self.acceptable_answers = aanswers
		self.left_child = None
		self.right_child = None

	def handleAnswer(self,sin,lout): #string in, list out
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
					return 1
			return 0
