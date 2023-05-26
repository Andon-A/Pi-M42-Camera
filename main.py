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
_encIntPin  = 17

def printShutterButton(btn):
    # This won't stay.
    # Check our button.
    p = btn.pressed
    if p:
        print("Shutter pressed")

        
def printEncoderBetter(enc):
    # A lot of things have been pushed back to the controls.py file
    print("Encoder direction: " + enc.direction)
    if enc.pressedChange:
        if enc.isPressed:
            print("Encoder pressed")
        elif not enc.isPressed:
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
#shutter     = controls.button(_shutterPin, bounce=100, callback=handleShutterButton)
shutter     = controls.button(_shutterPin, bounce=100, callback=printShutterButton)
encoder     = controls.encoder(_encIntPin, printEncoderBetter, timeout=10)

while True:
    print("Interface Board temp: " + str(round(boardTemp.temp_F, 2)))
    print("CPU Temp: " + str(round(cpuTemp.temp_F, 2)))
    print("Battery Voltage: " + str(round(battery.voltage, 2)))
    print(GPIO.input(encoder.int_pin))
    #checkShutterButton()
    #encoder.reset_State()
    time.sleep(2)