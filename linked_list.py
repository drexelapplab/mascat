# -*- coding: utf-8 -*-

import os

class linkedlist:
	head = None
	answer_box = []

	def __init__(self,head=None):
		self.head = head
		self.answer_box = []
		self.user_id = ""

	def next(self):
		if self.head.next_node != None:
			self.head = self.head.next_node
		else:
			return 0