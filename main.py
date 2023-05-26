# Main Python code for the Pi Camera

# Notes: Board thermistor's Res = 9980, Beta = 3435

# Run our updater.
# Once the watchdog is in play, we'll be able to restart automatically with this, too.
#import updater
#updater.update()

# Set our paths
import sys
sys.path.append('./camera_lib')

import system, controls, camera # Our own libraries
import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

# Pin assignments
_shutterPin = 14
_encIntPin  = 17 # CHANGE THIS when it's actually connected

# Encoder variables.
_lastCount = 0 # The last count that we had our encoder at. It resets when we start.
_shutterPressed = False # The last state our shutter was at. Default to unpressed.
_encPressed = False # The last state our encoder button was at. Default to unpressed.
_encDir = "Stopped" # The last direction our encoder was turning.

def checkShutterButton():
    # See if our shutter button is actually
    global _shutterPressed
    if shutter.pressed != _shutterPressed:
        printShutterButton(shutter.pressed)

def printShutterButton(value):
    global _shutterpressed
    # This won't stay.
    if value:
        print("Shutter pressed.")
    else:
        print("Shutter released.")
    _shutterPressed = value
    #time.sleep(0.1)
    #checkShutterButton()
        
def printEncoderBetter(enc):
    # A lot of things have been pushed back to the controls.py file
    print("Encoder direction: " + enc.direction)
    if encoder.pressedChange:
        if encoder.isPressed:
            print("Encoder pressed")
        elif not encoder.isPressed:
            print("Encoder released")
    enc.resetState() # Return everything to zero state.
        
        

# Camera
#cam = camera.Camera()
#cam.startCam()

def handleShutterButton(value):
    # This will need a lot of work to be good.
    # But it'll do for now.
    if value:
        cam.shutter()

# Our interfaces
adc         = system.ADC()
boardTemp   = system.Thermistor(adc.Pin0, Res=9980, Beta=3435)
cpuTemp     = system.CPU()
battery     = system.Battery(adc.Pin2)
# Shutter is hooked up to GPIO 14.
# Encoder interrupt is hooked up to 17.
#shutter     = controls.button(_shutterPin, False, 10, handleShutterButton)
shutter     = controls.button(_shutterPin, False, 10, printShutterButton)
encoder     = controls.encoder(_encIntPin, printEncoderBetter, timeout=10)

while True:
    print("Interface Board temp: " + str(round(boardTemp.temp_F, 2)))
    print("CPU Temp: " + str(round(cpuTemp.temp_F, 2)))
    print("Battery Voltage: " + str(round(battery.voltage, 2)))
    print("Shutter button: " + str(_shutterPressed))
    print("Encoder Count: " + str(encoder.count))
    checkShutterButton()
    #encoder.reset_State()
    time.sleep(1)