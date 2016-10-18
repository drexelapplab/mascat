import os

class questionnode:
	entry_words = []
	prompt = ""
	child_nodes = {}

	def __init__(self,e,p,c):
		self.entry_words = e
		self.prompt = p
		self.child_nodes = c

	def getPrompt():
		return self.prompt

	def setPrompt(s):
		self.prompt = s

	def getEntryWords():
		return self.entry_words

	def setEntryWords(a):
		self.entry_words = a

	def getChildNodes():
		return self.child_nodes

	def setChildNodes(d):
		self.child_nodes = ds
