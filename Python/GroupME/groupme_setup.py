import json
import time
import os
from collections import Counter
import matplotlib.pyplot as plt
from jsonfield import JSONField
import csv
import sys
import ast
import requests
import datetime
import re
from peewee import *


URL = "https://api.groupme.com/v3"
# Specific Token from GroupMe. Should be inputed by User
TOKEN = '?token=***'
# Input ID for group messages are coming from
MASTER_GROUP_ID = '***'
db = SqliteDatabase('group_info.db')  # Name Messages database file
db2 = SqliteDatabase('users.db')  # Name user database file


class Messages(Model):
    """Sets up database entry structure for each message.
Linked to database named db in source."""
    class Meta:
        database = db

    # Unique GroupMe ID should be same as sender ID except in cases
    # with system messages (most likely)
    user_id = TextField(null=False)
    # Unique GroupMe ID of sender
    sender_id = TextField(null=False)
    # Current Avatar of User. Returned as link
    avatar_url = TextField(null=True)
    # Indicates if the sender was a user or system
    sender_type = TextField(null=False)
    # True if sender was system. Redundant to sender_type
    system_check = BooleanField(null=False)
    # ID of sender system. Appears each id is different
    source_guid = TextField()
    # ID of message sent from GroupMe. Non-sequential integer within
    # group since ID appears to be for whole of GroupMe
    message_id = TextField()
    # GroupMe given integer for each Group
    group_id = TextField()
    # Non-GroupMe generated ID tracking messages with sequential integer
    num_id = PrimaryKeyField(null=False)
    # Current name in group
    poster = TextField()
    # Counts number of users that liked the post
    likes = IntegerField(null=False)
    # Gives url if picture or video. Includes other media type in post
    # if not picture or video
    media = TextField(null=True)
    # Timestamped computer time integer
    date_and_time = FloatField()
    # Full text of post
    text = TextField(null=True)
    # Number IDs of group members who liked post
    fav_by = TextField()
    # Full text from API for each message
    full_text = TextField()


class Users(Model):
    """Sets up database of user_ids matched with entered
    corresponding selected names"""
    user_id = TextField()
    name = TextField()

    class Meta:
        database = db2


def initialize():
    """Connects to database defined as db in source"""
    db.connect()
    db.create_tables([Messages], safe=True)


def initialize2():
    db2.connect()
    db2.create_tables([Users], safe=True)


def getMessages(before_after_id=None, x=0, before=True):
    """Communicates with GroupMe API to grab each message string
    and create new entries in database"""

    #time.sleep(5)

    groupme = {'messages': '1'}

    while groupme['messages'] != []:

        try:

            if before is True:
                groupme = requests.get(URL + '/groups/' +
                                       MASTER_GROUP_ID + '/messages' + TOKEN,
                                       {'before_id': before_after_id,
                                        'limit': '100'}).json()['response']
                y = groupme['count'] - x
                #uprint(groupme)

            else:
                groupme = requests.get(URL + '/groups/' +
                                       MASTER_GROUP_ID + '/messages' + TOKEN,
                                       {'after_id': before_after_id,
                                        'limit': '100'}).json()['response']
                y = x
            # count gives how many messages are in response string
            l = y

            for message in groupme['messages']:
                #uprint(message)
                try:
                    if before is True:
                        l -= 1

                    else:
                        l += 1

                    # inputs to database entry from GroupMe response.
                    # Descriptions in Messages class
                    Messages.create(
                        user_id=message['user_id'],
                        sender_id=message['sender_id'],
                        avatar_url=message['avatar_url'],
                        sender_type=message['sender_type'],
                        system_check=message['system'],
                        source_guid=message['source_guid'],
                        message_id=message['id'],
                        group_id=message['group_id'],
                        num_id=l,
                        poster=message['name'],
                        likes=len(message['favorited_by']),
                        media=isThereMedia(message['attachments']),
                        date_and_time=message['created_at'],
                        text=message['text'],
                        fav_by=message['favorited_by'],
                        full_text=str(message)
                        )
                    before_after_id = message['id']
                    x += 1
                except:
                    print("Bad Message")
            # Updates if message string has been saved
            if y != l:
                print("Messages {} to {} saved".format(y, l))
        # When no more messages can be recieved give this message
        except:
            print()
            print("Done")
            print()
            break


def uprint(*objects, sep=' ', end='\n', file=sys.stdout):
    """Printing method to deal with strange characters."""
    enc = file.encoding

    if enc == 'UTF-8':
        print(*objects, sep=sep, end=end, file=file)

    else:
        f = lambda obj: str(obj).encode(
                                        enc,
                                        errors='backslash'
                                        'replace').decode(enc)
        print(*map(f, objects), sep=sep, end=end, file=file)


def isThereMedia(is_there):
    """Changes media input to either url, location lat/long, or media type"""
    if is_there == []:
        return False

    else:
        if is_there[0]['type'] == "image" or is_there[0]['type'] == "video":
            # Saves images or videos at urls
            return str(is_there[0]['url'])

        elif is_there[0]['type'] == 'location':
            # returns latitude and longitude if type is location
            return 'lat: ' + str(is_there[0]['lat'] +
                                 ", lon: " +
                                 str(is_there[0]['lon']))

        else:
            # gives back media type
            return is_there[0]['type']


