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
		print("sin " + str(sin))
		print(self.acceptable_answers)
		if sin == None:
			print "no answer"
			return 0
		elif self.acceptable_answers is None:
			lout.append(sin)
			print(lout)
		elif sin in self.acceptable_answers:
			print "good answer"
			lout.append(sin)
			print(lout)
		else:
			print "bad answer"
			return 0
