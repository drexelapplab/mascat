import os
import time
import urllib2
from slackclient import SlackClient

BOT_ID = os.environ.get("BOT_ID")

#constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"

MONTH_DICT = { '1':'January', '2':'February', '3':'March', '4':'April', '5':'May', '6':'June', '7':'July', '8':'August', '9':'September', '10':'October', '11':'November', '12':'December' }

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
			if output and 'channel' in output:
				ch = slack_client.api_call("channels.info", channel=output['channel'])
				gr = slack_client.api_call("groups.info", channel=output['channel'])
				if ch['ok'] == False and gr['ok'] == False:
					is_im = True
				else:
					is_im = False	
				print(is_im)
			if output and 'text' in output and AT_BOT in output['text'] and not is_im:
				print(output['user'])
				print(output['channel'])
				return output['user'], output['channel']
			print(output['type'])
	return None,None

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

# Takes a string formatted like "00:00:00AM" and formats it to "00:00AM".
def parse_time(time_string):
	first_part = ":".join(time_string.split(":")[:2])
	parts = time_string.split(" ")
	last_part = parts[1]
	return first_part + last_part
	
# Gets all events and sends notifications of all of them to the user.
def getEvents():
	data = urllib2.urlopen("https://docs.google.com/spreadsheets/d/1uKLG9WQOLwQ56dewfKFZDwehy_vs0EXN1jXfdMmNbwY/pub?gid=224197384&single=true&output=tsv")
	user = "U034LKGHE"
	# user = "U04JCJPLY"
	first = True
	for row in data:
		if first:
			first = False
			continue
		else:
			comps =  row.split("\t")
			month,day,year = parse_date(comps[2])
			location = comps[4].decode('utf-8')
			location = location.rstrip('.')
				
			out = "Hi " + slack_client.api_call("users.info", user=user)['user']['profile']['first_name'] + ", *" + month + " " + day + ", " + year + ", " + parse_time(comps[3]) + "* will be *" + comps[1].decode('utf-8') + "*!\n" + comps[5].decode('utf-8') + "\n The event will be held at *" + location  + "*."
			
			message_one(out,user)

def herd_to_dm(user, channel):
	response = "Baby, we can talk, but not here. Send me a DM."
	slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

if __name__ == "__main__":
	getEvents()
	READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
	if slack_client.rtm_connect():
		print("Mascat connected and running.")
		while True:
			user, channel = parse_slack_output(slack_client.rtm_read())
			if user and channel:
				herd_to_dm(user, channel)
			time.sleep(READ_WEBSOCKET_DELAY)
	else:
		print("Connection failed. Invalid Slack token or bot ID?")
