# -*- coding: utf-8 -*-

import os

class linkedlist:
	head = None
	answer_box = []

	def __init__(self,head=None):
		self.head = head
		self.answer_box = []
		self.user_id = ""
		self.confused_count = 0