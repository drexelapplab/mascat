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
import question_node as qn
import linked_list as ll
from socket import error as SocketError
from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build
from httplib2 import Http
import websocket

BOT_ID = os.environ.get("BOT_ID")

#constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"

#global
CURRENT_DATE = datetime.date.today()
PREVIOUS_REMINDER_DATE = datetime.date.today()

LINKED_QUESTION_DICT = {}

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


	#tacsam = 98
	hello = 99
	pretty = 100

	# Mascat non message actions
	newUser = 101
	remind = 102

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
	29:"Miao."
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

EMOTICON_DICT = \
{
	1:"(  ˊ - ˋ)ノ thanks...",
	2:"\\(^o^)/",
	3:":moo:",
	4:"\\(:϶_∠)_",
	5:"*ᴛʜᴀɴᴋ ʏᴏᴜ*"
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
						elif 'pretty' in text:
							return output['user'], output['channel'], Action.pretty
						#elif 'tacsam' in text:
						#	return output['user'], output['channel'], Action.tacsam
						else:
							return output['user'], output['channel'], Action.generic
			if output['type'] != "presence_change" and output['type'] != "reconnect_url" and output['type'] != "pong":
				print(output)
				print("")	
	return None,None,None

def parse_slack_output_for_linked_question(slack_rtm_output):
	output_list = slack_rtm_output
	if output_list and len(output_list) > 0:
		for output in output_list:

			if output and 'channel' in output and 'user' in output and output['user'] != BOT_ID:
				ch = slack_client.api_call("channels.info", channel=output['channel'])
				gr = slack_client.api_call("groups.info", channel=output['channel'])

				if ch['ok'] == False and gr['ok'] == False:
					is_im = True
				else:
					is_im = False	

				if 'text' in output:
					consoletext = output['text']
					text = output['text'].lower()
					if is_im:
						print(slack_client.api_call("users.info", user=output['user'])['user']['name'] + ": " + consoletext)
						return output['text']
			if output['type'] != "presence_change" and output['type'] != "reconnect_url" and output['type'] != "pong":
				print(output)
				print("")	
	return None,None

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

#def messageOneTacsam(message_text, user_id):
#	im = slack_client.api_call("im.open", user=user_id)
#	response = message_text
#	slack_client.api_call("chat.postMessage", channel=im['channel']['id'], text=response, as_user=False, username="T͍͖͚̰̹̹̥̈́ͭͪa̶̤̤͈̮͗͑ͩc̈́̑͋ͯ̒҉̪͔̼ͅs͉͇a̫ͮm̡̤͍ͬͅ,̥̲͕͎̒̔͑ͪ ̻͚̹͙̙ͯ͛̿ͣ̆t̠̯̏͂h͎̲͕̹̟̙ͭ̂́ͩ̎̂e̢̎̒ͣͩ̔ͩͪ ̳̬̹͉̜͉̲̐u͔̲̞̪̗͓̽͗ͣn̆҉͍̗̭̝̝͉ḓ͍̲̬̯̖̅y̌̓҉̟̮̞̞i̠̠̱̝̻͈n͉̺͙̥̮͇̓g̡̬̬̺̬͍̔ ̙̤̼ͪ͑͌̽d͉͙͚̻̱̙ͩ̈́͒̆̉͂͐͞e̜̙͕͙̹̣͈̾͒̏̀̚͞iṱ̶̥̲͗̎ͯͩ̚y̭̣͐ͮ̓̏ ̙͍̹̰̭̦̫̏͗̓o͎͖f̵͔̰̐͌̋ͯ̋́̊ ̙͇̝̱̝ͩE͙̣̦̤ͧ̓ͫ̆x̡͊ͭC̗̱̙͇̺͎̋̂̄̅ͬ͘I̬̙T̳̞͉̞͎͎̯ë́̓ͦ̋̎̿", icon_url="http://lorempixel.com/128/128/")
#	print(response +"\n")

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
			if date > CURRENT_DATE:
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
	elif time.hour >= 16 and time.hour < 22:
		time_text = LATE_DICT[random.randint(1,len(LATE_DICT))]
	else:
		time_text = NIGHT_DICT[random.randint(1,len(NIGHT_DICT))]

	
	response = getGreetingResponse() + " " + slack_client.api_call("users.info", user=user)['user']['profile']['first_name'] + ".\n" + time_text
	messageOne(response,user)



def newUser(user):
	tsvFile = open("new_users.tsv", "a")
	out = csv.writer(tsvFile, delimiter='\t')
	out.writerow([user,CURRENT_DATE.strftime("%Y%m%d")])
	tsvFile.close()

def calendar():
	scopes = ['https://www.googleapis.com/auth/calendar']
	credentials = ServiceAccountCredentials.from_json_keyfile_name('Mascat-c45fe465c3ab.json', scopes=scopes)
	http_auth = credentials.authorize(Http())
	service = build('calendar', 'v3', http=http_auth)

	calendar = {
		'summary':'OrangeReservations',
		'timeZone':'America/New_York'
	}
	print(service.calendarList().list().execute())


	#orange = service.calendars().insert(body=calendar).execute()
	#print orange['id']

def initaliseQuestionCard():
	card0 = qn.questionnode("Need an access card? Is it for just ExCITe or is it for the building?",['excite', 'building'])
	card1 = qn.questionnode("What is your first name?")
	card2 = qn.questionnode("What is your last name?")
	card3 = qn.questionnode("If you have a Drexel ID, what is it?")
	card0.setNextNode(card1)
	card1.setNextNode(card2)
	card2.setNextNode(card3)
	card = ll.linkedlist(card0)
	LINKED_QUESTION_DICT["card"] = card
	return LINKED_QUESTION_DICT['card']

def initaliseQuestionConference():
	conference0 = qn.questionnode("Trying to book a conference room? Do you want Orange or Grey?")
	conference1 = qn.questionnode("What day do you want the room?")
	conference2 = qn.questionnode("What times do you want the room?")
	conference0.setNextNode(conference1)
	conference1.setNextNode(conference2)
	conference = ll.linkedlist(conference0)
	LINKED_QUESTION_DICT["conference"] = conference
	return LINKED_QUESTION_DICT['conference']

def doLinkedQuestion(linked_question,user_id):
	answer_box = []
	messageOne(linked_question.head.question,user_id)
	try:
		time.sleep(5)
		text = parse_slack_output(slack_client.rtm_read())
		if linked_question.head.handleAnswer(text,answer_box) == 0:
			doLinkedQuestion(linked_question,user_id)
		else:
			doLinkedQuestion(linked_question.next())

		
	except SocketError as e:
		pass


MESSAGE_DICT = \
{
	Action.hello:"bad",
	Action.redirect:"Baby, we can chat, but not here. Send me a DM.",
	Action.event:"bad",
	Action.printing:"To use the ExCITe printer, visit <http://144.118.173.220:8000/rps/pprint.cgi|our printing website>, enter '101' as the department user, and hit log in. There's no password. The ExCITe printer is located in the EGS.",
	Action.card:initaliseQuestionCard(),
	#"Looking for card access? Contact <@U04JCJPLY|Lauren> for more information.",
	Action.conference:initaliseQuestionConference(),
	Action.restroom:"The men's bathroom code is [3] and [4] simultaneously, followed by [1]. The women's bathroom doesn't have a password.",
	Action.payroll:"Payroll problems? Fill <https://files.slack.com/files-pri/T0257SBSW-F2LNMHC3W/payroll_resolution_form-open_with_pro.pdf|this> out and submit it to <@U04JCJPLY|Lauren>. You need an Adobe Reader to open it though. If you have issues with it you can ask Lauren for a printed copy from her desk by the piano.",
	Action.generic:"bad",
	Action.prout:"The public Repository of Useful Things, or PROUT, is a collection of supplies and tools located in the Market space near the piano. Anyone can borrow these but non-ExCITe personnel need approval.",
	Action.dragonfly:"Need internet access? Fill <https://trello-attachments.s3.amazonaws.com/5632515fc4c137d65df17d8a/56325241e75242adc10d19fd/8011fbde5a2fc760de5d9eb4069dc261/NEA_Template.pdf|this> out and submit it to <@U04JCJPLY|Lauren> for approval.",
	Action.airplay:"There are five TV displays for use: Market, Orange Room, Market Kitchen, Workshop, and Gray Room. You can connect to these displays in three ways. HDMI, VGA, or Mac Airplay. You must be on the 'ExciteResearch' network to use it. Contact <@U04JCJPLY|Lauren> if something's not working.",
	Action.extension:"Here are the conference room phone number extensions: ORANGE:215.571.4492 - CONF:215.571.4496 - CALL#1:215.571.4231",
	Action.hours:"The building hours are M-F 7:30 AM - 9:00 PM, Saturday 8:00 AM - 4:00 PM. If you need to get in off regular hours, contact <@U04JCJPLY|Lauren> about getting an access card.",
	Action.tour:"Want a tour of ExCITe? Contact <@U04JCJPLY|Lauren>. Please add information about date, time, and how many people will be expected. Also add information about age if the tour is for a school group.",
	Action.kitchen:"Comments on the kitchen? Requests? Send them <http://bit.ly/KitchenFeedback|here>. Submissions are anonymous, so add your name if you want a response back.",
	Action.applab:"The APP Lab is a programming space where people can come to work and get advice on their mobile app projects. Open hours are Tuesday, 5:00 PM - 7:00 PM. Come to Appy Hour every second Tuesday of the month at 5:30 PM to meet other developers and hear talks.",
	#Action.tacsam:"O̥͍Ư̖̻̮͉̪̠̂̎͗̓ͫ̌R̞̘͍͙̄̿̾ ͤͦŅͨ̊ͪͪ̇̌Aͫ͗M̴̙̰̗̤̫ͩͩ̊̄̾̚ͅE̦̘̥̒͒̓̏̿ͩ ̴͍̹̞̮͖͍ͥ̔̏Ḩ̮͔̖͇͑̔͗̓̇̎͗A̪̟̖̣͌̍̋̈́Ş̥̿̾ͨͤ̀͑ ̷̹̬̻̙̰͙͊̾͋B̨̮̹̖̒̒͊̏̓E̸͙̖̹ͥE̴ͯ̓̒Nͣ̑ͬ̍̽̒҉̰ ͉̭͍̍̉̍ͯ̔I͓̤͎͖̐ͩͫ̾̒͟N̳̹͕͡V̞̫̤̳͂ͩ̆ͮ̋ͤͣ͜ͅO̷̟̗̜̟ͬK̢͖͈̰͙̩̦E̢̅̏D̜̦̂͗ͧͦ̔,҉͔̜̤͎̯̱͍ ͉̹̯̣̋Ą͛̾N̹̼͈͇͎͛ͬ̉̈͆͝D͔̦̼̍ͮ̊̽̊ ̦ͭͩW̱̱̞̜̹̳̜͛̽E̪̗̬̘̩͎͊ͅ ̸̿̍ͅA̖̥ͨ̿̐̄Pͨ͊͛ͣͧ̽̂҉͕̫̩̼̮Ṕ̗̙̫ͭ͆Ȇ͂ͥ̀͛̈A̭̱̞ͣ͋͐͊̽̕Ŗ͍̝̈́̓ͥͣ ̤͍̺̦͈́͊Bͨͨ̎̽͏͔E̬͇̥͎̗F̵̣ͫ̓̈́̒̍̽ͭỌ̶̖̭ͪ̋ͨͨ͌̑R̖͉̺͉̱̃̓̽͋ͯͮ͜Ẽ̗͍͍͈͊̂̾̀͊̀̚ ̶̠̙̏͌Y͉̺̓ͦ͂͛O̢͖̞̲̭̙͉ͧ͂̽ͥͅṶ̜̟ͮͭ̑ͩ.̗͛̔̀ ̷̞̮͙̫P̪̣͗͆͟R̡̘ͧ̏ͨ̏ͭ̃̓ͅÄ͔̙̻̻͍ͯ͗ͫ͌͗ͯI̟̪̤͖̰̍̓ͮ̈́S̡͚̥̻͔̞̽E̹̲̱̺̠͕͈̎̉ͣ̈́̉ ̼̝͕̟̽ͬ͋́͗̃̾͢ͅȎ̗̝͉ͩ͘Ų̦̖̟̱͇́̇̐Ṙ̪͆̿ͨ̀̑̓ ͍͙̮͊̊ͧͣV̻͔͍̩̠̩̎̒̓́͒ͣI̩͇̬̣S̝͉̝̠̰̼̩̏̾ͨA̳̞͚͉̼ͥ̇̾̀ͦ̒̀G̥̭͖̺̥̈́̌̿͐̍̿͠ͅË͔̙̩ͤ,̙̃ͯ̀ ̹͔͍͚̥̄ͤ̃̓ͯͥͨF̶̙̜̆̉͗̃̆ͧO͂̈ͤR҉͓ ̡̱͂͌ͧͯͧ͋W͈̞̰̖̄͑̍ͣ͒͡È̛͖̥̬̠̂̂ ͊A̧̯̰ͪ̌̄R͚͍̥͌̂͊̃ͪͬ̆͜E̘̹̺͇̩͑̉ͥ ̛̮͉ͦ̈Ę͓͍͕̬̫ͥ͛T̲͔͈͍̮̋ͤ͞E͓̯̒ͩ̓ͫR̳̰̤̀̓̆̃ͩͨ̚N̸̖̻̮͎̹̰͑͋͆̌ͦ̿͂A̶̤̞̰̦̰̿͑L̦̻̘̜̤͢"
}

if __name__ == "__main__":
	#initaliseQuestions()
	calendar()

	#PING_FREQUENCY_DELAY = 100 # amount of reads to do between each ping
	READ_WEBSOCKET_DELAY = 0.2 # delay between reading from firehose in seconds
	if slack_client.rtm_connect():

		#reads_to_ping = PING_FREQUENCY_DELAY
		print("Mascat connected and running.")
		while True:
			#reads_to_ping -= 1
			#if reads_to_ping == 0:
			#	slack_client.server.send_to_websocket({"id":1234, "type":"ping"})
			#	reads_to_ping = PING_FREQUENCY_DELAY


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
				#Attención. Soy Mascat y tú amigo.
				messageChannel("I'm Mascat. Send me a DM if you have questions about ExCITe and I'll try to help.",CHANNEL_DICT['general'])

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
					elif action == Action.pretty:
						messageOne(EMOTICON_DICT[random.randint(1,len(EMOTICON_DICT))],user)
					#elif action == Action.tacsam:
					#	messageOneTacsam(MESSAGE_DICT[action],user)
					else:
						if isinstance(action, str):
							messageOneWithGreeting(MESSAGE_DICT[action],user)
						else:
							doLinkedQuestion(MESSAGE_DICT[action],user)
			except WebSocketConnectionClosedException as e:
				sack_client.rtm_connect()

			

			
			time.sleep(READ_WEBSOCKET_DELAY)
	else:
		print("Connection failed. Invalid Slack token or bot ID?")
