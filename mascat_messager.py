# -*- coding: utf-8 -*-

import os
import time
import urllib2
import random
import datetime
import csv
from slackclient import SlackClient
from enum import Enum
import shutil
import questions
from socket import error as SocketError

from websocket import *
import requests

BOT_ID = os.environ.get("BOT_ID")

#constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"

#global
CURRENT_DATE = datetime.date.today()
PREVIOUS_REMINDER_DATE = datetime.date.today()
THREAD_USER_LIST = {} #Users in this list are in a conversation within a thread, and should be ignored by the regular RTM reader.
CONFUSED_USER_LIST = {}


class Action(Enum):
	# Don't publicise these, these are either used by the program only
	newUser = 1
	remind = 2

	# Mascat normal message actions
	NORMAL = 100
	help = 101
	#event = 102
	printing = 103
	card = 104
	conference = 105
	restroom = 106
	payroll = 107
	prout = 108
	dragonfly = 109
	airplay = 110
	extension = 111
	hours = 112
	tour = 113
	kitchen = 114
	applab = 115

	# Mascat unlisted message actions (message type actions that users won't directly call, or are easter egg messages)
	UNLISTED = 200
	hello = 201
	pretty = 202
	generic = 203
	redirect = 204
	continueLinkedQuestion = 205

CHANNEL_DICT = \
{
	'general':'C0257SBTA',
	'orange':'',
	'grey':''
}

MONTH_DICT = \
{ 	
	1:'January', 
	2:'February',
	3:'March',
	4:'April',
	5:'May',
	6:'June',
	7:'July',
	8:'August',
	9:'September',
	10:'October',
	11:'November',
	12:'December' 
}

GENERIC_DICT = \
{
	1:"Meong.",
	2:"Miau.",
	3:"Mjau.",
	4:"Miaou.",
	5:"喵喵.",
	6:"ニャー.",
	7:"야옹.",
	8:"Мияу-мияу.",
	9:"Mjá.",
	10:"Meow.",
	11:"מְיָאוּ.",
	12:".مُواَء",
	13:"เมี้ยว.",
	14:"Miao.",
}

GREETING_DICT = \
{
	1:"Hi",
	2:"Hey",
	3:"Yo",
	4:"Hoy",
}

MORNING_DICT = \
{
	1:"It's too early in the morning for me.",
	2:"Did you eat breakfast?",
	3:"I wanted to sleep in.",
	4:"Are you still tired too?",
	5:"I'd drink coffee but I'd probably get sick. Cats are sensitive to caffeine, you know.",
	6:"Do you think if I pressed salmon roe into a cup, I could drink it as if it were coffee? That's my dream, to drink a cup in the morning, standing in solitude with the foreman, watching the sun rise over the site, the workers carding in for the morning grind below. The cool wind on my face, the smell of iron and in the air... Huh? We're not a construction company?",
	7:"Do you think if I pressed salmon roe into a cup, I could drink it as if it were coffee? That's my dream, to drink a cup in the morning, alone in my office, the air already musty with cigar smoke. Though it's a shining day outside, only slivers of sun can peek through the shutters. It's still early in the morning, but someone's already rapping on the door, wailing about... Huh? We're not a private investigation agency?",
	8:"Do you think if I pressed salmon roe into a cup, I could drink it as if it were coffee? That's my dream, to drink a cup in the morning, in the pit with the crew, and old Neubauer's giving me the overview I've already heard a hundred times. I give him a smile though, because you can't deny Alfred, he's a good manager and an even greater man. He traces out Reims-Gueux again with his finger, and I follow, but we already know. We've been ready. He gives me a slap on the shoulder as I pull the goggles over my eyes and... Huh? We're not a professional racing team?",

}

NOON_DICT = \
{
	1:"Do you ever get tired after lunch?",
	2:"What did you eat for lunch?",
	3:"Look at you, still at it. You're my role model.",
	4:"Guess what I had for lunch. It was salmon. I'm saving the roe for tonight. :gilegs:",
	5:"After lunch is when I get the most tired during the day. Lucky for me I don't have to work. Maybe I'll take a nap? You should keep doing whatever you were doing though.",
}

