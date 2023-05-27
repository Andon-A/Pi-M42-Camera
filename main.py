# Main Python code for the Pi Camera

# Notes: Board thermistor's Res = 9980, Beta = 3435

# Run our updater.
# Once the watchdog is in play, we'll be able to restart automatically with this, too.
#import updater
#updater.update()

# Set our paths
import sys
sys.path.append('./camera_lib')

import system, controls, camera, menu # Our own libraries
import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

# Pin assignments
_shutterPin = 14
_encIntPin  = 17

# Timer for the encoder.
_encTimer

# Are we in settings?
_settingsMode = False

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
        
def handleEncoder(enc):
    global _encTimer, _settingsMode
    # Handle's the encoder's direction.
    sel = None
    if enc.direction == "Left":
        menu.liveMenu.prevOption()
        sel = menu.liveMenu.getCurrentSelect()
        print("Selected {1} from {0}".format(sel[0], sel[1]))
    elif enc.direction == "Right":
        menu.liveMenu.nextOption()
        sel = menu.liveMenu.getCurrentSelect()
        print("Selected {1} from {0}".format(sel[0], sel[1]))
    # Handle the button press.
    if enc.pressedChange and enc.isPressed:
        _encTimer = time.monotonic() # When we started listening.
    elif enc.pressedChange and not enc.isPressed:
        # Encoder is released. How long has it been?
        t = time.monotonic() - _encTimer
        if t >= 5.0: # If we've been pressed for 5 or more seconds, enter or leave settings menu.
            _settingsMode = not _settingsMode
        else:
            menu.liveMenu.nextMenu()
            sel = menu.liveMenu.getcurrentSelect()
            print("Switched to menu {0}".format(sel[0]))
    # Now we need to handle our items.
    

def handleShutterButton(value):
    # This will need a lot of work to be good.
    # But it'll do for now.
    if value:
        print("Click")
        # cam.shutter()

# Our interfaces
adc         = system.ADC()
boardTemp   = system.Thermistor(adc.Pin0, Res=9980, Beta=3435)
cpuTemp     = system.CPU()
battery     = system.Battery(adc.Pin2)
# Shutter is hooked up to GPIO 14.
# Encoder interrupt is hooked up to 17.
shutter     = controls.button(_shutterPin, bounce=100, callback=handleShutterButton)
encoder     = controls.encoder(_encIntPint, timeout=10, callback=handleEncoder)
#shutter     = controls.button(_shutterPin, bounce=100, callback=printShutterButton)
#encoder     = controls.encoder(_encIntPin, printEncoderBetter, timeout=10)

while True:
    print("Interface Board temp: " + str(round(boardTemp.temp_F, 2)))
    print("CPU Temp: " + str(round(cpuTemp.temp_F, 2)))
    print("Battery Voltage: " + str(round(battery.voltage, 2)))
    print(GPIO.input(encoder.int_pin))
    #checkShutterButton()
    #encoder.reset_State()
    time.sleep(2)