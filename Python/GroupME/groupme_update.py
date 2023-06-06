from groupme_setup import *


def messageNum(message_numID):
	return Messages.select().where(Messages.num_id == message_numID).get().message_id


initialize()

members, user_members = setMembersDict()
#Establishes CSV before the update for comparison
setCSV(members, user_members, "Preupdate Groupme.csv")

#Grabs the last message and the most recent message from a month prior to now for update
max_message = Messages.select().order_by(Messages.num_id.desc()).get()
min_message = Messages.select().order_by(Messages.num_id.asc()).get()

#marks the id of the messages
min_message_count = min_message.num_id
#Calculates the number of messages between the most recent message and the first message
limit_num = max_message.num_id - min_message_count + 1
updated_messages = ""

while limit_num > 0:
	min_message_hold = min_message_count
	limit_hold = 0

	if limit_num >= 100:
		limit_hold = 100
		limit_num -= 100
	else:
		#If less than 100 messages a single request will retrieve remaining messages. The limit is adjusted to get exactly the last message.
		limit_hold = limit_num
		limit_num = 0
		
	#grabs messages from groupme API
	updated_messages = requests.get(URL + "/groups/" + MASTER_GROUP_ID + "/messages" + TOKEN, {'after_id': messageNum(min_message_count), 'limit': limit_hold}).json()['response']
	
	#Updates like count of all prior posts
	for message in updated_messages['messages']:
		min_message_count += 1
		Messages.update(fav_by = message['favorited_by'], likes = len(message['favorited_by'])).where(Messages.num_id == min_message_count).execute()
		
		
	print("Messages {} to {} updated".format(min_message_hold, min_message_count-1))

after_id = str(max_message.message_id)
groupme = {'messages':'1'}

getMessages(before_after_id = after_id, x = max_message.num_id, before = False)

print()
setCSV(members, user_members, "Postupdate Groupme.csv")