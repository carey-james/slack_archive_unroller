import json
import re
from glob import glob
from pathlib import Path
from datetime import datetime

def grab_users(root_dir):
	users = {}
	with open(str(root_dir / 'users.json')) as user_file:
		user_file_dic = json.loads(user_file.read())
		for user in user_file_dic:
			if user['profile']['display_name_normalized'] != '':
				users[user['id']] = user['profile']['display_name_normalized']
			else:
				users[user['id']] = user['profile']['real_name_normalized']
	return users

def user_lookup(match_obj, users):
	if match_obj.group(1) is not None:
		return f'`{users[match_obj.group(1)]}`'

def json_to_text(json_file_path, users):
	messages = ''
	with open(json_file_path) as day_file:
		day_file_dic = json.loads(day_file.read())
		for message in day_file_dic:

			name = users[message["user"]]
			timestamp = datetime.utcfromtimestamp(float(message["ts"])).strftime("%Y-%m-%d %H:%M:%S")
			text = message["text"]

			text = re.sub(r'<@(\w+)>', lambda m: user_lookup(m, users), text)

			if 'subtype' in message.keys():
				if message['subtype'] == 'channel_join':
					messages = f'{messages}**{name}** *{timestamp}* **:** `{name}` joined the channel.\n\n'
			else:
				messages = f'{messages}**{name}** *{timestamp}* **:** {text}\n\n'
	return messages

def main():
	slack_name = input('Slack name: ')
	root_dir = Path(input('Path to archive: '))
	out_name = input('Output file name: ')

	users = grab_users(root_dir)

	text = f'# {slack_name} \n\n'

	for channel in glob(str(root_dir / '*')):		
		if channel[-5:] != '.json':
			text = f'{text}---\n\n## Channel: {channel[(len(str(root_dir))+1):]}\n\n'
			days = glob(str(root_dir / channel / '*.json'))
			days.sort()			
			for day in days:
				messages = json_to_text(root_dir / channel / day, users)
				text = f'{text}{messages}\n\n'

	with open(f'{out_name}.md', 'w') as out_file:
		out_file.write(text)
	

if __name__ == '__main__':
	main()