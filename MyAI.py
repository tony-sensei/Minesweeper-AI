# ==============================CS-199==================================
# FILE:			MyAI.py
#
# AUTHOR: 		Justin Chung
#
# DESCRIPTION:	This file contains the MyAI class. You will implement your
#				agent in this file. You will write the 'getAction' function,
#				the constructor, and any additional helper functions.
#
# NOTES: 		- MyAI inherits from the abstract AI class in AI.py.
#
#				- DO NOT MAKE CHANGES TO THIS FILE.
# ==============================CS-199==================================

from AI import AI
from Action import Action
import itertools as it
import copy

class MyAI( AI ):

	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):

		########################################################################
		#							YOUR CODE BEGINS						   #
		########################################################################
		'''
		__stepX, __stepY: storing the current tile coordinate
		__ucTile: number of tiles uncovered
		__totTile: total number of tiles
		__board: a 2d array of -999, for initializing the board
		__safeTile: the tiles which are save to uncover
		__dangerTile: the tiles which need to be marked
		__undecidedTile: the tiles which need to be considered in the future
		__triggerTile: the tiles which have undecided surrounding tiles
		__flagedNum: the number of tiles flaged
		'''
		self.__rowD = rowDimension
		self.__colD = colDimension
		self.__totM = totalMines
		self.__stepX = startX
		self.__stepY = startY
		self.__ucTile = 1
		self.__totTile = rowDimension * colDimension
		self.__board = [[-999 for i in range(self.__rowD)] for j in range(self.__colD)]
		self.__safeTile = set()
		self.__dangerTile = set()
		self.__undecidedTile = set()
		self.__triggerTile = []
		self.__loopIter = 0 #used for guessing, may delete in the future
		self.__flagedNum = 0
		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################

		
	def getAction(self, number: int) -> "Action Object":
		'''
		first move is already happened, the number now is the uncovered tile number
		when marking a tile, set the value be -1
		'''
		########################################################################
		#							YOUR CODE BEGINS						   #
		########################################################################
		if(self.__totTile - self.__ucTile > self.__totM):
			if(self.__board[self.__stepX][self.__stepY] == -999):
				self.__board[self.__stepX][self.__stepY] = number 	  			
			
			self.__separateTiles(
				self.__getSurroundTiles(self.__stepX, self.__stepY), 
				self.__stepX, 
				self.__stepY
			) #update safe, danger, and undecided tile list

			
			#first checking whether have danger tile
			while True:
				while(len(self.__dangerTile) != 0):
					dangerX, dangerY = self.__dangerTile.pop()
					#check if duplicate marked, update board
					if(self.__board[dangerX][dangerY] != -1):
						self.__flagedNum += 1 
						self.__board[dangerX][dangerY] = -1
						if((dangerX, dangerY) in self.__undecidedTile):
							self.__undecidedTile.remove((dangerX, dangerY))
						self.__surroundTriggerDelete(dangerX, dangerY)
						return Action(AI.Action.FLAG, dangerX, dangerY)

				while(len(self.__safeTile) != 0):
					safeX, safeY = self.__safeTile.pop()
					#check if duplicate uncovered, update board
					if(self.__board[safeX][safeY] == -999):
						if((safeX, safeY) in self.__undecidedTile):
							self.__undecidedTile.remove((safeX, safeY))
						self.__stepX, self.__stepY = safeX, safeY
						self.__ucTile += 1
						self.__surroundTriggerDelete(safeX, safeY)
						return Action(AI.Action.UNCOVER, safeX, safeY)


				self.__loopIter = 0
				maxIters = len(self.__triggerTile)
				
				while(self.__triggerTile != [] and self.__flagedNum != self.__totM):
					self.__loopIter += 1
					self.__updateBoard()
					if(len(self.__dangerTile) != 0 or len(self.__safeTile) != 0):
						break
						
					#do the iterations for double checking the availability of rule of thumb, (self.__rowD * self.__colD)**2 times here
					if(self.__loopIter == maxIters):
						# separate distinct lists
						notThatLong = False
						# if(len(self.__undecidedTile) > 15):
						# 	separatedList = self.__separateLists()
						# else:
						# 	separatedList = [list(self.__undecidedTile)]
						# 	notThatLong = True
						separatedList = self.__separateLists()

						updatedSafe = False
						updatedDanger = False
						safetyQueue = []
						safetyDict = dict() # for merging all subsets' safety dict
						for list_Sep in separatedList:
							# if notThatLong:
							# 	proceededList = separatedList
							# else:
							# 	proceededList = self.__evenlySeparate(list_Sep) # evenly separate long lists
							proceededList = self.__evenlySeparate(list_Sep)
							
							updateSafeTile, updateDangerTile, eachSafetyDict = self.__getProbabilityQueue(proceededList)
							
							if(updateSafeTile != []):
								self.__safeTile.update(updateSafeTile)
								updatedSafe = True
							if(updateDangerTile != []):
								self.__dangerTile.update(updateDangerTile)
								updatedDanger = True
							safetyDict.update(eachSafetyDict)
						# sort safety dict and choose the safest one
						if(updatedSafe == False and updatedDanger == False):
							sortedDict = {k: v for k, v in sorted(safetyDict.items(), key=lambda item: item[1])}
							safetyQueue = list(sortedDict.keys())
							if(safetyQueue != []):
								guessTile = safetyQueue.pop(0)
								self.__safeTile.add(guessTile)
						
						# if no clue at all
						if(len(self.__dangerTile) == 0 and len(self.__safeTile) == 0):
							if(self.__flagedNum != self.__totM):
								for i in range(self.__colD):
									for j in range(self.__rowD):
										if(self.__board[i][j] == -999):
											self.__safeTile.add((j, j))

				#after marking all, if still have not uncovered tiles, add all to safetile set
				#or have no clue with empty triggerTile
				if(self.__flagedNum == self.__totM or 
					(len(self.__dangerTile) == 0 and len(self.__safeTile) == 0 and self.__triggerTile == [])):
					for i in range(self.__colD):
						for j in range(self.__rowD):
							if(self.__board[i][j] == -999):
								self.__safeTile.add((i, j))
	

		else:
			return Action(AI.Action.LEAVE)
		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################

	
	#-----------------------#
	#	helper functions	#
	#-----------------------#
	
	def __getSurroundTiles(self, X, Y):
		"Return list of tiles which are surrounded by current coordinate"
		result = []
		if(X == 0 and Y == 0):
			result.append((X+1,Y))
			result.append((X,Y+1))
			result.append((X+1,Y+1))
		elif(X == 0 and Y == self.__rowD-1):
			result.append((X+1,Y))
			result.append((X,Y-1))
			result.append((X+1,Y-1))
		elif(X == 0):
			result.append((X+1,Y))
			result.append((X,Y-1))
			result.append((X+1,Y-1))
			result.append((X,Y+1))
			result.append((X+1,Y+1))
		elif(X == self.__colD-1 and Y == 0):
			result.append((X-1,Y))
			result.append((X,Y+1))
			result.append((X-1,Y+1))
		elif(X == self.__colD-1 and Y == self.__rowD-1):
			result.append((X-1,Y))
			result.append((X,Y-1))
			result.append((X-1,Y-1))
		elif(X == self.__colD-1):
			result.append((X-1,Y))
			result.append((X,Y-1))
			result.append((X-1,Y-1))
			result.append((X,Y+1))
			result.append((X-1,Y+1))
		elif(Y == 0):
			result.append((X+1,Y))
			result.append((X-1,Y))
			result.append((X+1,Y+1))
			result.append((X,Y+1))
			result.append((X-1,Y+1))
		elif(Y == self.__rowD-1):
			result.append((X+1,Y))
			result.append((X-1,Y))
			result.append((X+1,Y-1))
			result.append((X,Y-1))
			result.append((X-1,Y-1))
		else:
			result.append((X+1,Y+1))
			result.append((X,Y+1))
			result.append((X-1,Y+1))
			result.append((X+1,Y))
			result.append((X-1,Y))
			result.append((X+1,Y-1))
			result.append((X,Y-1))
			result.append((X-1,Y-1))
		return result

	def __getNeighbourTiles(self, X, Y):
		"Return list of tiles which are up, down, left, or right by current coordinate"
		result = []
		if(X == 0 and Y == 0):
			result.append((X+1,Y))
			result.append((X,Y+1))
		elif(X == 0 and Y == self.__rowD-1):
			result.append((X+1,Y))
			result.append((X,Y-1))
		elif(X == 0):
			result.append((X+1,Y))
			result.append((X,Y-1))
			result.append((X,Y+1))
		elif(X == self.__colD-1 and Y == 0):
			result.append((X-1,Y))
			result.append((X,Y+1))
		elif(X == self.__colD-1 and Y == self.__rowD-1):
			result.append((X-1,Y))
			result.append((X,Y-1))
		elif(X == self.__colD-1):
			result.append((X-1,Y))
			result.append((X,Y-1))
			result.append((X,Y+1))
		elif(Y == 0):
			result.append((X+1,Y))
			result.append((X-1,Y))
			result.append((X,Y+1))
		elif(Y == self.__rowD-1):
			result.append((X+1,Y))
			result.append((X-1,Y))
			result.append((X,Y-1))
		else:
			result.append((X,Y+1))
			result.append((X+1,Y))
			result.append((X-1,Y))
			result.append((X,Y-1))
		return result
			
	def __separateTiles(self, listOfTiles, X, Y):
		'''
		input getSurroundTiles list, separate tiles into safe, danger and undecided
		'''
		covered = [] # first find all covered tiles
		effectiveLable = self.__board[X][Y]
		while(len(listOfTiles) != 0):
			checkingTile = listOfTiles.pop() #pop from listOfTiles and check
			if(self.__board[checkingTile[0]][checkingTile[1]] == -1):
				effectiveLable -= 1
			if(self.__board[checkingTile[0]][checkingTile[1]] == -999):
				covered.append(checkingTile)
		#separating tiles
		if(effectiveLable == 0):
			self.__safeTile.update(covered)
		elif(effectiveLable == len(covered)):
			self.__dangerTile.update(covered)
		else:
			self.__undecidedTile.update(covered)
			self.__triggerTile.append((X, Y))
		return


	def __updateBoard(self):
		'''
		check all the triggerTile, updating their effectiveLable
		return the new set of undecidedTile
		'''
		checkingTile = self.__triggerTile.pop(0)
		surroundingTile = self.__getSurroundTiles(checkingTile[0], checkingTile[1])
		
		#separateTileAgain, only update if effectiveLabel change
		covered = [] # first find all covered tiles
		effectiveLable = self.__board[checkingTile[0]][checkingTile[1]]
		while(len(surroundingTile) != 0):
			currentTile = surroundingTile.pop() #pop from listOfTiles and check
			if(self.__board[currentTile[0]][currentTile[1]] == -1):
				effectiveLable -= 1
			if(self.__board[currentTile[0]][currentTile[1]] == -999):
				covered.append(currentTile)
		
		#separating tiles
		if(effectiveLable == 0):
			self.__safeTile.update(covered)
		elif(effectiveLable == len(covered)):
			self.__dangerTile.update(covered)
		else:
			self.__undecidedTile.update(covered)
			self.__triggerTile.append(checkingTile)
		return


	def __separateLists(self):
		'''
		separate out the undecidedTiles into separate lists
		NOTICE: __undecidedTile may need to change, remember to check the other
			places which use it
		
		Problem: if the frontier is not linear, it cannot be correctly grouped,
			need to be solved in the future
		'''
		listOfLists = []
		finalResult = []
		pool = set(self.__undecidedTile) #copy undecidedTiles
		eachList = []
		neighbourList = []
		updateFront = False
		updateEnd = False

		while pool != set():
			if(eachList == []):
				target = pool.pop()
				eachList.append(target)
				#find the neighbour of this tile and check whether any of them in the pool
				neighbourList = self.__getNeighbourTiles(target[0], target[1])
				#gather all the neighbours if they appear in undecidedTile into eachSet
				while neighbourList != []:
					neighbour = neighbourList.pop(0)
					if(neighbour in pool):
						pool.remove(neighbour)
						#check whether add on front or end, used for checking in order or 
						#separate in the future						
						if(eachList[-1] == target):
							eachList.append(neighbour)
						else:
							eachList = [neighbour] + eachList
				#check whether need to look forward or backward
				if(eachList[0] != target):
					updateFront = True
				if(eachList[-1] != target):
					updateEnd = True
				if(pool == set()):
					listOfLists.append(eachList)
				
			elif(updateFront):
				target = eachList[0]
				neighbourList = self.__getNeighbourTiles(target[0], target[1])
				#gather all the neighbours if they appear in undecidedTile into eachSet
				while neighbourList != []:
					neighbour = neighbourList.pop(0)
					if(neighbour in pool):
						pool.remove(neighbour)
						eachList = [neighbour] + eachList
				#check whether the front changed
				if(eachList[0] == target):
					updateFront = False
				if(pool == set()):
					listOfLists.append(eachList)
			elif(updateEnd):
				target = eachList[-1]
				neighbourList = self.__getNeighbourTiles(target[0], target[1])
				#gather all the neighbours if they appear in undecidedTile into eachSet
				while neighbourList != []:
					neighbour = neighbourList.pop(0)
					if(neighbour in pool):
						pool.remove(neighbour)
						eachList.append(neighbour)
				#check whether the end changed
				if(eachList[-1] == target):
					updateEnd = False
				if(pool == set()):
					listOfLists.append(eachList)
			else:
				listOfLists.append(eachList)
				eachList = []
		# merge too small lists
		listOfLists.sort(key = len)
		newListForFinal = []
		while(len(listOfLists) != 0):
			curListElem = listOfLists.pop(0)
			if(len(newListForFinal) + len(curListElem) > 10):
				finalResult.append(newListForFinal)
				newListForFinal = curListElem
			else:
				newListForFinal += curListElem
		if newListForFinal != []:
			finalResult.append(newListForFinal)

		return finalResult

	def __evenlySeparate(self, eachList):
		'''
		return:
			a list of the separated list, each length 10
		if the lenth of eachList is less than 10, then keep, if larger, separate as follows:
			if we have a length 16 input list, we should get the separated list of [:10],
		[5:15], [10:16]
		'''
		separatedList = []
		listLength = len(eachList)
		if(listLength > 10):
			no_separated = listLength // 5 if listLength % 5 != 0 else listLength // 5 - 1 
			for i in range(no_separated):
				#normal case
				if(i != no_separated - 1):
					elementList = eachList[i * 5 : i * 5 + 10]
				else:
					elementList = eachList[i * 5 :]
				separatedList.append(elementList)
		else:
			separatedList.append(eachList)
		return separatedList

	
	def __getProbabilityQueue(self, separateList):
		'''
		passing in the sublist of the undecided tiles
		return:
			a list of must safe tiles,
			a list of must danger tiles,
			a dict of tile with their probability to be mine
		
		ideally each group should have at least 1 mine, but this version still cannot
			correctly group all the frontiers, so ignore this time
		'''
		safeTileList = []
		dangerTileList = []		
		#for updating the tiles info for distinct frontiers
		tileSafetyDict = dict()

		#for each segement of subsets
		for eachList in separateList:
			solutions = 0
			lengthList = len(eachList)		
			countList = [0] * lengthList # count the numbers of each tile be mine	
			possibilityList = []

			#generate all possibilities for these tiles, each as 0 for no mine, 1 for mine
			possibilities = list(it.product(range(2), repeat = lengthList))
			
			# the list storing the possibilities which will work
			availablePossibilities = [] # stores tuples
			
			#check each possible whether can work
			for possible in possibilities:
				if(self.__checkAvailiability(eachList, possible) == True):
					availablePossibilities.append(possible)
					#if work, count the mines
					for i in range(lengthList):
						if(possible[i] == 1):
							countList[i] += 1
					solutions += 1 # update solution numbers
			# get the probabilities which each tile to be mine
			if(solutions != 0):
				for count in countList:
					possibilityList.append(count / solutions)
				# get the pairs of tiles which are dependent, and shows the same result in this case
				compareIndep = [] # the list storing all the status by each tile
				for l in range(lengthList):
					compareIndep.append([])# the list storing the possibilities which will work
				for availablePossibility in availablePossibilities:
					for i in range(lengthList):
						compareIndep[i].append(availablePossibility[i])
				depListOfListsS = [] # the list storing all lists of the dependent tiles groups
				depListOfListsD = [] # storing same and diff
				eyesOfPossibility = [1] * len(availablePossibilities) # the list for checking whether two
																	  # tiles are depDiff
				sameIndicatorList = [False] * lengthList
				
				# comparing whether the status in each case are the same, and store the index of the tile
				for i in range(lengthList):
					depListSame = []
					depListDiff = []
					targetChanging = compareIndep[i]
					for j in range(lengthList):
						if(j > i and compareIndep[j] == targetChanging and sameIndicatorList[j] == False):
							depListSame.append(j)
							sameIndicatorList[j] = True
						if(j > i and 
							[sum(tup) for tup in zip(compareIndep[j], targetChanging)] == eyesOfPossibility):
							depListDiff.append(j)
					if depListSame != []:
						depListSame.append(i)
						depListOfListsS.append(depListSame)	
					if depListDiff != []:
						depListDiff.append(i)
						depListOfListsD.append(depListDiff)		
				
				# if two tiles are dep diff, their must be one mine between these two, so add to 50%
				if(depListOfListsD != []):
					for depListDiff in depListOfListsD:
						for eachTile in depListDiff:
							if(possibilityList[eachTile] < 0.5 and possibilityList[eachTile] > 0):
								possibilityList[eachTile] = 0.5
				
				# divide the possibilities of each tile based on whether they have other dependent tiles
				if(depListOfListsS != []):
					for depListSame in depListOfListsS:
						numEachDep = len(depListSame)
						for eachTile in depListSame:
							if(possibilityList[eachTile] != 100 and possibilityList[eachTile] != 0):
								possibilityList[eachTile] = possibilityList[eachTile] / numEachDep

				# update tileSafetyDict, with index: the tiles coordinates, value: the probability
				# if the tile appeared in the Dict before, get average
				for index, tile in enumerate(eachList):
					if(tile in tileSafetyDict.keys()):
						tileSafetyDict[tile] = (tileSafetyDict[tile] + possibilityList[index]) / 2
					else:
						tileSafetyDict[tile] = possibilityList[index]

		
		#generate the three lists
		for key in tileSafetyDict:
			if(tileSafetyDict[key] == 0):
				safeTileList.append(key)
			elif(tileSafetyDict[key] == 1):
				dangerTileList.append(key)
		for tile in safeTileList:
			del tileSafetyDict[tile]
		for tile in dangerTileList:
			del tileSafetyDict[tile]
		
		# if the result is from segement, we dont trust the danger, and only try one safe
		if(len(separateList) != 1):
			dangerTileList = []
			if safeTileList != []:
				safeTileList = [safeTileList[0]]
		return safeTileList, dangerTileList, tileSafetyDict


	def __checkAvailiability(self, targetList, status):
		'''
		checking whether the tiles in targetList can work in status
		input:
			targetList: segaments of subsets
			status: tuple of status(0 or 1, which is not mine or mine)
		output:
			boolean
		'''
		testingBoard = copy.deepcopy(self.__board) # copy the board
		currentMines = self.__flagedNum # make sure the mines are not exceed the total
		#check whether exceed mine limit
		mineInStatus = 0
		for i in status:
			if(i == 1):
				mineInStatus += 1
		if(mineInStatus + currentMines > self.__totM):
			return False
		else:
			surroundingTiles = [] # the pool of tiles which surrounded by the targetTiles
			checkingTiles = set() # the pool of the surroundingTiles which can be indicator
			# get all the surrounding tiles
			for target in targetList:
				surroundingTiles.extend(self.__getNeighbourTiles(target[0], target[1]))
			# filter out all other tiles except indicators
			for tile in surroundingTiles:
				if(testingBoard[tile[0]][tile[1]] >= 0):
					checkingTiles.add(tile)
			# update the testingBoard
			for index, tile in enumerate(targetList):
				if(status[index] == 1):
					testingBoard[tile[0]][tile[1]] = -1
				if(status[index] == 0):
					testingBoard[tile[0]][tile[1]] = 100

			# check the checkingTiles
			for tile in checkingTiles:
				surrounCheckingTile = self.__getSurroundTiles(tile[0], tile[1])
				effectiveLable = testingBoard[tile[0]][tile[1]]
				rangeOfMinesSurround = 0 # if the tile is the front or end, it may still have covered surrounding tiles
				while(len(surrounCheckingTile) != 0):
					currentTile = surrounCheckingTile.pop() 
					if(testingBoard[currentTile[0]][currentTile[1]] == -1):
						effectiveLable -= 1
					if(testingBoard[currentTile[0]][currentTile[1]] == -999):
						rangeOfMinesSurround += 1
				if(effectiveLable < 0 or effectiveLable > rangeOfMinesSurround):  # if out of range
					return False
			return True
	

	def __surroundTriggerDelete(self, X, Y):
		'''
		detect whether the surrounding tiles in trigger, and whether they have 0
		effective label, if so, remove
		input:
			X, Y: the coordinates of the tile
		'''
		surroundingTile = self.__getSurroundTiles(X, Y)
		while(len(surroundingTile) != 0):
			currentTile = surroundingTile.pop()
			if currentTile in self.__triggerTile:
				surroundingTrigger = self.__getSurroundTiles(currentTile[0], currentTile[1])
				covered = []
				effectiveLable = self.__board[currentTile[0]][currentTile[1]]
				while(len(surroundingTrigger) != 0):
					currentTrigger = surroundingTrigger.pop()
					if(self.__board[currentTrigger[0]][currentTrigger[1]] == -1):
						effectiveLable -= 1
					if(self.__board[currentTrigger[0]][currentTrigger[1]] == -999):
						covered.append(currentTrigger)
				if(effectiveLable == 0):
					self.__safeTile.update(covered)
					self.__triggerTile.remove(currentTile)
		
		return
				