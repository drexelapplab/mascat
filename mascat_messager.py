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
import question_node
from socket import error as SocketError

BOT_ID = os.environ.get("BOT_ID")

#constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"
GENERAL_CHANNEL = "C0257SBTA"

#global
CURRENT_DATE = datetime.date.today()
PREVIOUS_REMINDER_DATE = datetime.date.today()

class Action(Enum):
	# Mascat message actions
	generic = 1
	redirect = 2
	event = 3
	printing = 4
	card = 5
	conference = 6
	restroom = 7
	payroll = 8
	prout = 9
	dragonfly = 10
	airplay = 11
	extension = 12
	hours = 13
	tour = 14
	kitchen = 15
	applab = 16

	hello = 99

	# Mascat non message actions
	newUser = 101
	remind = 102

MONTH_DICT = \
{ 	
	'1':'January', 
	'2':'February',
	'3':'March',
	'4':'April',
	'5':'May',
	'6':'June',
	'7':'July',
	'8':'August',
	'9':'September',
	'10':'October',
	'11':'November',
	'12':'December' 
}

GENERIC_DICT = \
{
	1:"I'm just a cat. Can't do everything.", 
	2:"What.", 
	3:"Say that again, but slower. I'm tired.", 
	4:"I don't have real ears so I have no idea what you just said.", 
	5:"Hipchat wouldn't ask me to do this.", 
	6:"Don't feel like it.", 
	7:"Ask me later.", 
	8:"Can't be bothered to.", 
	9:"I'll do it if you pay me.", 
	10:"I'm not really alive.", 
	11:"Want to play video games instead?",
	12:"Let's do karaoke instead.",
	13:"Let's play fighter. Winner stays, loser pays.",
	14:"Try asking someone else.",
	15:"I don't care.",
	16:"Meong.",
	17:"Miau.",
	18:"Mjau.",
	19:"Miaou.",
	20:"喵喵.",
	21:"ニャー.",
	22:"야옹.",
	23:"Мияу-мияу.",
	24:"Mjá.",
	25:"Meow.",
	26:"מְיָאוּ.",
	27:".مُواَء",
	28:"เมี้ยว.",
	29:"Miao.",
	30:":moo:"
}

SUFFIX_DICT = \
{
	1:""
}

GREETING_DICT = \
{
	1:"Hi",
	2:"Hey",
	3:"Yo",
	4:"Hoy"
}

MORNING_DICT = \
{
	1:"It's too early in the morning for me.",
	2:"Did you eat breakfast?",
	3:"I wanted to sleep in."
}

NOON_DICT = \
{
	1:"Do you ever get tired after lunch?",
	2:"What did you eat for lunch?",
	3:"Look at you, still at it. You're my role model."
}

LATE_DICT = \
{
	1:"Isn't it almost time to go home?",
	2:"Is the sun setting?",
	3:"What are you getting for dinner?",
	4:"In a perfect world, I'd eat salmon roe every night."
}

