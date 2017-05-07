import urllib2
import json
import sys
import getpass

def clientlogic():
        welcomeback = "Welcome back to the menu. Please type the command you wish to do." ##death to the string literals
        
        username = raw_input("Enter your username: ")
        password = getpass.getpass("Enter your password: ")


        def login():
                inputUrl = 'http://178.62.47.78:1080/player/login/%s/%s'%(str(username), str(password))
                try:
                        resp = urllib2.urlopen(inputUrl)        
                        resp1 = resp.read()
                        data = json.loads(resp1)
                        if data["status"] == "error":
                                print "Error: " + data["description"]
                                clientlogic()
                        else:
                                return data["key"]
                                
                except IOError as e:
                        print "Error: ", e


        def viewmenufirsttime():
                print '\n'
                print """
         ___   _ _____ _____ _    ___ ___ _  _ ___ ___  ___ 
    ~~~~| _ ) /_\_   _|_   _| |  | __/ __| || |_ _| _ \/ __|~~~~
~~~~~~~~| _ \/ _ \| |   | | | |__| _|\__ \ __ || ||  _/\__ \~~~~~~~~  
    ~~~~|___/_/ \_\_|   |_| |____|___|___/_||_|___|_|  |___/~~~~

Welcome back, %s!
Welcome to Team UCD's Battleship client!
Currently running on: http://battleship.doesnot.run
The available commands are:
- checkgame
- makeshot
- getturn
- getboard
- newgame
- logout
To return to the menu at any stage, hit enter without typing any command."""%(username[0].upper() + username[1:])
                activegames()
                menu()
        auth_key = login()
        glistURL = 'http://178.62.47.78:1080/player/%s/get_games/%s'%(str(username),str(auth_key))
        resp_glist = urllib2.urlopen(glistURL)
        resp1_glist = resp_glist.read()
        data_glist = json.loads(resp1_glist)
        gamelist = []
        for game in data_glist["active_games"]:
                gamelist.append(game)
                
        ## this function was wrote by Kumaran (specialk) in the first draft of the game code. it takes in an array and grid-ifys it, making it readable by a user.
        def grid(arr):
                print "   ",
                for i in range(10):
                    print i,
                print ""
                print ''
                for index, i in enumerate(arr):
                    if index < 10:
                        sys.stdout.write('0')   
                    print str(index)+" ",
                    for j in i:
                        print j,
                    print''
                print'\n'


        ## takes in two player names and creates a new game between those two players
        def newgame():
                player1id = username
                player2id = raw_input("Enter the user you wish to start a game against: ")
                if player2id == 'quit':
                        quit
                if player2id == '':
                        print welcomeback
                        print '  '
                        menu()
                inputUrl = 'http://178.62.47.78:1080/game/new/%s/%s/%s'%(str(player1id), str(player2id), str(auth_key))
                try:
                        resp = urllib2.urlopen(inputUrl)
                        resp1 = resp.read()
                        data = json.loads(resp1)# this returns a JSONified version of what was just read
                        if data["status"] == "error":
                                print "Error: " + data["description"]# makes figuring out errors nicer
                                menu()
                        else:
                                print data # if nothing goes wrong it just prints the JSONified data
                                menu()
                except IOError as e:
                        print "Error: ", e # error handling
                        menu()
                
                
        ##takes in a gameid, userid and coords and makes a shot and returns the result       
        def makeshot():
                gameid = raw_input("To make a shot, enter the game ID: ")
                if gameid == 'quit':
                        quit
                if gameid == '':
                        print welcomeback
                        print '  '
                        menu()
                playerid = username
                coords = raw_input("Now enter the coordinates you wish to make the shot at, in the form x,y: ")
                if coords == 'quit':
                        quit
                if coords == '':
                        print welcomeback
                        print '  '
                        menu()
                coordints = coords.split(',')
                inputUrl = 'http://178.62.47.78:1080/game/%s/make_shot/%s/%d/%d'%(str(gameid),str(playerid),int(coordints[1]),int(coordints[0])) ## same old URL pointing
                try:
                        resp = urllib2.urlopen(inputUrl)
                        resp1 = resp.read()
                        data = json.loads(resp1)
                        if data["status"] == "error":
                                print "Error: " + data["description"]
                                makeshot()
                        elif data["status"] == "ok":
                                print "Hit: " + str(data["hit"]) ## takes the JSON and formats it even further to just return a nice easy to read 'Hit' or 'Miss'
                                inputUrl = 'http://178.62.47.78:1080/game/%d/get_board/%s'%(int(gameid),str(playerid))
                                resp = urllib2.urlopen(inputUrl)
                                resp1 = resp.read()
                                data = json.loads(resp1)
                                grid (data["data"][playerid]["visible_board"])
                                print welcomeback
                                menu()             
                except IOError as e:
                        print "Error: ", e

        def placeship():
                gameid = int(raw_input("Enter the game ID you wish to place ships for: "))
                if gameid == 'quit':
                        quit
                if gameid == '':
                        print welcomeback
                        print '  '
                        menu()
                shiplength = int(raw_input("Enter the length you wish the ship to be (1-4): "))
                if shiplength == 'quit':
                        quit
                if shiplength == '':
                        print welcomeback
                        print '  '
                        menu()
                shipdir = int(raw_input("Enter the direction you wish the ship to go, 1 for horizontal, 0 for vertical: "))
                if shipdir == 'quit':
                        quit
                if shipdir == '':
                        print welcomeback
                        print '  '
                        menu()
                coords = raw_input("Now enter the coordinates you wish to place the ship at, in the form x,y: ")
                if coords == 'quit':
                        quit
                if coords == '':
                        print welcomeback
                        print '  '
                        menu()
                coordints = coords.split(',')
                inputUrl = 'http://178.62.47.78:1080/game/%s/place_ship/%s/%d/%d/%d/%d/%s'%(str(gamelist[gameid]), str(username), int(shiplength), int(shipdir),int(coordints[1]),int(coordints[0]), str(auth_key))
                try:
                        resp = urllib2.urlopen(inputUrl)
                        resp1 = resp.read()
                        data = json.loads(resp1)
                        if data["status"] == "error":
                                print "Error: " + data["description"]
                                placeship()
                        else:
                                print data
                                print welcomeback
                                menu()
                except IOError as e:
                        print "Error: ", e
                        menu()
        ##given a gameid, returns the metadata about the game
        def checkgame():
                gameid = int(raw_input("Enter the game ID (1, 2, 3, etc.) you wish to check: "))
                gameid -= 1
                if gameid == 'quit':
                        quit
                if gameid == '':
                        print welcomeback
                        print '  '
                        menu()  
                inputUrl = 'http://178.62.47.78:1080/game/%s/%s/%s'%(str(gamelist[gameid]),str(username), str(auth_key)) ## same old URL pointing...
                try:
                        resp = urllib2.urlopen(inputUrl)
                        resp1 = resp.read()
                        data = json.loads(resp1)
                        if data["status"] == "error":
                                print "Error: " + data["description"]
                                checkgame()
                        else:
                                print data
                                print welcomeback
                                menu()   
                except IOError as e:
                        print "Error: ", e
                        menu()

        def activegames():
                inputUrl = 'http://178.62.47.78:1080/player/%s/get_games/%s'%(str(username),str(auth_key))
                try:
                        resp = urllib2.urlopen(inputUrl)
                        resp1 = resp.read()
                        data = json.loads(resp1)
                        if data["status"] == "error":
                                print "Error: " + data["description"]
                                checkgame()
                        else:

                                print "Your active games are:"
                                index1 = 0
                                index2 = 1
                                for activegame in data["active_games"]:
                                        
                                        print str(index2) +': '+ data["active_games"][index1]
                                        index1 += 1
                                        index2 += 1
                                menu()
                except IOError as e:
                        print "Error: ", e
                        menu()

        ##given a gameid, returns who's players turn it is
        def getturn():
                gameid = int(raw_input("Enter the game ID (1, 2, 3, etc.) you wish to check the player turn of: "))
                if gameid == 'quit':
                        quit
                if gameid == '':
                        print welcomeback
                        print '  '
                        menu()
                inputUrl = 'http://178.62.47.78:1080/game/%s/get_turn/%s/%s'%(str(gamelist[gameid]),str(username), str(auth_key))
                try:
                        resp = urllib2.urlopen(inputUrl)
                        resp1 = resp.read()
                        data = json.loads(resp1)
                        if data["status"] == "error":
                                print "Error: " + data["description"]
                                getturn()
                        elif data["status"] == "ok":
                                print "Turn: " + data["turn"]
                                menu()
                except IOError as e:
                        print "Error: ", e
                        menu()


        ## this function returns a grid-ified board
        def getboard():
                gameid = raw_input("Enter the game ID of the board you wish to check: ")
                if gameid == 'quit':
                        quit
                if gameid == '':
                        print welcomeback
                        menu()
                playerid = username
                inputUrl = 'http://178.62.47.78:1080/game/%s/get_board/%s/%s'%(str(gameid),str(playerid),str(auth_key))
                try:
                        resp = urllib2.urlopen(inputUrl)
                        resp1 = resp.read()
                        data = json.loads(resp1)
                        if data["status"] == "error":
                                print "Error: " + data["description"]
                                getboard()
                        else:
                                grid (data["data"][playerid]["visible_board"])
                                print welcomeback
                                menu()
                except IOError as e:
                        print "Error: ", e
                        menu()

        def logout():
                print "You have successfully logged out. Do you wish to log back in? Y/N"
                choice = raw_input()
                if choice == 'N':
                        quit()
                elif choice =='Y':
                        clientlogic()

        def menu():
                
                inputchoice = raw_input()
                if inputchoice == 'checkgame':
                        checkgame()
                        
                elif inputchoice == 'makeshot':
                        makeshot()
                        
                elif inputchoice == 'getturn':
                        getturn()
                        
                elif inputchoice == 'getboard':
                        getboard()
                        
                elif inputchoice == 'newgame':
                        newgame()

                elif inputchoice == 'logout':
                        logout()

                elif inputchoice == 'activegames':
                        activegames()

                elif inputchoice == 'placeship':
                        placeship()
        
                        
                        
                elif inputchoice == '':
                        print welcomeback
                        print "   "
                        menu()

                else:
                        print "Unknown command, please try again."
                        menu()

        viewmenufirsttime()
clientlogic()
