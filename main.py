# Main Python code for the Pi Camera

# Notes: Board thermistor's Res = 9980, Beta = 3435

# Run our updater.
# Once the watchdog is in play, we'll be able to restart automatically with this, too.
import updater
updater.update()

from camera_lib import system, controls # Our own libraries
import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

# Pin assignments
shutterPin = 14
encIntPin  = 17

# Encoder variables.
lastCount = 0 # The last count that we had our encoder at.
shutterPressed = False
encPressed = False
encSpeed = "None"
encDir = "Stopped"
encMidSpeed = 20 # The change for a medium speed threshold
encHiSpeed = 100 # The change for a high speed threshold

def checkShutterButton():
    # See if our shutter button is actually
    if shutter.pressed != shutterPressed:
        printShutterButton(shutter.pressed)

def printShutterButton(value):
    # This won't stay.
    if value:
        print("Shutter pressed.")
    else:
        print("Shutter released.")
    shutterPressed = value
    #time.sleep(0.1)
    #checkShutterButton()
    

def printEncoder(pressed, count):
    # Nor will this.
    if pressed and not encPressed:
        print("Encoder Pressed.")
        encPressed = pressed
    if not pressed and encPressed:
        print("Encoder Released.")
        encPressed = pressed
    if count != lastCount:
        countDif = count - lastCount
        lastCount = count
        if countDif < 0:
            encDir = "Left"
        else:
            encDir = "Right"
        if countDif < encMidSpeed:
            encSpeed = "Slow"
        elif countDif < encHiSpeed:
            encSpeed = "Medium"
        else:
            encSpeed = "Fast"
        print("Encoder Spun {0}, count {1}, dif {2}".format(dir, count, countDif))
    else:
        encDir = "Stopped"
        encSpeed = "None"
        print("Encoder stopped at count {0}".format(count))

# Our interfaces
adc         = system.ADC()
boardTemp   = system.Thermistor(adc.Pin0, Res=9980, Beta=3435)
cpuTemp     = system.CPU()
battery     = system.Battery(adc.Pin2)
# Shutter is hooked up to GPIO 14
shutter     = controls.button(shutterPin, False, printShutterButton)
encoder     = controls.encoder(encIntPin, printEncoder)


while True:
    print("Interface Board temp: " + str(round(boardTemp.temp_F, 2)))
    print("CPU Temp: " + str(round(cpuTemp.temp_F, 2)))
    print("Battery Voltage: " + str(round(battery.voltage, 2)))
    print("Shutter button: " + str(shutterPressed))
    checkShutterButton()
    time.sleep(10)