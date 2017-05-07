##Both functions would be placed at line 74 in client.py right underneath def grid(arr)
##Line 158 would be placed within the placeship function in client.py and would run if the game was vs an ai
##Line 162 would be placed within the makeshot function in client.py and again would run if the game was vs an ai

#Should be stored in database
#overall_gameid = range(1, 101)
#checkerboard_gameid = []
#for number in range(10, 110, 10):
#	if (number/10) % 2 == 0:
#		even = range(number-8, number + 2, 2)
#		checkerboard_gameid.extend(even)
#	else:
#		odd = range(number-9, number +1, 2)
#		checkerboard_gameid.extend(odd)
#firstHit_gameid = [0, []]
#aimed_gameid = False
		
#def aiShot(overall, checkerboard, firstHit, aimed, gameid):
#Should be
def aiShot():
	def aiLogin():
		inputUrl = 'http://178.62.47.78:1080/player/login/%s/%s'%(str("Ai"), str("qwerty"))
		resp = urllib2.urlopen(inputUrl)
		resp1 = resp.read()
		data = json.loads(resp1)
		return data["key"]
	auth_key = aiLogin()
	# example of how it would request overall, checkerboard, firstHit, aimed from the server
	# inputUrl = 'http://178.62.47.78:1080/ai/variables/%s'%(str(auth_key)) (or however you want the http request to be)
	# resp = urllib2.urlopen(inputUrl)
	# resp1 = resp.read()
	# data = json.loads(resp1)
	# overall = data["overall"]
	# checkerboard = data["checkerboard"]
	# firstHit = data["firstHit"]
	# aimed = data["aimed"]
	
	def shotsRemaining(hit):
		i = 0
		for elem in hit:
			i+=1
		return i
	
	def convert(i):
		if i < 11:
			x = i-1
			y = 0
		elif i % 10 == 0:
			x = 9
			y = (i/10)-1
		else:
			y = int(math.floor(i/10))
			x = int(i-(10*y)-1)
		return (x,y)
	
	def normalShot(overall, checkerboard, aimed):
		location = random.choice(checkerboard)
		if location in overall:
			overall.remove(location)
		checkerboard.remove(location)
		x, y = convert(location)
		aimed = False
		return (x, y, location, aimed)
	
	def aimedShot(firstHit, overall, aimed):
		direction = random.choice(firstHit[1])
		firstHit[1].remove(direction)
		if (firstHit[0] + direction) in overall:
			x, y = convert(firstHit[0]+direction)
			overall.remove(firstHit[0]+direction)
			aimed = True
			return (x, y, firstHit[0]+direction, aimed)
		elif shotsRemaining(firstHit[1]) > 0:
			return aimedShot(firstHit, overall, aimed)
		else:
			return normalShot(overall, checkerboard, aimed)
	
	location = 0
	if shotsRemaining(firstHit[1]) > 0:
		x, y, location, aimed = aimedShot(firstHit, overall, aimed)
	else:
		x, y, location, aimed = normalShot(overall, checkerboard, aimed)
	
	inputUrl = 'http://178.62.47.78:1080/game/%d/make_shot/%s/%d/%d/%s'%(int(gameid),str("Ai"),int(y),int(x),str(auth_key))
	resp = urllib2.urlopen(inputUrl)
	resp1 = resp.read()
	data = json.loads(resp1)
	value = data["hit"]
	
	if value == "Hit" and aimed == False:
		if location == 1:
			firstHit = [location, [1, 10]]
		elif location == 100:
			firstHit = [location, [-1,-10]]
		elif location % 10 == 0:
			firstHit = [location, [-1,10,-10]]
		elif (location-1)%10 == 0:
			firstHit = [location, [1,10,-10]]
		elif location < 11:
			firstHit = [location, [1,-1,10]]
		elif location >90:
			firstHit = [location, [1,-1,-10]]
		else:
			firstHit = [location, [1,-1,10,-10]]
	# example of how it would update overall, checkerboard, firstHit, aimed on the server
	# inputUrl = 'http://178.62.47.78:1080/ai/update/%s/%s/%s/%s%s'%(str(overall),str(checkerboard),str(firstHit),str(aimed),str(auth_key)) (or however you want the http request to be)
	
def placeshipAi():
	def aiLogin():
		inputUrl = 'http://178.62.47.78:1080/player/login/%s/%s'%(str("Ai"), str("qwerty"))
		resp = urllib2.urlopen(inputUrl)
		resp1 = resp.read()
		data = json.loads(resp1)
		return data["key"]
	auth_key = aiLogin()
	positions = range(1, 101)
	ship = [5,4,3,3,2]
	shiplength = []
	shipdir = []
	
	def convert(i):
		if i < 11:
			x = i-1
			y = 0
		elif i % 10 == 0:
			x = 9
			y = (i/10)-1
		else:
			y = int(math.floor(i/10))
			x = int(i-(10*y)-1)
		return (x,y)
	
	def shipSelection(positions, ship, shiplength, shipdir):
		shipdirection = [-1, 1]
		shipdir = random.choice(shipdirection)
		shipdirection.remove(shipdir)
		shiplength = random.choice(ship)
		position = random.choice(positions)
		def test(position, shipdir, shiplength, positions):
			for i in range(1,shiplength+1):
				if (position+(shipdir*i)) not in positions:
					return False
			for i in range(1,shiplength+1):
				positions.remove(position+(shipdir*i))
			return True	
		if test(position, shipdir, shiplength, positions) == True:
			if shipdir == 1:
				shipdir = 0
			ship.remove(shiplength)
			x, y = convert(position)
			return (x, y, shiplength, shipdir)
		else:
			return shipSelection(positions, ship, shiplength, shipdir)
	
	for i in range(0, 5):
		x, y, shiplength, shipdir = shipSelection(positions, ship, shiplength, shipdir)
		inputUrl = 'http://178.62.47.78:1080/game/%s/place_ship/%s/%d/%d/%d/%d/%s'%(str(gamelist[gameid]), str("Ai"), int(shiplength), int(shipdir),int(x),int(y), str(auth_key))
		resp = urllib2.urlopen(inputUrl)
#placeshipAi()
#overall_gameid, checkerboard_gameid, firstHit_gameid, aimed_gameid  = aiShot(overall_gameid, checkerboard_gameid, firstHit_gameid, aimed_gameid, gameid)
#Should just be
#aiShot()