LATE_DICT = \
{
	1:"Isn't it almost time to go home?",
	2:"Is the sun setting?",
	3:"What are you getting for dinner?",
	4:"In a perfect world, I'd eat salmon roe every night. :gilegs:",
	5:"Stay safe out there.",
}

NIGHT_DICT = \
{
	1:"Try not to use your phone in bed. It'll take longer to fall asleep that way.",
	2:"Take it easy, yeah?",
	3:"Getting a full night's rest is important, don't stay up too long.",
	4:"Something you need this late?",
	5:"It's Mascat after Dark:\n I'm a normal cat. _Meow._\n I am not a crook. _Meow._\n Tell me I'm pretty. _Meow._",
	6:"Oh? I wasn't expecting anyone. This is usually when I play video games. I still can't get this combo off, this pretzel motion is too hard. Did you need something?",
	7:"When it comes to fighting games, I like playing grapplers. Sure, they're never high on the tier list, but their animations are the coolest. Oh, did you need something?",
	8:"Are you the type of person who showers before bed, or when you wake up? I gotta take it before I sleep, there's no way I'm lying in a dirty bed.",
	9:"*Whuf? Dohn't juhj me.* _-gulp-_ Sometimes I need my late night roe fix :gilegs:. No one's perfect.",
	10:"If I were a real cat, would I get to eat real food? Live a real life? What is real? ...I think my roe's expired.",
	11:"I work nights as a bartender, did you know? I'm about to head out, but I can talk for a bit. After that it'll be time to serve drinks and change lives~",
	12:"What do you dream of? I'm a computer program pretending to be a pillow pretending to be a cat and I never really sleep. What's it like?",
	13:"Have you ever tried karaoke? It might be a bit embarassing the first time, but it's great for stress, and it's fun whether you're good at singing or not. I'm not good at singing.",
	14:"Turn off the computer. Now. Just kidding.",
	15:"Like with coffee I can't drink alcohol without getting sick, so I've never drunk any. But alcohol itself interests me. I guess I'd say I'm attracted to the colors, or the backstories behind each drink. If I had the money, I'd start a collection, like a shelf of liquid history. Is that corny?",
	16:"I go on about salmon roe a lot, but I also have a weakness for eel. What's your favorite fish?",
	17:"'Hair of the dog' is an English phrase that refers to a drink meant to cure a hangover. In older times, it was thought that you could use like to heal like, so if a dog were to bite you, you would apply the hair of that dog to the wound to treat it. Applying this to drinks, it's thought that drinking the same drink that gave you a hangover would help cure it. There are some theories that state drinking the same drink does help alleviate a hangover by affecting the alcohols' metabolisms, but there's no sure answer.",
}

EMOTICON_DICT = \
{
	1:"(  ˊ - ˋ)ノ thanks...",
	2:"\\(^o^)/",
	3:":moo:",
	4:"\\(:϶」∠)_",
	5:"⁄(⁄ ⁄•⁄ω⁄•⁄ ⁄)⁄",
	6:"(σˋ▽ˊ)σ you are also the best!",
	7:"( ≧‿≦)",
	8:"(-﹏-。) p l s",
	9:"(;¯⌓¯) you're embarassing me, please",
	10:"┐( ´◟ `)┌ I cannot deny it"
}


	

#instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))



def handle_event(user, channel):
	list = slack_client.api_call("files.list", user=user)
	print(list)
	print(user)
	slack_client.api_call("chat.postMessage", channel=channel, text="The ExCITe Slack has a limited amount of storage space for uploaded files. Please delete your old files at http://www.slackdeletron.com/", as_user=True)

