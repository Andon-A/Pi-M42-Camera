# Main Python code for the Pi Camera

# Notes: Board thermistor's Res = 9980, Beta = 3435
# Notes: 
from camera_lib import system, controls # Our own library
import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

# Pin assignments
_shutterPin = 14
_encIntPin  = 12 # CHANGE THIS when it's actually connected

# Encoder variables.
_lastCount = 0 # The last count that we had our encoder at.
_shutterPressed = False
_encPressed = False
_encSpeed = "None"
_encDir = "Stopped"
_encMidSpeed = 20 # The change for a medium speed threshold
_encHiSpeed = 100 # The change for a high speed threshold

def checkShutterButton():
    # See if our shutter button is actually
    if shutter.pressed != _shutterPressed:
        printShutterButton(shutter.pressed)

def printShutterButton(value):
    # This won't stay.
    if value:
        print("Shutter pressed.")
    else:
        print("Shutter released.")
    _shutterPressed = value
    time.sleep(0.1)
    checkShutterButton()
    

def printEncoder(pressed, count):
    # Nor will this.
    if pressed and not _encPressed:
        print("Encoder Pressed.")
        _encPressed = pressed
    if not pressed and _encPressed:
        print("Encoder Released.")
        _encPressed = pressed
    if count != _lastCount:
        countDif = count - lastCount
        _lastCount = count
        if countDif < 0:
            _encDir = "Left"
        else:
            _encDir = "Right"
        if countDif < _encMidSpeed:
            _encSpeed = "Slow"
        elif countDif < _encHiSpeed:
            _encSpeed = "Medium"
        else:
            _encSpeed = "Fast"
        print("Encoder Spun {0}, count {1}, dif {2}".format(dir, count, countDif))
    else:
        _encDir = "Stopped"
        _encSpeed = "None"
        print("Encoder stopped at count {0}".format(count))

# Our interfaces
adc         = system.ADC()
boardTemp   = system.Thermistor(adc.Pin0)
cpuTemp     = system.CPU()
battery     = system.Battery(adc.Pin2)
# Shutter is hooked up to GPIO 14
shutter     = controls.button(_shutterPin, False, printShutterButton)
encoder     = controls.encoder(_encIntPin, printEncoder)


while True:
    print("Interface Board temp: " + str(boardTemp.temp_F))
    print("CPU Temp: " + str(cpuTemp.temp_F))
    print("Battery Voltage: " + str(battery.voltage))
    checkShutterButton()
    time.sleep(10)