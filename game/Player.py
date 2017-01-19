from __future__ import division
from threading import Thread

import time
import i2c
import MySQLdb
from game import Game
from neopixel import *


class player(object):

	def __init__(self, gameobj, GameMode, LightMode, Name, pin):
		self.Name = Name
		print("GameMode: %s" %(GameMode))
		if(GameMode == "easy"):
			self.time = 20
		elif(GameMode == "normal"):
			self.time = 15
		elif(GameMode == "hard"):
			self.time = 10
		else:
			self.time = 30
		self.maxTime = self.time
		self.GameMode = GameMode
		self.LightMode = LightMode
		self.pin = pin
		self.stress = 0
		self.balls = 0
		self.points = 0
		self.timethread = Thread(target = self.timeLooping, args = ())
		self.updatethread = Thread(target = self.updateLooping, args = ())
		self.updateloop = True
		self.holescores = [0,0,0,0,0,0,0,0]
		self.brilkleur = [0,0,0]
		self.blinkBril = False
		self.blinkOn = False
		self.game = gameobj

	def startTime(self):
		
		gelukt = False
		while (gelukt == False):
			try:
				self.setBrilColor(255,0,0)
				i2c.setBallsLeds(self.pin, self.balls,255,0)
				gelukt = True
				
			except:
				print("ERROR START LEDS")
				gelukt = False

			self.timethread.start()
			self.updatethread.start()

	def timeLooping(self):
		for i in range(self.time):
			self.time = self.time -1
			print("time running: %d" %(self.time))
			averageSensor = i2c.getAverage(self.pin)
			self.writeToSql("INSERT  INTO Hartstats (BPM, R, G, B) VALUES ('"+ str(averageSensor)+"', '"+str(self.brilkleur[0])+"', '"+str(self.brilkleur[1])+"', '"+str(self.brilkleur[2])+"')")

			#waitTime=0
			try:
				#waitTime = i2c.readSensor(self.pin)
				self.stress = averageSensor / 2.55
				time.sleep(2-((self.stress+50)/100))
				self.setBrilColor(0,255,0)
			except:
				print("ERROR READING SENSOR")
			if(averageSensor<65):
				self.setBrilColor(0,0,255)
				self.blinkBril = False
			elif(averageSensor<75):
				self.setBrilColor(0,255,0)
				self.blinkBril = False
			elif(self.LightMode == "extreme"):
				self.setBrilColor(255,0,0)
				self.blinkBril = True
			else:
				self.setBrilColor(255,0,0)
				self.blinkBril = False

			i2c.resetAverage()
			#time.sleep(1)
		print("Player %s is dead" %(self.Name))
		self.updateloop = False
		self.endGame()
		
		


	def updateLooping(self):
		previousReading = 0
		while self.updateloop:
			try:
				self.balls = i2c.readballs(self.pin)
				if((self.balls != previousReading)): 
					#print("NOT SAME")
					i2c.setBallsLeds(self.pin, self.balls,0,255)
					#time.sleep(0.05)
					i2c.setBallsLeds(self.pin, (255-self.balls),255,0)
					if(self.balls > 0):
						for j in range(8):
							if((self.balls >> j)%2):#puntentelling
								self.points+=(j+1)
								self.holescores[j] +=1 
				
			except:
				print("ERROR READING BALLS")

			previousReading = self.balls
			timeStrip = ((self.time/self.maxTime)*100)
			intTimeStrip = int (timeStrip)
			#print(intTimeStrip)
			try:
				if (intTimeStrip < 20 and self.LightMode == "extreme"):
					if (i2c.getPassiveTimeColor(self.pin) != Color(0,0,0)):
						i2c.setPassiveTimeColor(self.pin,0,0,0)
						#self.setAllBallsLeds(0,0)
						i2c.setBallsLeds(self.pin,255-self.balls,0,0)

					else:
						i2c.setPassiveTimeColor(self.pin,255,0,0)
						#self.setAllBallsLeds(255,0)
						i2c.setBallsLeds(self.pin,255-self.balls,255,0)
				elif(intTimeStrip<20):
					i2c.setPassiveTimeColor(self.pin,255,0,0)
				i2c.setLedStripTime(self.pin,intTimeStrip)
			except:
				print("ERROR SET BALLS LEDS")
			try:
				if(self.blinkBril and self.blinkOn):
					i2c.setHeadsetColor(self.pin,0,0,0)
				elif(self.blinkBril):
					i2c.setHeadsetColor(self.pin,self.brilkleur[0],self.brilkleur[1],self.brilkleur[2])
			except:
				print("ERROR BlINK HEADSET")

			for i in range(10):
				if(self.updateloop):
					time.sleep(0.03)



	def endGame(self):
		#HIGHSCORE TABLE UPDATE
		self.writeToSql("INSERT INTO Highscore (Name, Score, GameMode, LightMode) VALUES ('" + self.Name + "', '"+ str(self.points) + "', '"+ str(self.GameMode) + "', '"+ str(self.LightMode)  + "');")
		#HOLESTAT TABLE UPDATE
		self.writeToSql("INSERT INTO Holestats (Hole1, Hole2, Hole3, Hole4, Hole5, Hole6, Hole7, Hole8, GameMode, LightMode, Player) VALUES ('" + str(self.holescores[0]) + "', '" + str(self.holescores[1]) + "', '" + str(self.holescores[2]) + "', '" + str(self.holescores[3]) + "', '" + str(self.holescores[4]) + "', '" + str(self.holescores[5]) + "', '" + str(self.holescores[6]) + "', '" + str(self.holescores[7]) + "', '"+ str(self.GameMode) + "', '"+ str(self.LightMode) + "', '"+ str(self.Name) + "');")

		time.sleep(0.1)
		i2c.setPassiveTimeColor(self.pin,255,0,0)
		i2c.setLedStripTime(self.pin,0)
		self.setAllBallsLeds(255,0)
		self.game.endGame(self.pin)




	def writeToSql(self, sql):
		db = MySQLdb.connect("localhost","root","root","MindGame" )
		dbc = db.cursor()
		dbc.execute(sql)
		db.commit()

		

	def setAllBallsLeds(self,R,G):
		try:
			i2c.setBallsLeds(self.pin,255,R,G)
		except:
			print("ERROR SETTING LEDS")



	def setBalls(self, pos):
		self.balls = self.balls & 1<<pos



	def setBrilColor(self,R,G,B):
		self.brilkleur = [R,G,B]
		try:
			i2c.setHeadsetColor(self.pin,R,G,B)
		except:
			print("ERROR SET HEADSET COLOR")



	def getBalls(self):
		balArray = [False,False,False,False,False,False,False,False]
		for i in range(0,7):
			if(self.balls & 1<<i):
				ballArray[i] = True
		return ballArray



	def getName(self):
		return self.Name