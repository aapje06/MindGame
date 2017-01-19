import gevent
from gevent.wsgi import WSGIServer
from gevent.queue import Queue
import time
from flask import Flask, Response, send_from_directory, request
import os.path
import MySQLdb
from game.game import Game
import __main__
from threading import Thread

noFurtherRequests = True

# SSE "protocol" is described here: http://mzl.la/UPFyxY
class ServerSentEvent(object):

    def __init__(self, id, event, data, retry):
        self.data = data
        self.event = event
        self.id = id
        self.retry = retry
        self.desc_map = {
        	self.retry : "retry",
        	self.id : "id",
        	self.event : "event",
            self.data : "data"
        }

    def encode(self):
        if not self.data:
            return ""
        lines = ["%s: %s" % (v, k) 
                 for k, v in self.desc_map.iteritems() if k]
        
        return "%s\n\n" % "\n".join(lines)

app = Flask(__name__, static_url_path='', static_path='',static_folder='')
#app.debug = True
app.debug = False
app.use_reloader=False
app.threaded = True

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)

@app.route('/inGame/pics/<path:path>')
def send_pics(path):
    return send_from_directory('pics', path)

@app.route('/stats/pics/<path:path>')
def send_pics_stats(path):
    return send_from_directory('pics', path)

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@app.route('/fonts/<path:path>')
def send_fonts(path):
    return send_from_directory('fonts', path)

# Client code consumes like this.
@app.route("/")
def index():
    return app.send_static_file('index.html')


@app.route("/inGame/<path:path>")
def inGame(path):
    global noFurtherRequests
    noFurtherRequests = False
    #print("inGame Request")
    return app.send_static_file('inGame.html')

@app.route("/stats/")
def stats():
   return app.send_static_file('stats.html')


@app.route("/startInfo")
def startInfo():
    def gen():
            db = MySQLdb.connect("localhost","root","root","MindGame" )
            dbc = db.cursor()
    		#update highscore section
            sql = "SELECT Name, Score FROM Highscore order by Score desc limit 5"
            dbc.execute(sql)
            results = dbc.fetchall()
            result = '{"highscore": ['
            for row in results:
                result += '{"Name": "%s", "Score": "%s"},' % (row[0], row[1])

            if (not result.endswith("[")):
                result = result[:-1]
            result +=']}'

            sendResult = ServerSentEvent(1,"highscore", str(result), "1000")
            yield sendResult.encode()

            #update Game section
            sql = "SELECT Gamename FROM Game limit 5"
            dbc.execute(sql)
            results = dbc.fetchall()
            result = '{"Games": ['
            boolrunning = __main__.go.p1.time > 0 and __main__.go.p2.time > 0
            for row in results:
            	result += '{"Gamename": "%s", "Running": "%s"},' % (row[0], str(boolrunning))

            if (not result.endswith("[")):
                result = result[:-1]
            result +=']}'

            sendResult = ServerSentEvent(1,"Game", str(result), "1000")
            yield sendResult.encode()
            #print "info send"
    return Response(gen(), mimetype="text/event-stream")

@app.route("/inGameInfo/<path:path>")
def gameInfo(path):
    def gen(game):
        __main__.gameRunning = True
        global noFurtherRequests
        noFurtherRequests = False
        #playerinfo
        result = '{"players":[{"name": "' + __main__.go.getPlayer1Name() 
        result += '", "time":' + str(__main__.go.p1.time) +', "maxTime": '+ str(__main__.go.p1.maxTime) +', "stress": '+ str(__main__.go.p1.stress) 
        result += ', "balls": ' + str(__main__.go.p1.balls)
        result += ', "points": ' + str(__main__.go.p1.points) + '},'
        result += '{"name": "' + __main__.go.getPlayer2Name()
        result += '", "time":' + str(__main__.go.p2.time) +', "maxTime": '+ str(__main__.go.p2.maxTime)+ ', "stress": '+ str(__main__.go.p2.stress)
        result += ', "balls": ' + str(__main__.go.p2.balls)
        result += ', "points": ' + str(__main__.go.p2.points) + '}]}'
        result = ServerSentEvent(1,"playerInfo", str(result), "300")
        yield result.encode()

        #countdown
        result = __main__.go.countdown
        sendResult = ServerSentEvent(1,"countdown", str(result), "300")
        yield sendResult.encode()

        #debugging
        result = '{"debugging":[{"line": "' + __main__.go.getPlayer1Name() + ' time '+ str(__main__.go.p1.time) +' maxTime ' + str(__main__.go.p1.maxTime) + ' Points ' + str(__main__.go.p1.points) + '"}]}'
        result = ServerSentEvent(1,"debug", str(result), "300")
        yield result.encode()
    return Response(gen(path), mimetype="text/event-stream")


@app.route("/stopGame", methods=['POST'])
def debug():
    def stopwait(gamename):
        print("stopGame called")
        time.sleep(2)
        noFurtherRequests = True
        time.sleep(2)
        global noFurtherRequests
        if (noFurtherRequests and not __main__.go.p1.time > 0 and not __main__.go.p2.time > 0):
            #print( __main__.go.p1.time)
            db = MySQLdb.connect("localhost","root","root","MindGame" )
            dbc = db.cursor()
            sql = "DELETE FROM Game WHERE Gamename = '" + gamename + "';"
            print(sql)
            dbc.execute(sql)
            db.commit()
            __main__.gameRunning = False
        else:
            noFurtherRequests = True
            print("not stopping the game")

    #def printReq():
    #    while True:
    #        global noFurtherRequests
    #        print("request: %s" %(noFurtherRequests))
    #        time.sleep(1)

    #printreqThread = Thread(target = printReq, args = ())
    #if(not printreqThread.isAlive()):
    #    printreqThread.start()
    stopWaitThread = Thread(target = stopwait, args = (str(request.form['gn']),))
    if(not stopWaitThread.isAlive()):
        stopWaitThread.start()
    return "ok"