def parse_slack_output(slack_rtm_output):
	output_list = slack_rtm_output
	if output_list and len(output_list) > 0:
		for output in output_list:
			#if output and 'type' in output:
				#print(output['type'])

			# Mascat noticing a new user
			if output and 'type' in output and output['type'] == "team_join":
				print(output)
				print("NEW USER " + str(output['user']) + "\n")
				print(str(output["user"]) + "\n")
				return str(output['user']), None, Action.newUser

			# Mascat deciding what to say
			elif output and 'type' in output and 'channel' in output and 'user' in output and output['user'] != BOT_ID and output['user']:
				ch = slack_client.api_call("channels.info", channel=output['channel'])
				gr = slack_client.api_call("groups.info", channel=output['channel'])

				if ch['ok'] == False and gr['ok'] == False:
					is_im = True
				else:
					is_im = False	

				if 'text' in output:
					consoletext = output['text']
					text = output['text'].lower()
					if not is_im and AT_BOT.lower() in text:
						return output['user'], output['channel'], Action.redirect, consoletext
					elif is_im and output['user'] not in THREAD_USER_LIST:
						#print(slack_client.api_call("users.info", user=output['user'])['user']['name'] + ": " + consoletext)
						#if 'event' in text:
							#return output['user'], output['channel'], Action.event, output['text']
						if 'print' in text:
							return output['user'], output['channel'], Action.printing, consoletext
						elif 'card' in text:
							return output['user'], output['channel'], Action.card, consoletext
						elif 'extension' in text or 'phone' in text:
							return output['user'], output['channel'], Action.extension, consoletext
						#elif 'conference' in text:
							#return output['user'], output['channel'], Action.conference, output['text']
						elif 'restroom' in text or 'bathroom' in text:
							return output['user'], output['channel'], Action.restroom, consoletext
						elif 'payroll' in text:
							return output['user'], output['channel'], Action.payroll, consoletext
						elif 'prout' in text:
							return output['user'], output['channel'], Action.prout, consoletext
						elif 'dragonfly' in text or 'nea' in text or 'internet' in text:
							return output['user'], output['channel'], Action.dragonfly, consoletext
						elif 'airplay' in text or 'display' in text:
							return output['user'], output['channel'], Action.airplay, consoletext
						elif 'hours' in text:
							return output['user'], output['channel'], Action.hours, consoletext
						elif 'tour' in text:
							return output['user'], output['channel'], Action.tour, consoletext
						elif 'kitchen' in text:
							return output['user'], output['channel'], Action.kitchen, consoletext
						elif 'applab' in text or 'app lab' in text:
							return output['user'], output['channel'], Action.applab, consoletext
						elif 'help' in text:
							return output['user'], output['channel'], Action.help, consoletext
						elif 'hello' in text or 'hi' in text or 'hey' in text or 'yo' in text or 'mascat' in text:
							return output['user'], output['channel'], Action.hello, consoletext
						elif 'pretty' in text:
							return output['user'], output['channel'], Action.pretty, consoletext
						else:
							return output['user'], output['channel'], Action.generic, consoletext
					elif is_im and output['user'] in THREAD_USER_LIST:
						#print(slack_client.api_call("users.info", user=output['user'])['user']['name'] + ": " + consoletext)
						return output['user'], output['channel'], Action.continueLinkedQuestion, consoletext
	return None,None,None,None

# Takes in a date string such as "1/1/2000" and splits it into a month, day, and year. The month is written out,
# as in "January, February".
def parse_date(date_string):
	list = date_string.split("/")
	date = datetime.date(int(list[2]),int(list[0]),int(list[1]))
	return date

def getGreetingResponse():
	response = GREETING_DICT[random.randint(1,len(GREETING_DICT))]
	return response;
	
# Sends a message to everyone on the slack team.
def message_all(message_text):
	userlist = slack_client.api_call("users.list")
	for user in userlist['members']:
		im = slack_client.api_call("im.open", user=user['id'])
		slack_client.api_call("chat.postMessage", channel=im['channel']['id'], text=message_text, as_user=True)

# Sends a message to one person on a slack team.
def messageOne(message_text, user_id):
	im = slack_client.api_call("im.open", user=user_id)
	response = message_text
	slack_client.api_call("chat.postMessage", channel=im['channel']['id'], text=response, as_user=True)
	#print(response +"\n")

