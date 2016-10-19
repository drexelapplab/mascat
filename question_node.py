import os

class questionnode:
	entry_words = []
	prompt = ""
	paths = {}

	def __init__(self,e,p,c):
		self.entry_words = e
		self.prompt = p
		self.paths = c

	def getPrompt():
		return self.prompt

	def setPrompt(s):
		self.prompt = s

	def getEntryWords():
		return self.entry_words

	def setEntryWords(a):
		self.entry_words = a

	def getChildNodes():
		return self.paths

	def setChildNodes(d):
		self.paths = ds

	def askQuestion():
		return self.prompt

	def handleAnswer(s):
		if(isinstance(self.paths[s], questionnode)):
			f
		elif(isinstance(self.paths[s], Action)):
			f
