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

BOT_ID = os.environ.get("BOT_ID")

#constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"

#global
CURRENT_TIME = datetime.date.today()
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
	13:"...I'm hungry.",
	14:"Try asking someone else."
}

GREETING_DICT = \
{
	1:"Hi",
	2:"Hey",
	3:"I'll help you out",
	4:"Yo",
	5:"Oh, it's",
	6:"Ok,",
	7:"Sure,"
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
			if output and 'type' in output:
				print(output['type'])

			# Mascat noticing a new user
			if output and 'type' in output and output['type'] == "team_join":
				print("NEW USER " + output['user'])
				return output['user'], None, Action.newUser

			# Mascat deciding what to say
			elif output and 'channel' in output and output['user'] != BOT_ID:
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
						print(slack_client.api_call("users.info", user=user)['user']['name'] + " " + consoletext)
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
	response = GREETING_DICT[random.randint(1,7)]
	return response;
	
# Sends a message to everyone on the slack team.
def message_all(message_text):
	userlist = slack_client.api_call("users.list")
	for user in userlist['members']:
		im = slack_client.api_call("im.open", user=user['id'])
		slack_client.api_call("chat.postMessage", channel=im['channel']['id'], text=message_text, as_user=True)

# Sends a message to one person on a slack team.
def message_one(message_text, user_id):
	im = slack_client.api_call("im.open", user=user_id)
	slack_client.api_call("chat.postMessage", channel=im['channel']['id'], text=message_text, as_user=True)

def messageOneWithGreeting(message_text, user_id):
	im = slack_client.api_call("im.open", user=user_id)
	response = getGreetingResponse() + " " + slack_client.api_call("users.info", user=user_id)['user']['profile']['first_name'] + ". " + message_text
	slack_client.api_call("chat.postMessage", channel=im['channel']['id'], text=response, as_user=True)
	print(response)

# Takes a string formatted like "00:00:00AM" and formats it to "00:00AM".
def parse_time(time_string):
	first_part = ":".join(time_string.split(":")[:2])
	parts = time_string.split(" ")
	last_part = parts[1]
	return first_part + last_part
	
# Gets all events and sends notifications of all of them to the user.
def getEvents(user):
	data = urllib2.urlopen("https://docs.google.com/spreadsheets/d/1uKLG9WQOLwQ56dewfKFZDwehy_vs0EXN1jXfdMmNbwY/pub?gid=224197384&single=true&output=tsv")
	# user = "U034LKGHE"
	# user = "U04JCJPLY"
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
			message_one(out,user)
		else:
			comps =  row.split("\t")
			month,day,year = parse_date(comps[2])
			location = comps[4].decode('utf-8')
			location = location.rstrip('.')
				
			out = "Also, *" + month + " " + day + ", " + year + ", " + parse_time(comps[3]) + "* will be *" + comps[1].decode('utf-8') + "*!\n" + comps[5].decode('utf-8') + "\n The event will be held at *" + location  + "*.\n"
			message_one(out,user)

def herd_to_dm(user, channel, response):
	slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

def getGenericResponse():
	response = GENERIC_DICT[random.randint(1,14)]
	return response;

MESSAGE_DICT = \
{
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
	Action.kitchen:"Comments on the kitchen? Requests? Send them <http://bit.ly/KitchenFeedback|here>. Submissions are anonymous, so add your name if you want a response back."
}

def newUser(user):
	tsvFile = open("new_users.tsv", "a")
	out = csv.writer(tsvFile, delimiter='\t')
	out.writerow([user,CURRENT_TIME.strftime("%Y%m%d")])
	tsvFile.close()

def initaliseQuestions():
	card2 = questionnode(None,"",None)
	card0 = questionnode(None,"Do you want a building card or an ExCITe card?",None)



if __name__ == "__main__":
	READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
	if slack_client.rtm_connect():
		print("Mascat connected and running.")
		while True:

			# See how many days it's been since the last date update.
			time_delta = datetime.date.today() - CURRENT_TIME
			# If it's been at least a day, update the date and
			# check if we need to greet any recent new users.
			if time_delta.days > 0:
				print("New Day")
				CURRENT_TIME = datetime.date.today()

				with open('new_users.tsv', 'rb') as fin, open('temp.tsv', 'wb') as fout:
					writer = csv.writer(fout, delimiter="\t")
					for row in csv.reader(fin, delimiter="\t"):
						if (CURRENT_TIME - datetime.datetime.strptime(row[1],"%Y%m%d").date()).days >= 1:
							messageOneWithGreeting("Welcome to the ExCITe Slack team. I'm Mascat. Ask me questions. You've got the touch.",row[0])
						else:
							writer.writerow(row)
				shutil.copy("temp.tsv","new_users.tsv")
				os.remove("temp.tsv")

			time_delta = datetime.date.today() - PREVIOUS_REMINDER_DATE
			if time_delta.days > 28:
				print("New Month")
				# ADD POST TO GENERAL BOARD ABOUT EXISTANCE


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
					messageOneWithGreeting(getGenericResponse(),user)
				else:
					messageOneWithGreeting(MESSAGE_DICT[action],user)
			time.sleep(READ_WEBSOCKET_DELAY)
	else:
		print("Connection failed. Invalid Slack token or bot ID?")