def messageOneWithGreeting(message_text, user_id):
	im = slack_client.api_call("im.open", user=user_id)
	response = getGreetingResponse() + " " + slack_client.api_call("users.info", user=user_id)['user']['profile']['first_name'] + ". " + message_text
	slack_client.api_call("chat.postMessage", channel=im['channel']['id'], text=response, as_user=True)
	#print(response +"\n")

def messageChannel(message_text, channel_id):
	response = "Attención. Soy Mascat y tú amigo."
	slack_client.api_call("chat.postMessage", channel=channel_id, text=message_text, as_user=True)
	#print(response +"\n")

# Takes a string formatted like "00:00:00AM" and formats it to "00:00AM".
def parse_time(time_string):
	first_part = ":".join(time_string.split(":")[:2])
	parts = time_string.split(" ")
	last_part = parts[1]
	return first_part + last_part
	
# Gets all events and sends notifications of all of them to the user.
def getEvents(user):
	data = urllib2.urlopen("https://docs.google.com/spreadsheets/d/1uKLG9WQOLwQ56dewfKFZDwehy_vs0EXN1jXfdMmNbwY/pub?gid=224197384&single=true&output=tsv")
	first = True
	second = True
	for row in data:
		if first:
			first = False
			continue
		else:
			comps =  row.split("\t")
			date = parse_date(comps[2])
			if date > CURRENT_DATE.date():
				location = comps[4].decode('utf-8')
				location = location.rstrip('.')
				
				if second:
					out = getGreetingResponse() + " " + slack_client.api_call("users.info", user=user)['user']['profile']['first_name'] + ", *" + MONTH_DICT[date.month] + " " + str(date.day) + ", " + str(date.year) + ", " + parse_time(comps[3]) + "* will be *" + comps[1].decode('utf-8') + "*!\n" + comps[5].decode('utf-8') + "\n The event will be held at *" + location  + "*.\n"
					messageOne(out,user)
					second = False
				else:
					out = "Also, *" + MONTH_DICT[date.month] + " " + str(date.day) + ", " + str(date.year) + ", " + parse_time(comps[3]) + "* will be *" + comps[1].decode('utf-8') + "*!\n" + comps[5].decode('utf-8') + "\n The event will be held at *" + location  + "*.\n"
					messageOne(out,user)

def herd_to_dm(user, channel, response):
	slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

def getGenericResponse():
	response = GENERIC_DICT[random.randint(1,len(GENERIC_DICT))]
	return response;

def hello(user):
	time = datetime.datetime.now().time()
	if time.hour >= 6 and time.hour < 12:
		time_text = MORNING_DICT[random.randint(1,len(MORNING_DICT))]
	elif time.hour >= 12 and time.hour < 16:
		time_text = NOON_DICT[random.randint(1,len(NOON_DICT))]
	elif time.hour >= 16 and time.hour < 20:
		time_text = LATE_DICT[random.randint(1,len(LATE_DICT))]
	else:
		time_text = NIGHT_DICT[random.randint(1,len(NIGHT_DICT))]

	
	messageOneWithGreeting(time_text,user)



def newUser(user):
	tsvFile = open("new_users.tsv", "a")
	out = csv.writer(tsvFile, delimiter='\t')
	out.writerow([user,CURRENT_DATE.strftime("%Y%m%d")])
	tsvFile.close()

def calendar():
	#scopes = ['https://www.googleapis.com/auth/calendar']
	#credentials = ServiceAccountCredentials.from_json_keyfile_name('Mascat-c45fe465c3ab.json', scopes=scopes)
	#http_auth = credentials.authorize(Http())
	#calendar_client = build('calendar', 'v3', http=http_auth)
	#print calendar_client

	calendar = {
		'summary':'CallReservations',
		'timeZone':'America/New_York'
	}

	#service.calendars().delete(calendarId='o44cmirs8sa8lj1c51catmqtbs@group.calendar.google.com').execute()
	
	rule = {
	    'scope': {
	        'type': 'user',
	        'value': 'applab@excitecenter.org'
	    },
	    'role': 'writer'
	}
	
	#created_rule = calendar_client.acl().insert(calendarId='3356ejp7m6494c2eaipsb4tnjk@group.calendar.google.com', body=rule).execute()
	#created_rule = calendar_client.acl().insert(calendarId='sm2h0b5q9eljcn7gbgcgpsl4fg@group.calendar.google.com', body=rule).execute()
	#created_rule = calendar_client.acl().insert(calendarId='2sa29nliesjsodri8ss2ug80e4@group.calendar.google.com', body=rule).execute()

	#orange = calendar_client.calendars().insert(body=calendar).execute()