def createUsersDB():
    """Not done yet. Meant to make database of user entered names to match ID.
    Names used throughout program, most notably for folder creation"""

    # Simplifies text that is used multiple times
    text_noti = 'membership.notifications.'
    text_noti2 = 'membership.announce.'
    # Gets full text of first message
    first_message = ast.literal_eval(Messages.select().get().full_text)
    # Easier to search list than dictionary. All ID's ever in group
    member_track = [first_message['event']['data']['adder_user']['id']]
    # Dictionary of ID and all usernames associated with the ID
    member_dict = {first_message['event']['data']['adder_user']['id']:
                   [first_message['event']['data']['adder_user']['nickname']]}

    for message in Messages.select().where(Messages.system_check
                                           ).order_by(Messages.
                                                      date_and_time.asc()):

        try:

            # hold for event type
            evnt = ast.literal_eval(message.full_text)['event']['type']
            # Checks if system message included the addition of a new user.
            # Added names are typically closest to true irl names
            if evnt == text_noti2 + 'added' or evnt == text_noti2 + 'rejoined':
                # GroupMe tracks the IDs of added users
                for key, value in ast.literal_eval(message.full_text
                                                   )['event']['data'].items():
                    # Finds original names of added users
                    if key == 'added_users':
                        # IDs added are sent back as list
                        for items in value:
                                # If ID is not yet tracked
                                # in member tracking
                                # list it is added and
                                # the corresponding nickname is put in
                                if items['id'] not in member_track:
                                    member_track.append(items['id'])
                                    member_dict[items['id']
                                                ] = [items['nickname']]

                                else:
                                    # If ID has been tracked then the
                                    # new nicknames are added the
                                    # dictionary to help with identification
                                    if items['nickname'] not in member_dict[items['id']]:
                                        member_dict[items['id']].append(items['nickname'])

        # The exception is thrown on name changes
        except:
            None
    # Looks through member dictionary and gives IDs and usernames to identify users.
    # Database entry is created based on user input for name
    for key, value in member_dict.items():

        print(str(key) + ": " + str(value))
        member_dict[key] = input("Who is this? ")

        Users.create(
            user_id=key,
            name=member_dict[key]
            )

        print()
    # Calls back just entered names with their corresponding GroupMe IDs
    for user in Users.select():
        print(user.user_id + ": " + user.name)

    print()

    return None


def setMembersDict():
    """Records current usernames associated with user's GroupMe ID. Needs to be updated to strip user_members and to include DB"""

    members = []
    for message in Messages:
        check = False
        for member in members:
            if message.sender_id == member['id'] or message.system_check or message.media == 'event':
                # Makes sure only to capture messages by users
                check = True
        if check is False:
            if message.poster != 'GroupMe':
                # If user_id isn't already in the list this value is added
                members.append({'id': message.sender_id, 'name': message.poster})

    # Saves member list at just users. This is unnecessary now with user DB.
    # Left in because update currently runs with this structure
    user_members = members[:]

    # Loop adds remaining system id's to member list
    # to give a complete list for CSV commmand
    for message in Messages:

        check = False
        for member in members:
            if message.sender_id == member['id']:
                check = True
        if check is False:
            members.append({'id': message.sender_id, 'name': message.poster})

    return members, user_members


def setCSV(members, user_members, name='GroupMe.csv'):
    """Publishes CSV file based on database. Name inputed by user
    in def line. Should be updated to remove user_members"""

    with open(name, 'w', newline='') as the_file:
        message_writer = csv.writer(the_file)
        our_members = [member['name'] for member in user_members]
        # Header rows
        header_list = [
            "Poster",
            "Text",
            "Likes",
            "Media",
            "DD/MM/YY",
            "H:M:S",
            "Post Number",
        ]

        header_list.extend(our_members)

        member_count=1

        for member1 in our_members:
            #Set headers for correlation
            
            #Helps avoid mirrored correlation counts
            for member2 in our_members[member_count:]:
            
                try:
                    header_list.append(member1+"_"+member2)
                except:
                    None

            member_count += 1

        message_writer.writerow(header_list)

        for message in Messages.select():
            fill_list = []

            for member in members:
                # First looks for sender_id and then matches name
                if member['id'] == message.sender_id:
                    fill_list.append(member['name'])
                    break

            # Puts text into fill list
            fill_list.append(message.text)
            # Puts the number of likes given
            fill_list.append(message.likes)

            # Simplifies media to Yes or empty string
            if message.media == "False":
                fill_list.append("")

            else:
                fill_list.append("Yes")

            try:
                t1 = datetime.datetime.fromtimestamp(message.date_and_time)
            except:
                t1 = datetime.datetime.fromtimestamp(0)
            # Enters day, month, year based on timestamp
            fill_list.append(t1.strftime("%m/%d/%y"))
            # Enters hours, minutes, and seconds based on timestamp
            fill_list.append(t1.strftime("%H:%M:%S"))
            # Enters sequential message primary key
            fill_list.append(message.num_id)
            total = 0
            favorite_list = []

            # If the message is liked by at least one person
            # separates the list of likes into list of separate user_ids
            if message.fav_by != "" or []:
                favorite_list = ast.literal_eval(message.fav_by)
                favorite_list = [x.strip() for x in favorite_list]

            for member in user_members:

                # In order of the members that are users indicates
                #  if that user likes the post
                if member['id'] in favorite_list:
                    fill_list.append("x")
                    total += 1

                else:
                    fill_list.append("")

            member_count = 1

            for member1 in user_members:
            #Set headers for correlation
            
            #Helps avoid mirrored correlation counts
                for member2 in user_members[member_count:]:
            
                    if member1['id'] in favorite_list and member2['id'] in favorite_list:
                        fill_list.append("x")
                    else:
                        fill_list.append("")

                member_count += 1

            try:
                message_writer.writerow(fill_list)

            # If message text is unpublishable, uses empty string instead.
            # Not working on first run for some reason
            except:
                fill_list[1] = ""
                message_writer.writerow(fill_list)

    print("{} created".format(name))
    print()
