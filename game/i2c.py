from __future__ import division
import smbus
import time
from neopixel import *
global sensor1
global sensor2
global holes1
global holes2
sensor1 = 128
sensor2 = 128
holes1 = 0
holes2 = 0
bus = smbus.SMBus(1)
address = 0x04

global teller1
teller1 = 2
global teller2
teller2 = 2

global p1active
global p1passive
global p2active
global p2passive

p1active = Color(255,0,0)
p1passive = Color(0,0,0)
p2active = Color(255,0,0)
p2passive = Color(0,0,0)

# LED strip configuration:
LED_COUNT      = 82      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
# Intialize the library (must be called once before other functions).
strip.begin()


global averagecounter
global sensor1Average
global sensor2Average
averagecounter = 0
sensor1Average = 0
sensor2Average = 0

def setinputs():
    result = [0,128,1,128,2,0,3,0]#bus.read_i2c_block_data(address,0,8)
    if(result[0] == 0 and result[2] == 1 and result[4] == 2 and result[6] == 3):
        global sensor1
        global sensor2
        global holes1
        global holes2
        sensor1 = result[1]
        sensor2 = result[3]
        holes1 = result[5]
        holes2 = result[7]
        #Calculating average
        global averagecounter
        global sensor1Average
        global sensor2Average
        sensor1Average = (sensor1Average*(averagecounter/(averagecounter+1))) + (sensor1 * (1/(averagecounter+1)))
        sensor2Average = (sensor2Average*(averagecounter/(averagecounter+1))) + (sensor2 * (1/(averagecounter+1)))
        averagecounter +=1
        #print("sensor1: %d sensor1 average: %d" %(sensor1, sensor1Average))

        #print("setinput: %d" %(sensor1))
        #print("getballs: %d" %(holes1))

def resetAverage():
    global averagecounter
    averagecounter = 0

def getAverage(sensor):
    global sensor1Average
    global sensor2Average
    if(sensor == 1):
        return sensor1Average
    elif(sensor == 2):
        return sensor2Average
        
def readSensor(person):
    global sensor1
    global sensor2
    #print("sensor read: %d" %(sensor1))
    if (person == 1):
        return sensor1
    elif (person == 2):
        return sensor2

def readballs(person):
    #print("balls reading: %d" %(holes1))
    global holes1
    global holes2
    setinputs()
    if (person == 1):
    #    global teller1
    #    teller1 = teller1 +1
    #    if(teller1%10 == 0):
    #        return 16
    #    else:
    #        return 0
        return holes1
    elif (person == 2):
    #    global teller2
    #    teller2 = teller2 +1
    #    if(teller2%10 == 0):
    #        return 4
    #    else:
    #        return 0
        return holes2

def setLedStripTime(person,percentage):
    global p1active
    global p1passive
    global p2active
    global p2passive
    if(person == 2):
        for i in range(int(strip.numPixels()*percentage/200)):
            strip.setPixelColor(i, p1active)
        for i in range(int(strip.numPixels()*percentage/200),int(strip.numPixels()/2)):
            strip.setPixelColor(i, p1passive)
    else:
        for i in range(int(strip.numPixels()/2), int(strip.numPixels()*percentage/200 + strip.numPixels()/2)):
            strip.setPixelColor(i, p2active)
        for i in range(int(strip.numPixels()*percentage/200 + strip.numPixels()/2),int(strip.numPixels())):
            strip.setPixelColor(i, p2passive)
    strip.show()

def setActiveTimeColor(person, R,G,B):
    global p1active
    global p2active
    if(person == 1):
        p1active = Color(G,R,B)
    else:
        p2active = Color(G,R,B)

def setPassiveTimeColor(person, R,G,B):
    global p1passive
    global p2passive
    if(person == 1):
        p1passive = Color(G,R,B)
    else:
        p2passive = Color(G,R,B)

def getActiveTimeColor(person):
    global p1active
    global p2active
    if(person == 1):
        return p1active
    else:
        return p2active

def getPassiveTimeColor(person):
    global p1passive
    global p2passive
    if(person == 1):
        return p1passive
    else:
        return p2passive
    
def setBallsLeds(person,hole,R,B):
    if (person == 1):
        bus.write_i2c_block_data(address,22,[hole, R,B])
        #print("setBallsPerson1")
    elif (person == 2):
        bus.write_i2c_block_data(address,38,[hole, R,B])
        #print("setBallsPerson2")

def setHeadsetColor(person,R,G,B):
    bus.write_i2c_block_data(address,53 + person,[R,G,B])
    #print("setHeadsetColor")
            
def initialize():
    bus.write_i2c_block_data(address,60,[255,0,255])
    #print("initialize")

def startgame():
    bus.write_i2c_block_data(address,61,[255,0,255])
    #print("startgame")