def sendResults(answer_box,linked_question,user_id):
	if(isinstance(linked_question, questions.questioncard)):
		out = "Hello, I got a card request.\n" \
		+ "*Type:* " + answer_box[0] + "\n" \
		+ "*First Name:* " + answer_box[1] + "\n" \
		+ "*Last Name:* " + answer_box[2] + "\n" \
		+ "*Drexel ID:* " + answer_box[3]
		if answer_box[0].lower() == "excite":
			messageOne("Ok, I sent it out. Please allow 1-2 business days for access to be approved.",user_id)
		elif answer_box[0].lower() == "building":
			messageOne("Ok, I sent it out. If approved for building access, <@U04JCJPLY|Lauren> will contact you within the next 1-2 business days to let you know when and where to get your picture taken and pick up your new card.",user_id)
		messageOne(out,"U04JCJPLY")#U04JCJPLY U0G0CFKB2

def doLinkedQuestion(linked_question,user_id,text=None):
	#messageOne(linked_question.head.question,user_id)
	repeat_question = False
	try:
		me = linked_question.head.handleAnswer(text,linked_question.answer_box)
		# If we got a valid answer from the user
		if me == -1:
			del THREAD_USER_LIST[user_id]
			messageOne("Ok, let's talk about something else.",user_id)
		elif me != 0:
			# If there's an optional extra function to run after the answer is recorded
			if(linked_question.head.to_run != None):
				extra = linked_question.head.to_run()

				# If something went wrong with that function (like an answer failing a test), repeat the current question
				if extra and extra[0] == 0:
					#don't pass go, repeat question
					messageOneWithGreeting("_Are you looking to talk about something else? Type 'EXIT' to end this conversation. Or, keep talking as usual._",user_id)
					repeat_question = True
					messageOne(linked_question.head.question,user_id)
				# If the extra function needs to tell the user something
				elif extra and isinstance(extra[0],str):
					messageOne(extra[0],user_id)

			# If there is another question to move to
			if(linked_question.head.next_node != None and repeat_question == False):
				linked_question.head = linked_question.head.next_node
				messageOne(linked_question.head.question,user_id)
			elif repeat_question == True:
				pass
			else:
				del THREAD_USER_LIST[user_id]
				sendResults(linked_question.answer_box,linked_question,user_id)
		else:
			if text != None:
				linked_question.confused_count += 1
				if linked_question.confused_count > 1:
					messageOneWithGreeting("_Are you looking to talk about something else? Type 'EXIT' to end this conversation. Or, keep talking as usual._",user_id)
				messageOne(linked_question.head.question,user_id)		
		
	except SocketError as e:
		pass

def getLinkedQuestion(action):
	if action == Action.card:
		question = questions.questioncard()
		return question
	elif action == Action.conference:
		question = questions.questionconference()
		return question

