import os
import time
import urllib2
import random
from slackclient import SlackClient
from enum import Enum

BOT_ID = os.environ.get("BOT_ID")

#constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"

class Action(Enum):
	generic = 1
	redirect = 2
	event = 3
	printing = 4
	card = 5
	conference = 6
	restroom = 7

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
	3:"Say that again, but slower.", 
	4:"I don't have real ears, so I have no idea what you just said.", 
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
			if output and 'channel' in output and output['user'] != BOT_ID:
				ch = slack_client.api_call("channels.info", channel=output['channel'])
				gr = slack_client.api_call("groups.info", channel=output['channel'])
				if ch['ok'] == False and gr['ok'] == False:
					is_im = True
				else:
					is_im = False	
				if 'text' in output:
					if not is_im and AT_BOT in output['text']:
						return output['user'], output['channel'], Action.redirect
					elif is_im:
						if 'event' in output['text'].lower():
							return output['user'], output['channel'], Action.event
						elif 'print' in output['text'].lower():
							return output['user'], output['channel'], Action.printing
						elif 'card' in output['text'].lower():
							return output['user'], output['channel'], Action.card
						elif 'conference' in output['text'].lower():
							return output['user'], output['channel'], Action.conference
						elif 'restroom' in output['text'].lower() or 'bathroom' in output['text'].lower():
							return output['user'], output['channel'], Action.restroom
						else:
							return output['user'], output['channel'], Action.generic
				print(output['type'])
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
	slack_client.api_call("chat.postMessage", channel=im['channel']['id'], text=getGreetingResponse() + " " + slack_client.api_call("users.info", user=user)['user']['profile']['first_name'] + ". " + message_text, as_user=True)

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

ACTION_DICT = \
{
	Action.redirect:"Baby, we can chat, but not here. Send me a DM.",
	Action.event:"bad",
	Action.printing:"To use the ExCITe printer, visit <http://144.118.173.220:8000/rps/pprint.cgi|our printing website>, enter '101' as the department user, and hit log in. There's no password. The ExCITe printer is located in the EGS.",
	Action.card:"Looking for card access? Contact <@U04JCJPLY|Lauren> for more information.",
	Action.conference:"Ye can't get ye conference room.",
	Action.restroom:"The men's bathroom code is [3] and [4] simultaneously, followed by [1]. The women's bathroom doesn't have a password.",
	Action.generic:"bad"
}


if __name__ == "__main__":
	READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
	if slack_client.rtm_connect():
		print("Mascat connected and running.")
		while True:
			user, channel, action = parse_slack_output(slack_client.rtm_read())
			if user and channel:
				if action == Action.redirect:
					herd_to_dm(user,channel,ACTION_DICT[action])
				elif action == Action.event:
					getEvents(user)
				elif action == Action.generic:
					messageOneWithGreeting(getGenericResponse(),user)
				else:
					messageOneWithGreeting(ACTION_DICT[action],user)
			time.sleep(READ_WEBSOCKET_DELAY)
	else:
		print("Connection failed. Invalid Slack token or bot ID?")
