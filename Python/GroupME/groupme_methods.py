from groupme_setup import *


db2 = SqliteDatabase('***.db')


def addMediatoFile(member_pics, media_type):
# Creates dict of all messages with a video or image
	for message in Messages.select().order_by(Messages.date_and_time.asc()):

		if message.media not in member_pics and message.media not in [None, 'null']:

			if media_type == "Videos" and message.media[8:11:]=="v.g":
				#print(message.media)
				member_pics.append(message.media)
				member_pics.append({message.likes: message.media})

			if media_type == "Pictures" and message.media[8:11:]=="i.g":
				#print(message.media)
				member_pics.append(message.media)
				member_pics.append({message.likes: message.media})

	return member_pics


def createLikesMediaFolders(media_type = "Videos"):
# Lists pictures and videos by person so everyone's individual contributions can be viewed easily.
	filePath = "c:/***/" + media_type + "/"
	x=1
	member_pics = []
	member_pics = addMediatoFile(member_pics, media_type)
	for item in member_pics:
		try:
			for key,value in item.items():
				if not os.path.exists(filePath + str(key)):
					os.makedirs(filePath + str(key))

				if media_type == "Pictures":
					filename = filePath + str(key) + '/' + str(x) + '.jpg'

				if media_type == "Videos":
					filename = filePath + str(key) + '/' + str(x) + '.mp4'

				f = open(filename, "wb")
				f.write(requests.get(value).content)
				f.close()
			x+=1
		except:
			None


def createConsecMediaFolders(media_type = "Pictures"):
# Lists pictures and videos by numbers so a timelapse of material can be created easily
	filePath = "c:/***/" + media_type + "/"
	x=1
	member_pics = []
	member_pics = addMediatoFile(member_pics, media_type)
	for item in member_pics:
		try:
			for key,value in item.items():
				if not os.path.exists(filePath):
					os.makedirs(filePath)

				if media_type == "Pictures":
					filename = filePath + str(x) + '.jpg'

				if media_type == "Videos":
					filename = filePath + str(x) + '.mp4'

				f = open(filename, "wb")
				f.write(requests.get(value).content)
				f.close()
			x+=1
		except:
			None


def addAvatarsToFile():
# Adds avatars to file. This function is largely useless as the links seem to be protected
	filePath = "c:/***/Avatars/"
	member_avatars = []
	for message in Messages.select().order_by(Messages.date_and_time.asc()):
			if message.avatar_url not in member_avatars and message.avatar_url not in [None, 'null']:
				print(message.avatar_url)
				member_avatars.append(message.avatar_url)
				member_avatars.append({message.poster: message.avatar_url})

	for item in member_avatars:
		try:	
			for key,value in item.items():
					if not os.path.exists(filePath):
						os.makedirs(filePath)

					filename = filePath + str(key) + '.jpg'
					f = open(filename, "wb")
					f.write(requests.get(value).content)
					f.close()
		except:
				None
	return member_avatars


def timeList(first_message_time, days_of_group):
	temp_list = [datetime.datetime.fromtimestamp(first_message_time) + datetime.timedelta(days = i) for i in range(days_of_group + 1)]
	return [item - datetime.timedelta(seconds = item.second) for item in temp_list]


def memberTracking(the_time):
# Old method based on the original membership of an old group. Method is flawed as messages containing too many additions or subtractions will not have full numbers captured.
	
	# This value would have to be changed to reflect the addition and removal of people from the group.
	current_members = 6
	kicks = adds = leave = rejoined = 0
	first_time = None
	members_overtime = []

	for times in the_time:
		second_time = time.mktime(times.timetuple())

		if first_time != None:
			for message in Messages.select().where(Messages.date_and_time >= first_time, Messages.date_and_time <= second_time):
				if message.text != None:
					if message.system_check == True and "from the group" in message.text:
						if "," in message.text:
							kicks += (1 + message.text.count(','))
							current_members -= (1 + message.text.count(','))
						else:
							kicks += (1 + message.text.count(' and '))
							current_members -= (1 + message.text.count(' and '))
					if "added" in message.text and "to the group" in message.text:
						if "," in message.text:
							adds += (1 + message.text.count(','))
							current_members += (1 + message.text.count(','))
						else:
							adds += (1 + message.text.count(' and '))
							current_members += (1 + message.text.count(' and '))
					if "has left the group" in message.text:
						leave += 1
						current_members -= 1
					if "rejoined the group" in message.text:
						rejoined += 1
						current_members += 1
		
		members_overtime.append(current_members)

		first_time = time.mktime(times.timetuple())

	with open('Member Times.csv', 'w', newline = '') as the_file:
		message_writer = csv.writer(the_file)
		header_list = [
			"Time", 
			"Members",
		]
		message_writer.writerow(header_list)

		x = 0
		for times in the_time:
			fill_list = []
			fill_list.append(times.strftime("%m/%d/%y"))
			fill_list.append(members_overtime[x])
			message_writer.writerow(fill_list)
			x += 1

	print("{} created".format("Member Times.csv"))
	print()

	return members_overtime


