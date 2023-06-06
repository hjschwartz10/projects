from fantasydrafter import *


posList = ['QB', 'WR', 'RB', 'TE', 'K', 'DST']
# Changes can be made to account for already drafted 
# players by removing them from ID selection
# Also could improve search function
# Neither necessary. Do need to add scarcity

if __name__ == '__main__':

    initialize()

    # Enters data from csv into database
    with open('fantasydata2022_2.csv') as fantasydata:
        for row in csv.reader(fantasydata):
            Player.create(
                key=tryInt(row[0]),
                posRank=tryInt(row[6]),
                adp=tryFloat(row[9]),
                position=str(row[2]),
                team=str(row[1]),
                firstName=str(row[3]),
                lastName=str(row[4]),
                injury=tryFloat(row[5]),
                ovrRank=tryFloat(row[7]),
                stdDevRank=tryFloat(row[8]),
                rankDiff=tryFloat(row[10]),
                vbdPoints=tryFloat(row[11]),
                projected=tryFloat(row[12]),
                vbdPosRef=tryFloat(row[13]),
                rankPosRef=tryFloat(row[15]),
                rankPoints=tryFloat(row[14]),
                bye=tryFloat(row[16]),
                upside=tryFloat(row[17]),
                downside=tryFloat(row[18]),
                multiplier=False
                )

    # Indicates that data is uploaded
    print('='*100)
    print()
    print("Data Uploaded")
    print()
    print('='*100)
    print('\n')
    begin = input('Begin? [Y/n] ').lower().strip()
    print()

    # Joke code that starts program regardless of entry
    if begin == 'y':
        print("Sweet")

    else:
        print("...We are starting anyway")

    # User enters name
    print('\n')
    # Starts list of drafter names
    drafterList = []
    yourName = input("What is your name? ").title().strip()
    print()

    drafterList.append(yourName)
    print("Welcome {}!".format(yourName))


    print('\n')

    # Asks user for number of drafters until an integer is entered
    while True:
        try:
            numDrafters = int(input("How many people in your league? "))
            print()
            print("Great, {} person snake draft".format(numDrafters))
            break

        except:
            print("Thats not a valid entry, try again")

    print('\n')
    x = 1

    # Gathers name of all drafters by user entries
    while x < numDrafters:
        newDrafter = input("What is the name of the drafter"
                           " #{}? ".format(x+1)).title().strip()

        if begin != 'y' and newDrafter == "Raghav":
            print("Nice try, your name is Raghav."
                  " I'll call this person Raghav2")
            newDrafter = "Raghav2"

        drafterList.append(newDrafter)
        print()
        x += 1

    print("Here are your drafters: ")
    print()

    # Prints the names of all drafters
    for people in drafterList:
        print(people)

    print()

    # Gets the number of each position in the league
    while True:
        try:
            numQB = int(input("Need to determine roster. How many QB's? "))
            draftLen = numQB
            numWR = int(input("How many WR's? "))
            draftLen += numWR
            numRB = int(input("How many RB's? "))
            draftLen += numRB
            numTE = int(input("How many TE's? "))
            draftLen += numTE
            numFlex = int(input("How many Flex? "))
            draftLen += numFlex
            numK = int(input("How many K's? "))
            draftLen += numK
            numDST = int(input("How many DST's? "))
            draftLen += numDST
            numBen = int(input("How many bench spots? "))
            draftLen += numBen
            numList = [numQB, numWR +
                       numFlex, numRB +
                       numFlex, numTE,
                       numK, numDST]
            print()
            break

        except:
            print("Not an integer. Now you have to start over...")
            print('\n')

    # Based on number of players per position
    # gives number of rounds in draft
    print("{} rounds in the draft".format(draftLen))
    print()
    # Determines if this is a keeper league
    keeper = input("Is this a keeper league? [Yn] ").lower().strip()
    print()
    keeperNum = 0

    # If it is a keeper league figures out the number of keepers
    if keeper == 'y':
        while True:
            try:
                keeperNum = input("How many keepers? ")
                keeperNum = int(keeperNum)
                break

            except:
                print("Not a valid number")

    print()

    if keeper == 'y':
        print("Sweet, {} keepers".format(keeperNum))
        print()
        print("Need to set keepers")
        print()

        # Goes name by name and selects keepers
        for drafters in drafterList:
            if keeper == 'y':
                print("Who are {}'s keepers "
                      "(search by first name)".format(drafters))
                x = 1
                stupidList = []

                while x <= keeperNum:
                    print()
                    stupidList.extend(playerSearch(input("Keeper {}: "
                                                         .format(x)).title()))
                    print()

                    # ID of player drafted
                    thisID = checkInt("ID or 0(for none): ")
                    # Round that player is going to be drafted in
                    thisRound = checkInt("Round: ")

                    if thisID == 0:
                        x += 1
                    else:
                        x += savePlayer(thisID, drafters, thisRound, stupidList)

                currentTeam(drafters, posList)

            else:
                None

    else:
        print("No keepers")
        print('\n')

    print("Need to set draft order. "
          "Enter position in first round for each player")
    draftDict = {}

    # User enters pick number for each player in first round
    for drafter in drafterList:
        draftDict.update({drafter: 0})
        draftDict[drafter] = checkInt("{}'s pick: ".format(drafter))

    print()
    print("Draft order:")

    # Returns draft order after user entry
    for drafter in drafterList:
        print(drafter + ":" + str(draftDict[drafter]))

    print('\n')

    # User decides if they want to account for injuries
    # Accounting for injury involves a 70% or higher injury probability
    # These players are expected to miss 75% of games 10% of the time.
    # 93% of total projection
    if input("Account for injuries? [Yn] ").lower() == 'y':
        print()

        for player in Player.select().where(Player.injury >= .7):
            player.projected *= 0.93
            player.projected = round(player.projected, 2)
            player.save()
            print(player.firstName +
                  " " + player.lastName +
                  " " + str(player.injury*100) + "%")

        print("These players have had their projected"
              " score reduced to 93{} of the original".format("%"))

    else:
        print("No injuries taken into account")

    print("\n")
    print('Time to draft!')
    print()

    # Sets up variables for draft loop
    thisRound = 1
    currentDrafter = ""
    orderPick = 0
    even = False
    away = [0, 0]

    # Loop for conducting the draft
    while draftLen > 0:
        thisPick = 1

        # Odd number of round counts up
        if even is False:
            orderPick = 1

        # Even number rounds count down
        else:
            orderPick = numDrafters

        # Loop for each round
        while thisPick <= numDrafters:

            # Calculates rounds away for scarcity
            if even is False:
                away[1] = 2 * (numDrafters - orderPick) + 1
                away[1] = math.floor(away[1] / 2)
                away[0] = 2

            else:
                away[1] = 2 * (orderPick - 1) + 1
                away[1] = math.floor(away[1] / 2)
                away[0] = 2

            # Based on pick in round finds drafter name
            for key, value in draftDict.items():
                if int(value) == orderPick:
                    currentDrafter = key

            # Prints drafter round and pick number
            print(currentDrafter + " - Round {}, "
                  "Pick {}:".format(thisRound, thisPick))

            # Checks if a keeper pick is holding this draft spot
            if Player.select().where(thisRound == Player.theround, currentDrafter == Player.fanTeam):
                print("Keeper already selected")
                thisPick += 1

                # Changes pick based on odd or even number round
                if even is False:
                    orderPick += 1

                if even is True:
                    orderPick -= 1
                # Prints current team
                currentTeam(currentDrafter, posList)

            else:
                # If user is the drafter checks to see if team has enough a position
                # If it is then the ranks are discounted to favor non-selected positions
                if yourName == currentDrafter:
                    y = 0

                    while y < 6:
                        z = 0

                        for player in Player.select().where(yourName == Player.fanTeam, posList[y] == Player.position):
                            z += 1

                        if z >= numList[y]:
                            for player in Player.select().where(posList[y] == Player.position, Player.multiplier == False):
                                if player.vbdPoints != None and player.rankPoints is not None:
                                    if player.vbdPoints > 0:
                                        player.vbdPoints *= 0.8
                                        player.vbdPoints = round(player.vbdPoints, 2)

                                    else:
                                        player.vbdPoints /= 0.8
                                        player.vbdPoints = round(player.vbdPoints, 2)

                                    if player.rankPoints > 0:
                                        player.rankPoints *= 0.8
                                        player.rankPoints = round(player.rankPoints, 2)

                                    else:
                                        player.rankPoints /= 0.8
                                        player.rankPoints = round(player.rankPoints, 2)

                                # Multiplier tracks if the rank has already been lowered
                                player.multiplier = True
                                player.save()
                        y += 1

                    # Displays players available
                    displayRanks(away)
                    print()
                    search = "search"

                    while search == "search":
                        search = input("Search or Pick? ").lower()
                        # If user wants to search by position allows them to
                        # Once the player is done searching moves to player selection
                        if search == "search":
                            while True:
                                attempt = input("Input position: ").upper()

                                if attempt in posList:
                                    posSearch(attempt, away)
                                    break

                                else:
                                    print("Invalid entry")
                                    print()

                # If drafter is not user then moves on immediately
                else:
                    displayRanks(away)

                # Allows user to pick a player for team to draft
                stupidList = []
                stupidList.extend(playerSearch(input("Now Picking. Search: ").title()))
                print()

                thisID = checkInt("ID or None: ")
                print()
                # If user selects a player that is draftable then adds them
                # If not then lettuce returns 0 and the loop for the pick is reset
                lettuce = savePlayer(thisID, currentDrafter, thisRound, stupidList)
                thisPick += lettuce

                # If pick is correct then moves on to next pick based on round
                if lettuce == 1 and even == False:
                    orderPick += 1

                if lettuce == 1 and even == True:
                    orderPick -= 1
                currentTeam(currentDrafter, posList)
                print()

        # At end of round change the round from even to odd
        # or vice versa
        if even is True:
            even = False

        else:
            even = True

        draftLen -= 1
        thisRound += 1

    # When final round is complete all teams are printed
    print()
    print("Draft over. Here are the Teams:")

    for drafters in drafterList:
        currentTeam(drafters, posList)
