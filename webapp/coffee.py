import RPi.GPIO as GPIO
import os
import time
import glob

chan_out = [19,12,22]
chan_in = [11,20,13,15]
out_relay = 19
out_relay = chan_out[0] #turnCoffeeMakerUp
out_speaker = chan_out[2]
in_notWet =  chan_in[2] #hazardInducingSensor
in_howWet = chan_in[0] #ultra
out_howWetTrig = chan_out[1] #ultra
deviceDir  = glob.glob('/sys/bus/w1/devices/28*')  
deviceFile = [deviceDir[0] + '/w1_slave', deviceDir[1] + '/w1_slave']

def coffeeOn():
    GPIO.output(out_relay,GPIO.HIGH)

def coffeeOff():
    GPIO.output(out_relay,GPIO.LOW)

def speakOn():
    GPIO.output(out_speaker,GPIO.HIGH)

def speakOff():
    GPIO.output(out_speaker,GPIO.LOW)

def noise():
    for i in range(5000):
        speakOn()
        timer.sleep(.0001)
        speakOff()
        timer.sleep(.0001)
def setupPin():
    os.system("modprobe w1-gpio")
    os.system("modprobe w1-therm")
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    print("out~~~~")
    for i in range(len(chan_out)):
        GPIO.setup(chan_out[i],GPIO.OUT)    
        print(str(chan_out[i])+", ")
    print("~~~~~~~~~~~\nIn~~~~~~~~")
    for i in range(len(chan_in)):
        GPIO.setup(chan_in[i],GPIO.IN)
        print(str(chan_in[i])+", ")
    print("~~~~~~~~~~~\n")

def tempRaw():
    f1     = open(deviceFile[0],'r')
    lines1 = f1.readlines()
    f1.close
    f2     = open(deviceFile[1],'r')
    lines2 = f2.readlines()
    f2.close
    return lines1 + lines2

def readTemp():
    lines = tempRaw()
    while lines[0].strip()[-3:] != 'YES' or lines[2].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = tempRaw()
    tempOutput = lines[1].find('t='), lines[3].find('t=')
    if tempOutput != 1: 
        tempString1 = lines[1].strip()[tempOutput[0]+2:]
        tempC1 = float(tempString1)/1000
        tempF1 = tempC1 * 9.0 / 5.0 + 32.0
        tempString2 = lines[3].strip()[tempOutput[1]+2:]
        tempC2 = float(tempString2)/1000
        tempF2 = tempC2 * 9.0 / 5.0 + 32.0
        return tempC1, tempF1, tempC2, tempF2

def pingWater(): 
    GPIO.output(out_howWetTrig,GPIO.LOW)
    time.sleep(0.000006) 
    GPIO.output(out_howWetTrig,GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(out_howWetTrig,GPIO.LOW)
    while GPIO.input(in_howWet) == 0:
        pulseStart = time.time() 
    while GPIO.input(in_howWet) == 1:
        pulseEnd = time.time()
    pulseDelta = pulseEnd - pulseStart
    distance = pulseDelta * 17150 
    distance = round(distance, 3)
    if GPIO.input(in_notWet):
            return 8.9 
    return distance

def printSensorStates():
    notWet   = GPIO.input(in_notWet)
    print("Water Level: " + str(pingWater()))
    print("Reservoir Temp: " + str(readTemp()[2:]))
    print("Element  Temp: " + str(readTemp()[:2]))
    x=""
    if(notWet): 
        x = "!!Critical Water Levels Contact an ADMIN!!"
    else:
        x = "Water Level: Nominal"
    print(x)

def brewCoffee():
    #setupPin()
    coffeeOn()
    while GPIO.input(in_notWet) == 0:
        printSensorStates()
    coffeeOff()
    #noise()