NIGHT_DICT = \
{
	1:"What are you waking me up so late for.",
	2:"Take it easy, yeah?",
	3:"Getting a full night's rest is important, don't stay up too long.",
	4:"Something you need this late?"
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
				print(output["user"] + "\n")
				return str(output['user']), None, Action.newUser

			# Mascat deciding what to say
			elif output and 'channel' in output and 'user' in output and output['user'] != BOT_ID:
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
						return output['user'], output['channel'], Action.redirect
					elif is_im:
						print(slack_client.api_call("users.info", user=output['user'])['user']['name'] + ": " + consoletext)
						if 'event' in text:
							return output['user'], output['channel'], Action.event
						elif 'print' in text:
							return output['user'], output['channel'], Action.printing
						elif 'card' in text:
							return output['user'], output['channel'], Action.card
						elif 'conference' in text and ('extension' in text or 'phone' in text):
							return output['user'], output['channel'], Action.extension
						elif 'conference' in text:
							return output['user'], output['channel'], Action.conference
						elif 'restroom' in text or 'bathroom' in text:
							return output['user'], output['channel'], Action.restroom
						elif 'payroll' in text:
							return output['user'], output['channel'], Action.payroll
						elif 'prout' in text:
							return output['user'], output['channel'], Action.prout
						elif 'dragonfly' in text or 'nea' in text or 'internet' in text:
							return output['user'], output['channel'], Action.dragonfly
						elif 'airplay' in text or 'display' in text:
							return output['user'], output['channel'], Action.airplay
						elif 'hours' in text:
							return output['user'], output['channel'], Action.hours
						elif 'tour' in text:
							return output['user'], output['channel'], Action.tour
						elif 'kitchen' in text:
							return output['user'], output['channel'], Action.kitchen
						elif 'applab' in text or 'app lab' in text:
							return output['user'], output['channel'], Action.applab
						elif 'hello' in text or 'hi' in text or 'hey' in text:
							return output['user'], output['channel'], Action.hello
						else:
							return output['user'], output['channel'], Action.generic
				#print(output['type'])
	return None,None,None

# Takes in a date string such as "1/1/2000" and splits it into a month, day, and year. The month is written out,
# as in "January, February".
def parse_date(date_string):
	list = date_string.split("/")
	try:
		month = MONTH_DICT[list[0]]
	except KeyError:
		month = ""
	day = list[1]
	if int(day) > 31 and int(day) < 1:
		day = ""
	year = list[2]
	return month, day, year	

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
	print(response +"\n")

def messageOneWithGreeting(message_text, user_id):
	im = slack_client.api_call("im.open", user=user_id)
	response = getGreetingResponse() + " " + slack_client.api_call("users.info", user=user_id)['user']['profile']['first_name'] + ". " + message_text
	slack_client.api_call("chat.postMessage", channel=im['channel']['id'], text=response, as_user=True)
	print(response +"\n")

def messageChannel(message_text, channel_id):
	response = "Attención. Soy Mascat y tú amigo."
	slack_client.api_call("chat.postMessage", channel=channel_id, text=message_text, as_user=True)
	print(response +"\n")

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
		elif second:
			second = False
			comps =  row.split("\t")
			month,day,year = parse_date(comps[2])
			location = comps[4].decode('utf-8')
			location = location.rstrip('.')
			#slack_client.api_call("users.info", user=user)['user']['profile']['first_name']
				
			out = getGreetingResponse() + " " + slack_client.api_call("users.info", user=user)['user']['profile']['first_name'] + ", *" + month + " " + day + ", " + year + ", " + parse_time(comps[3]) + "* will be *" + comps[1].decode('utf-8') + "*!\n" + comps[5].decode('utf-8') + "\n The event will be held at *" + location  + "*.\n"
			messageOne(out,user)
		else:
			comps =  row.split("\t")
			month,day,year = parse_date(comps[2])
			location = comps[4].decode('utf-8')
			location = location.rstrip('.')
				
			out = "Also, *" + month + " " + day + ", " + year + ", " + parse_time(comps[3]) + "* will be *" + comps[1].decode('utf-8') + "*!\n" + comps[5].decode('utf-8') + "\n The event will be held at *" + location  + "*.\n"
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
	elif time.hour >= 16 and time.hour < 22:
		time_text = LATE_DICT[random.randint(1,len(LATE_DICT))]
	else:
		time_text = NIGHT_DICT[random.randint(1,len(NIGHT_DICT))]

	emoticon = u"( ˊ-ˋ)ノ".encode("utf8")
	print emoticon
	response = getGreetingResponse() + " " + slack_client.api_call("users.info", user=user)['user']['profile']['first_name'] + ". \n" + time_text
	messageOne(response,user)

MESSAGE_DICT = \
{
	Action.hello:"bad",
	Action.redirect:"Baby, we can chat, but not here. Send me a DM.",
	Action.event:"bad",
	Action.printing:"To use the ExCITe printer, visit <http://144.118.173.220:8000/rps/pprint.cgi|our printing website>, enter '101' as the department user, and hit log in. There's no password. The ExCITe printer is located in the EGS.",
	Action.card:"Looking for card access? Contact <@U04JCJPLY|Lauren> for more information.",
	Action.conference:"byrnhildr y siegfred",
	Action.restroom:"The men's bathroom code is [3] and [4] simultaneously, followed by [1]. The women's bathroom doesn't have a password.",
	Action.payroll:"Payroll problems? Fill <https://files.slack.com/files-pri/T0257SBSW-F2LNMHC3W/payroll_resolution_form-open_with_pro.pdf|this> out and submit it to <@U04JCJPLY|Lauren>. You need an Adobe Reader to open it though. If you have issues with it you can ask Lauren for a printed copy from her desk by the piano.",
	Action.generic:"bad",
	Action.prout:"The public Repository of Useful Things, or PROUT, is a collection of supplies and tools located in the Market space near the piano. Anyone can borrow these but non-ExCITe personnel need approval.",
	Action.dragonfly:"Need internet access? Fill <https://trello-attachments.s3.amazonaws.com/5632515fc4c137d65df17d8a/56325241e75242adc10d19fd/8011fbde5a2fc760de5d9eb4069dc261/NEA_Template.pdf|this> out and submit it to <@U04JCJPLY|Lauren> for approval.",
	Action.airplay:"There are five TV displays for use: Market, Orange Room, Market Kitchen, Workshop, and Gray Room. You can connect to these displays in three ways. HDMI, VGA, or Mac Airplay. You must be on the 'ExciteResearch' network to use it. Contact <@U04JCJPLY|Lauren> if something's not working.",
	Action.extension:"Here are the conference room phone number extensions: ORANGE:215.571.4492 - CONF:215.571.4496 - CALL#1:215.571.4231 - CALL#2:215.571.4494",
	Action.hours:"The building hours are M-F 7:30 AM - 9:00 PM, Saturday 8:00 AM - 4:00 PM. If you need to get in off regular hours, contact <@U04JCJPLY|Lauren> about getting an access card.",
	Action.tour:"Want a tour of ExCITe? Contact <@U04JCJPLY|Lauren>. Please add information about date, time, and how many people will be expected. Also add information about age if the tour is for a school group.",
	Action.kitchen:"Comments on the kitchen? Requests? Send them <http://bit.ly/KitchenFeedback|here>. Submissions are anonymous, so add your name if you want a response back.",
	Action.applab:"The APP Lab is a programming space where people can come to work and get advice on their mobile app projects. Open hours are Tuesday, 5:00 PM - 7:00 PM. Come to Appy Hour every second Tuesday of the month at 5:30 PM to meet other developers and hear talks."
}

def newUser(user):
	tsvFile = open("new_users.tsv", "a")
	out = csv.writer(tsvFile, delimiter='\t')
	out.writerow([user,CURRENT_DATE.strftime("%Y%m%d")])
	tsvFile.close()

def initaliseQuestions():
	card2 = questionnode(None,"So you want an ExCITe card. What is your First Name?",None)
	card1 = questionnode(None,"So you want a building card. What is your First Name?",None)
	card0 = questionnode(None,"Do you want a building card or an ExCITe card?",{"building":card1,"excite":card2})



if __name__ == "__main__":
	READ_WEBSOCKET_DELAY = 0.2 # 1 second delay between reading from firehose
	if slack_client.rtm_connect():
		print("Mascat connected and running.")
		while True:

			# See how many days it's been since the last date update.
			date_delta = datetime.date.today() - CURRENT_DATE
			# If it's been at least a day, update the date and
			# check if we need to greet any recent new users.
			if date_delta.days > 0 and datetime.datetime.now().time().hour >= 9:
				print("New Day\n")
				CURRENT_DATE = datetime.date.today()

				with open('new_users.tsv', 'rb') as fin, open('temp.tsv', 'wb') as fout:
					writer = csv.writer(fout, delimiter="\t")
					for row in csv.reader(fin, delimiter="\t"):
						if (CURRENT_DATE - datetime.datetime.strptime(row[1],"%Y%m%d").date()).days >= 1:
							messageOneWithGreeting("Welcome to the ExCITe Slack team. I'm Mascat. Ask me questions. You've got the touch.",row[0])
						else:
							writer.writerow(row)
				shutil.copy("temp.tsv","new_users.tsv")
				os.remove("temp.tsv")

			if CURRENT_DATE.month != PREVIOUS_REMINDER_DATE.month:
				print("New Month\n")
				PREVIOUS_REMINDER_DATE = CURRENT_DATE
				messageChannel("Attención. Soy Mascat y tú amigo.",GENERAL_CHANNEL)

			try:
				user, channel, action = parse_slack_output(slack_client.rtm_read())
				if user and action and action.value > 100:
					if action == Action.newUser:
						newUser(user)

				elif user and action and action.value <= 100:
					if action == Action.redirect:
						herd_to_dm(user,channel,MESSAGE_DICT[action])
					elif action == Action.event:
						getEvents(user)
					elif action == Action.generic:
						messageOne(getGenericResponse(),user)
					elif action == Action.hello:
						hello(user)
					else:
						messageOneWithGreeting(MESSAGE_DICT[action],user)
			except SocketError as e:
				pass

			

			
			time.sleep(READ_WEBSOCKET_DELAY)
	else:
		print("Connection failed. Invalid Slack token or bot ID?")
