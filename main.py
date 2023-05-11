# Main Python code for the Pi Camera

# Notes: Board thermistor's Res = 9980, Beta = 3435
# Notes: 
from camera_lib import system, controls # Our own library
import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

def printEncoder(value, direction):
    print("Encoder rotated {0} with value {1}".format(direction, value))

def printEncoderButton(value):
    if value:
        print("Encoder pressed.")
    else:
        print("Encoder Released.")

def printShutter(value):
    if value:
        print("Shutter pressed.")
    else:
        print("Shutter released.")

def printMode(value):
    if value == 0:
        value = "Automatic"
    elif value == 1:
        value = "ISO"
    elif value == 2:
        value = "Shutter"
    elif value == 3:
        value = "ISO/Shutter"
    elif value == 4:
        value = "Video"
    print("Mode changed to: {0}".format(value))


# Our interfaces
adc         = system.ADC()
boardTemp   = system.Thermistor(adc.Pin0)
cpuTemp     = system.CPU()
battery     = system.Battery(adc.Pin2)
encoder     = controls.encoder(24, 7, printEncoder)
encButton   = controls.button(25, true, printEncoderButton)
shutter     = controls.button(1, false, printShutterButton)
modeKnob    = controls.modeKnob()


mode = modeKnob.position

while True:
    if mode != modeKnob.position:
        mode = modeKnob.position
        printMode(mode)

