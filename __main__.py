from game import i2c

import gevent
from gevent.wsgi import WSGIServer
from threading import Thread
from game.game import Game
go = Game("piet","pol","normal","subtile")
gameRunning = False
import webBack
import MySQLdb

import time

def startServer():
	server = WSGIServer(("", 5000), webBack.app)
	server.serve_forever()

def whiletrue():
	while(True):
		try:
			i2c.setinputs()
			#print(i2c.sensor1)
			#print(i2c.readSensor(1))
			time.sleep(0.25)
		except:
			print("ERROR READING")
			time.sleep(0.25)

if __name__ == "__main__":
	
	print("start Game")
	go = Game("jan","jaap","normal","subtile")
	#go.startGame()
	print("game running")

	db = MySQLdb.connect("localhost","root","root","MindGame" )
	dbc = db.cursor()
	sql = "DELETE FROM Game;"
	print(sql)
	dbc.execute(sql)
	db.commit()

	print("start server")
	thread = Thread(target = startServer, args = ())
	thread.start()
	whiletruethread = Thread(target = whiletrue, args = ())
	whiletruethread.start()
	print("server running")


		