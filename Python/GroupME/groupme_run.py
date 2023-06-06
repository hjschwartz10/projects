from groupme_setup import *
from groupme_methods import *

if __name__ == "__main__":
	#Run script. Test of different methods and run scripts to get first instance of GroupMe data.
	initialize()
	initialize2()


	#Gets all groups that given user token is associated with and prints them out
	#my_groups = requests.get(URL + '/groups' + TOKEN, {'per_page': 100}).json()['response']
	#for line in my_groups:
	#	uprint(line['name'] + ": " + line['group_id'])
	

	#puts entire API request for group names into a JSON file
	#json_file = open('Groups_Full.json', 'w')
	#json.dump(my_groups, json_file, indent = 4, sort_keys=False)
	#json_file.close()


	#Uncomment to download entire group into database. Changes need to be made to GroupMe.py for token and group ID
	#getMessages()
	

	#Uncomment to run Users DB entry. This DB was created to rename users outside of their groupme names. Used only for the postTracking method.
	#createUsersDB()

	
	#Uncomment to set members database. Necessary to create CSV file.
	members, user_members = setMembersDict()


	#Uncomment to create CSV file
	#setCSV(members, user_members, "group_test.csv")
	

	#Print list of user members and their corresponding IDs
	#for member in user_members:
	#	print(member['name'] + ": " + member['id'])
	

	#These variables and method allow the user to track the number of days after the start of the group that each method was sent. Potential applications in tracking likes and posts over time so they can be analyzed on a rolling scale.
	first_message_time = Messages.select().order_by(Messages.date_and_time.asc()).get().date_and_time
	days_of_group = (datetime.datetime.now() - datetime.datetime.fromtimestamp(first_message_time)).days
	the_time = timeList(first_message_time, days_of_group)
	#uprint(str(days_of_group) + " days group active")


	#One of the methods designed to use the time of each post to generate a rolling dataset. Need to input the sender_id for this method to run. Method is not currently running correctly.
	#postTracking(the_time, ***)


	#Method that adds all avatar images to a file location (which must be updated in the method). Not currently useful as the avatars seem to be restricted from access by GroupME.
	#addAvatarsToFile()
	

	#Creates a single media folder that lists each image or video (depending on the entry into the method) in post order
	#createConsecMediaFolders("Pictures")


	#Creates a media folder with images or videos (depending on the entry into the method) divided into separate folders by the number of likes
	#createLikesMediaFolders("Pictures")

	#Gives the number of total posts, likes, media posts, adds, kicks, leaves, and rejoins. This method is not currently functioning correctly for the adds and kicks because over a certain number, groupme doesn't give all the names
	#groupData()

	#Search for the number of instances and posts containing the word searched
	#wordSearch()