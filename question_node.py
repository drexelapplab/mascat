# -*- coding: utf-8 -*-

import os
import re

class questionnode:
	question = ""
	acceptable_answers = None
	next_node = None

	def __init__(self,question,aanswers=[]):
		self.question = question
		self.acceptable_answers = aanswers

	def getQuestion():
		return self.question

	def setQuestion(self,s):
		self.question = s

	def getAcceptableAnswers():
		return self.acceptable_answers

	def setAcceptableAnswers(self,a):
		self.acceptable_answers = a

	def getNextNode(self):
		return self.next_node

	def setNextNode(self,d):
		self.next_node = d

	def handleAnswer(self,sin,lout):
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
