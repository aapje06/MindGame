from Player import player
from threading import Thread
import time
import i2c

class Game:
	def __init__(self,player1,player2, GameMode, lightMode):
		self.player1 = player1
		self.player2 = player2
		self.GameMode = GameMode
		self.lightMode = lightMode
		self.countdown = 3
		self.p1 = player(self.GameMode, self.lightMode, self.player1, 1)
		self.p2 = player(self.GameMode, self.lightMode, self.player2, 2)
		print("game made")

	def startGame(self):
		def start():
			print("game starting")
			self.p1.time = self.p1.maxTime
			self.p2.time = self.p2.maxTime

			i2c.setPassiveTimeColor(1,0,0,0)
			i2c.setPassiveTimeColor(2,0,0,0)
			i2c.setLedStripTime(1,0)
			i2c.setLedStripTime(2,0)
			print("ledstrip set")
			i2c.initialize()
			while (self.countdown>0):
				print("countdown: %d" %(self.countdown))
				time.sleep(1)
				self.countdown -=1
			i2c.startgame()
			self.p1.startTime()
			self.p2.startTime()

		startThread = Thread(target = start, args = ())
		startThread.start()

	def getPlayer1Name(self):
		return self.p1.getName()

	def getPlayer2Name(self):
		return self.p2.getName()
