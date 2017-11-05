import coffee
import RPi.GPIO as GPIO
import app
from datetime import datetime, time

def main():
    coffee.setupPin()
    prevTime = datetime.now()
    while True:
        while GPIO.input(coffee.in_notWet) == 0:
            if ((datetime.now() - prevTime).seconds > 5):
                temps = coffee.readTemp()
                new=app.Stats(coffeeC=temps[0], coffeeF=temps[1], heaterC=temps[2], heaterF=temps[3])
                new.save()
                prevTime = datetime.now()
            coffee.printSensorStates()
        coffee.coffeeOff()

main()