def postTracking(the_time, this_id):
#Tracks posts, likes, and likes given overtime for an individual member (this_id). 
#This method does spit out a CSV file, but it is incomplete. 
#Meant to track 2 week running average of posts, likes received, and likes given as well as the totals (all time) of those three values
	first_time = None
	posts_counter = []
	likes_counter = []
	given_counter = []
	posts_overtime = []
	likes_overtime = []
	given_overtime = []
	days_tracked = 0

	for times in the_time:
		second_time = time.mktime(times.timetuple())
		todays_posts = 0
		todays_likes = 0
		todays_given = 0

		if days_tracked < 15:
			days_tracked += 1
		else:
			posts_counter = posts_counter[1::]
			likes_counter = likes_counter[1::]
			given_counter = given_counter[1::]

		if first_time != None:
			for message in Messages.select().where(Messages.date_and_time >= first_time, Messages.date_and_time <= second_time):
				if message.sender_id == this_id:
					todays_posts += 1
					todays_likes += message.likes
				else:
					if str(this_id) in message.fav_by:
						todays_given += 1
			#if len(posts_overtime) == 0:
			#	posts_overtime.append(1)
			#elif todays_posts == 0:
			#	posts_overtime.append(posts_overtime[-1]+1)
			#else:
			#	posts_overtime.append(0)
		posts_counter.append(todays_posts)
		likes_counter.append(todays_likes)
		given_counter.append(todays_given)
		z = 0

		for number in posts_counter:
			z += number
		posts_overtime.append(z)
		posts_overtime.append(z / 14)

		z = 0
		for number in likes_counter:
			z += number
		likes_overtime.append(z)
		likes_overtime.append(z / 14)

		z = 0
		for number in given_counter:
			z += number
		given_overtime.append(z)
		given_overtime.append(z / 14)
		
		first_time = time.mktime(times.timetuple())

		

	with open(Users.select().where(Users.user_id == this_id).get().name + '.csv', 'w', newline = '') as the_file:
		message_writer = csv.writer(the_file)
		header_list = [
			"Time", 
			"Posts",
			"Likes Received",
			"Likes Given",
			"Posts",
			"Likes Received",
			"Likes Given",
		]
		message_writer.writerow(header_list)

		x = 0
		for times in the_time:
			fill_list = []
			fill_list.append(times.strftime("%m/%d/%y"))
			fill_list.append(posts_overtime[x])
			fill_list.append(likes_overtime[x])
			fill_list.append(given_overtime[x])
			fill_list.append(posts_overtime[x+1])
			fill_list.append(likes_overtime[x+1])
			fill_list.append(given_overtime[x+1])
			message_writer.writerow(fill_list)
			x += 2

	print("{} created".format(Users.select().where(Users.user_id == this_id).get().name))
	print()

	return None


def groupData():
#Adds and kicks currently not functioning 100% correctly because of messages which have more than 7 people added or removed don't include every name. Could be fixed.
	member_dict = {}
	for message in Messages.select().order_by(Messages.date_and_time.asc()):

		x = message.poster
		y = message.sender_id

		if y not in member_dict:
			member_dict[y] = []
			
		if x in ["GroupMe","operator","GroupMe Calendar"]:
			None
		elif x not in member_dict[y]:
			member_dict[y].append(x)
			member_dict[y].append({x:""})
		elif x not in member_dict[y][-1]:
			member_dict[y].append({x:""})
		else:
			if member_dict[y][-1][x] == "":
				member_dict[y][-1]["t1"] = message.date_and_time
				member_dict[y][-1][x] = 0
			else:
				member_dict[y][-1][x] = message.date_and_time - member_dict[y][-1]["t1"]

	for key, value in member_dict.items():
		for item in value:
			if type(item) is dict:
				for key2, value2 in item.items():
					if key2 != "t1" and value2 != "":
						
						years = int(value2)//int(365.25*24*60*60)
						days = int(value2)%int(365.25*24*60*60)//int(24*60*60)
						hours = int(value2)%int(365.25*24*60*60)%int(24*60*60)//int(60*60)
						minutes = int(value2)%int(365.25*24*60*60)%int(24*60*60)%int(60*60)//60
						seconds = int(value2)%int(365.25*24*60*60)%int(24*60*60)%int(60*60)%60
						#print(key2 + ": " + str(years) + " Years " + str(days) + " Days " + str(hours) + " Hours " + str(minutes) + " Minutes " + str(seconds) + " Seconds")

	posts = 0
	likes = 0
	media = 0
	words = 0
	kicks = 0
	adds = 0
	leave = 0
	rejoined = 0
	media_list = []
	for message in Messages:
		posts += 1
		likes += message.likes
		if message.text != None:
			if message.system_check == True and "from the group" in message.text:
				if "," in message.text:
					kicks += (1 + message.text.count(','))
				else:
					kicks += (1 + message.text.count(' and '))
			if "added" in message.text and "to the group" in message.text:
				if "," in message.text:
					adds += (1 + message.text.count(','))
				else:
					adds += (1 + message.text.count(' and '))
			if "has left the group" in message.text:
				#print(message.text)
				leave += 1
			if "rejoined the group" in message.text:
				#print(message.text)
				rejoined += 1
		if message.media[0:4:] == "http":
			media += 1


	print()
	print("Posts: " + str(posts))
	print("Likes: " + str(likes))
	print("Media: " + str(media))
	print("Adds: " + str(adds))
	print("Kicks: " + str(kicks))
	print("Left: " + str(leave))
	print("Rejoined: " + str(rejoined))


def wordSearch():
#Searches for the number of times a post contained at least one instance of the word and returns all message featuring that word
	print()
	word = input("What word would you like to search for? ").lower()
	y = 0

	for message in Messages.select().where(Messages.text != None):
		if word in message.text.lower().split():
			y += 1
			t1 = datetime.datetime.fromtimestamp(message.date_and_time)
			uprint(t1.strftime("%m/%d/%y") + " " + t1.strftime("%H:%M:%S") + " " + message.user_id + ": " + message.text)
	print(str(y) + " posts containing the word " + word)
	
	z = input("Again? [Yn]")
	if z.lower() == 'y':
		wordSearch()
	else:
		return None
		