# -*- coding: utf-8 -*-

import os

class linkedlist:
	head = None

	def __init__(self,head=None):
		self.head = head

	def out():
		return 

	def next(self):
		if self.head.getNextNode() != None:
			self.head = self.head.getNextNode()
		else:
			return 0

	def preConfirm(self,lin):
		for i in range(0,len(lin)-1):
			print(lin[i])
		print("Does this look right?")