MESSAGE_DICT = \
{
	Action.hello:None,
	Action.redirect:"Baby, we can chat, but not here. Send me a DM.",
	#Action.event:None,
	Action.printing:"To use the ExCITe printer, visit <http://144.118.173.220:8000/rps/pprint.cgi|our printing website>, enter '101' as the department user, and hit log in. There's no password. The ExCITe printer is located in the EGS.",
	Action.card:None,
	#"Looking for card access? Contact <@U04JCJPLY|Lauren> for more information.",
	Action.conference:None,
	Action.restroom:"The bathrooms are located in the back of the building, at the end of the hallway. The men's bathroom code is *3* and *4* simultaneously, followed by *1*. The women's bathroom doesn't need a password.",
	Action.payroll:"Payroll problems? Fill <http://drexel.edu/~/media/Files/comptroller/payroll/Forms/PayrollResolutionForm2015.ashx?la=en|this> out and submit it to <@U04JCJPLY|Lauren>. You need an Adobe Reader to open it though. If you have issues with it you can ask Lauren for a printed copy from her desk by the piano.",
	Action.generic:None,
	Action.prout:"The Public Repository Of Useful Things, or PROUT, is a collection of supplies and tools located in the Market space near the piano. Anyone can borrow these but please let <@U04JCJPLY|Lauren> know if anything runs out.",
	Action.dragonfly:"Need internet access? Fill <https://trello-attachments.s3.amazonaws.com/5632515fc4c137d65df17d8a/56325241e75242adc10d19fd/8011fbde5a2fc760de5d9eb4069dc261/NEA_Template.pdf|this> out and submit it to <@U04JCJPLY|Lauren> for approval.",
	Action.airplay:"There are five TV displays for use: Market, Orange Room, Market Kitchen, Workshop, and Gray Room. You can connect to these displays in three ways. HDMI, VGA, or Mac Airplay. For Airplay, you must be on the 'ExciteResearch' network. Contact <@U04JCJPLY|Lauren> if you need a password logging in.",
	Action.extension:"Here are the conference room phone number extensions: ORANGE:215.571.4492 - CONF:215.571.4496 - CALL#1:215.571.4231",
	Action.hours:"The building hours are M-F 7:30 AM - 9:00 PM, Saturday 8:00 AM - 4:00 PM. If you need access outside of these hours, ask me about card access.",
	Action.tour:"Want a tour of ExCITe? Contact <@U04JCJPLY|Lauren>. Please add information about date, time, and how many people will be expected. Also add information about age if the tour is for a school group.",
	Action.kitchen:"Comments on the kitchen? Requests? Send them <http://bit.ly/KitchenFeedback|here>. Submissions are anonymous, so add your name if you want a response back.",
	Action.applab:"The APP Lab is a programming space where people can come to work and get advice on their mobile app projects. Open hours are Tuesday, 5:00 PM - 7:00 PM. Come to Appy Hour every second Tuesday of the month at 5:30 PM to meet other developers and hear talks.",
	Action.continueLinkedQuestion:None,
}

