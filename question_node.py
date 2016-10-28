# -*- coding: utf-8 -*-

import os

class questionnode:
	question = ""
	acceptable_answers = None
	next_node = None

	def __init__(self,question,aanswers=None):
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
		if sin == None:
			return 0
		elif self.acceptable_answers is None:
			lout.append(sin)
		elif sin.lower() in self.acceptable_answers:
			lout.append(sin)
		else:
			return 0
