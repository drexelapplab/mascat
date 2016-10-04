import os
from slackclient import SlackClient

#instantiate Slack client
slack_client = SlackClient('xoxp-2177895914-3156662592-81784082695-cb05829120')

if __name__ == "__main__":
	files = open('data_usage.csv', 'w')
	files.truncate()
	data_used = 0
	
	userlist = slack_client.api_call("users.list")
	for user in userlist['members']:
		filelist = slack_client.api_call("files.list", user=user['id'])
		for file in filelist['files']:
			data_used += file['size']
			data_used = round(float(data_used/1024),3)
		files.write(user['name'] + "," + str(data_used) + "\n")
		data_used = 0