@app.route("/startGame", methods=['POST'])
def startgame():
    if request.method == 'POST':
        #print("login!")
        #print(request.form)
        db = MySQLdb.connect("localhost","root","root","MindGame" )
        dbc = db.cursor()
        sql = "SELECT Gamename FROM Game where Gamename = '" + request.form['gn'] + "';"
        dbc.execute(sql)
        if (not dbc.fetchall() and __main__.gameRunning == False):
            sql = "INSERT INTO Game (Gamename, P1Name, P2Name, passwd, gameMode, lightMode) VALUES ('" + request.form['gn'] + "', '" + request.form['p1n'] + "', '"+ request.form['p2n'] + "', '"+ request.form['pw'] + "', '"+ request.form['gm'] + "', '"+ request.form['lm'] + "');"
            #print(sql)
            dbc.execute(sql)
            db.commit()
            __main__.gameRunning = True
            db = MySQLdb.connect("localhost","root","root","MindGame" )
            dbc = db.cursor()
            sql = "SELECT P1Name, P2Name, gameMode, lightMode FROM Game where Gamename = '" + request.form['gn'] + "'"
            #print(sql)
            dbc.execute(sql)
            results = dbc.fetchall()
            #print(results)
            for row in results:
                p1 = row[0]
                p2 = row[1]
                #if(row[2] == "easy"):
                #    startTime = 160
                #elif(row[2]=="normal"):
                #    startTime = 120
                #elif(row[2]=="hard"):
                #    startTime = 90
            __main__.go = Game(p1,p2,row[2],row[3])
            __main__.go.startGame()
            return "ok"
        elif (__main__.gameRunning == True):
            print("gameRunning...")
            return "gameRunning"
        else:
            print("nameExist...")
            return "nameExist"


@app.route("/statInfo")
def statinfo():
    def gen():
        #print("statInfo called")
        #HOLESTAT INFO
        db = MySQLdb.connect("localhost","root","root","MindGame" )
        dbc = db.cursor()
        sql = "SELECT sum(Hole1), sum(Hole2), sum(Hole3), sum(Hole4), sum(Hole5), sum(Hole6), sum(Hole7), sum(Hole8) FROM MindGame.Holestats;"
        dbc.execute(sql)
        results = dbc.fetchall()
        for row in results:
            result = '{"Holes":[{'
            for i in range(8):
                result += '"hole'+str(i+1)+'": "' + str(row[i]) + '", '
            result = result[:-2]
            result+='}]}'
        sendResult = ServerSentEvent(1,"holeStat", str(result), "15000")
        yield sendResult.encode()

        #POINTS INFO
        sql = 'Select(SELECT round(avg(Score),2) FROM MindGame.Highscore where GameMode = "easy" and LightMode = "subtile") as easy_subtile,(SELECT round(avg(Score),2) FROM MindGame.Highscore where GameMode = "normal"  and LightMode = "subtile") as normal_subtile,(SELECT round(avg(Score),2) FROM MindGame.Highscore where GameMode = "hard"  and LightMode = "subtile") as hard_subtile,(SELECT round(avg(Score),2) FROM MindGame.Highscore where GameMode = "easy" and LightMode = "extreme") as easy_extreme,(SELECT round(avg(Score),2) FROM MindGame.Highscore where GameMode = "normal"  and LightMode = "extreme") as normal_extreme,(SELECT round(avg(Score),2) FROM MindGame.Highscore where GameMode = "hard"  and LightMode = "extreme") as hard_extreme from MindGame.Highscore limit 1;'
        dbc.execute(sql)
        results = dbc.fetchall()
        result = ""
        for row in results:
            result = '{"averages":[{'
            result += '"easy_subtile": "' + str(row[0]) + '", '
            result += '"normal_subtile": "' + str(row[1]) + '", '
            result += '"hard_subtile": "' + str(row[2]) + '", '
            result += '"easy_extreme": "' + str(row[3]) + '", '
            result += '"normal_extreme": "' + str(row[4]) + '", '
            result += '"hard_extreme": "' + str(row[5]) + '"}]}'
        sendResult = ServerSentEvent(1,"pointsStat", str(result), "15000")
        yield sendResult.encode()

        #HART INFO
        sql = 'select(select round(avg(BPM),2) from MindGame.Hartstats where R = 255 and G = 0 and B = 0) as red,(select round(avg(BPM),2) from MindGame.Hartstats where R = 0 and G = 255 and B = 0) as green,(select round(avg(BPM),2) from MindGame.Hartstats where R = 0 and G = 0 and B = 255) as blue from MindGame.Hartstats limit 1;'
        dbc.execute(sql)
        results = dbc.fetchall()
        result = ""
        for row in results:
            result = '{"Hart":[{'
            result += '"Red": "' + str(row[0]) + '", '
            result += '"Green": "' + str(row[1]) + '", '
            result += '"Blue": "' + str(row[2]) + '"}]}'
        sendResult = ServerSentEvent(1,"hartsStat", str(result), "15000")
        yield sendResult.encode()


    return Response(gen(), mimetype="text/event-stream")