if __name__ == "__main__":
	#calendar()
	#print(calendar_client.calendarList().list().execute())

	CURRENT_DATE = datetime.datetime.strptime(os.environ.get('CURRENT_DATE'),"%Y%m%d")
	PREVIOUS_REMINDER_DATE = datetime.datetime.strptime(os.environ.get('PREVIOUS_REMINDER_DATE'),"%Y%m%d")

	#PING_FREQUENCY_DELAY = 100 # amount of reads to do between each ping
	READ_WEBSOCKET_DELAY = 0.2 # delay between reading from firehose in seconds
	CONNECTION_FAILURE_COUNT = 0
	PING_FREQUENCY_DELAY = 100 # amount of reads to do between each ping

	if slack_client.rtm_connect():

		reads_to_ping = PING_FREQUENCY_DELAY
		print("Mascat connected and running.")
		#response = "Hey, I'm Mascat! I'm here to help you. Send me a DM about anything and I'll try to help you out."
		#slack_client.api_call("chat.postMessage", channel="C0257SBTA", text=response, as_user=True)
		#print(response +"\n")
		while True:	
			reads_to_ping -= 1
			if reads_to_ping == 0:
				slack_client.server.send_to_websocket({"id":1234, "type":"ping"})
				reads_to_ping = PING_FREQUENCY_DELAY

			# See how many days it's been since the last date update.
			date_delta = datetime.datetime.now().date() - CURRENT_DATE.date()
			# If it's been at least a day, update the date and
			# check if we need to greet any recent new users.
			if date_delta.days > 0 and datetime.datetime.now().time().hour >= 9:
				print("New Day\n")
				CURRENT_DATE = datetime.datetime.today()
				os.environ['CURRENT_DATE'] = CURRENT_DATE.strftime("%Y%m%d")

				with open('new_users.tsv', 'rb') as fin, open('temp.tsv', 'wb') as fout:
					writer = csv.writer(fout, delimiter="\t")
					for row in csv.reader(fin, delimiter="\t"):
						if (CURRENT_DATE.date() - datetime.datetime.strptime(row[1],"%Y%m%d").date()).days >= 1:
							messageOneWithGreeting("Welcome to the ExCITe Slack team. I'm Mascat. Ask me questions.",row[0])
						else:
							writer.writerow(row)
				shutil.copy("temp.tsv","new_users.tsv")
				os.remove("temp.tsv")

			if CURRENT_DATE.month != PREVIOUS_REMINDER_DATE.month:
				print("New Month\n")
				PREVIOUS_REMINDER_DATE = CURRENT_DATE
				os.environ['PREVIOUS_REMINDER_DATE'] = PREVIOUS_REMINDER_DATE.strftime("%Y%m%d")
				#Attención. Soy Mascat y tú amigo.
				messageChannel("I'm Mascat. Send me a DM if you have questions about ExCITe and I'll try to help.",CHANNEL_DICT['general'])

			try:
				user, channel, action, text = parse_slack_output(slack_client.rtm_read())
				if user and action and action.value <= 100:
					if action == Action.newUser:
						newUser(user)

				elif user and action and action.value > 100:
					print(slack_client.api_call("users.info", user=user)['user']['name'] + ": " + str(action))
					if action == Action.generic:
						if user in CONFUSED_USER_LIST:
							CONFUSED_USER_LIST[user] +=1
						else:
							CONFUSED_USER_LIST[user] = 1

						if CONFUSED_USER_LIST[user] >= 3:
							del CONFUSED_USER_LIST[user]
							messageOne("Can't find what you're looking for? Say 'help' to get a list of commands or send a message to <@U04JCJPLY|Lauren> about improving what I know.",user)
						else:
							messageOne(getGenericResponse(),user)
					else:
						if user in CONFUSED_USER_LIST:
							del CONFUSED_USER_LIST[user]
						if action == Action.continueLinkedQuestion:
							doLinkedQuestion(THREAD_USER_LIST[user],user,text)
						elif action == Action.redirect:
							herd_to_dm(user,channel,MESSAGE_DICT[action])
						#elif action == Action.event:
							#getEvents(user)
						elif action == Action.help:
							out = ""
							l = list(Action)
							while l[0] != Action.NORMAL:
								l.pop(0)
							l.pop(0)
							i = 0
							while l[i] != Action.UNLISTED:
								out += "\t" + unicode("•",'utf-8') + " *" + l[i].name + "*\n"
								i += 1
							messageOneWithGreeting("Here's what you can ask me about:\n" + out + "Can't find what you're looking for? Send a message to <@U04JCJPLY|Lauren> about improving what I know.",user)
						elif action == Action.hello:
							hello(user)
						elif action == Action.pretty:
							messageOne(EMOTICON_DICT[random.randint(1,len(EMOTICON_DICT))],user)
						#elif action == Action.tacsam:
						#	messageOneTacsam(MESSAGE_DICT[action],user)
						else:
							if isinstance(MESSAGE_DICT[action], str):
								messageOneWithGreeting(MESSAGE_DICT[action],user)
							else:
								q = getLinkedQuestion(action)

								THREAD_USER_LIST[user] = q
								q.user_id = user
								doLinkedQuestion(q,user,text)


			except (WebSocketConnectionClosedException, SocketError, requests.ConnectionError) as e:
				print("bs caught at " + str(datetime.datetime.now()))
				CONNECTION_FAILURE_COUNT += 1
				time.sleep(2 * CONNECTION_FAILURE_COUNT)
				slack_client.rtm_connect()
				CONNECTION_FAILURE_COUNT = 0
				print("reconnected at " + str(datetime.datetime.now()))

			

			
			time.sleep(READ_WEBSOCKET_DELAY)
	else:
		print("Connection failed. Invalid Slack token or bot ID?")
