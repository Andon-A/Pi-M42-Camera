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


# Are we in settings?
_settingsMode = False

# Did we have an interrupt fire when another one was firing?
_encPriority = False

# Our interfaces
adc         = system.ADC()
boardTemp   = system.Thermistor(adc.Pin0, Res=9980, Beta=3435)
cpuTemp     = system.CPU()
battery     = system.Battery(adc.Pin2)
# Shutter is hooked up to GPIO 14.
# Encoder interrupt is hooked up to 17.
shutter     = controls.button(_shutterPin, bounce=100, callback=handleShutterButton)
encoder     = controls.encoder(_encIntPin, timeout=10, callback=handleEncoder)

# Camera
#cam = camera.Camera()
#cam.startCam()
        
def handleEncoder(enc):
    global _settingsMode, _encPriority
    # Handle's the encoder's direction.
    print("Dir: {0}, Pressed: {1}".format(enc.direction, enc.isPressed))
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
    if enc.pressedChange and enc.pressed:
        encTimer = time.monotonic() # When we started listening.
        t = time.monotonic() - encTimer
        while enc.pressed and t <= 5.0: # Wait until we have gone for 5 seconds or we release.
            time.sleep(0.1)
            t = time.monotonic() - encTimer
        # how long have we been pressed?
        if t >= 5.0: # If we've been pressed for 5 or more seconds, enter or leave settings menu.
            _settingsMode = not _settingsMode
            if _settingsMode:
                print("Entering Settings Mode")
            elif not _settingsMode:
                print("Exiting Settings Mode")
        else:
            menu.liveMenu.nextMenu()
            sel = menu.liveMenu.getCurrentSelect()
            print("Switched to menu {0}".format(sel[0]))
    _encPriority = True
    enc.resetState()
    # Now we need to handle our items.
    

def handleShutterButton(value):
    global _encPriority
    # This will need a lot of work to be good.
    # But it'll do for now.
    if value and not _encPriority:
        # Ignore any presses if we have the encoder button pressed at the same time.
        print("Click")
        # cam.shutter()

while True:
    #print("Interface Board temp: " + str(round(boardTemp.temp_F, 2)))
    #print("CPU Temp: " + str(round(cpuTemp.temp_F, 2)))
    #print("Battery Voltage: " + str(round(battery.voltage, 2)))
    #print(GPIO.input(encoder.int_pin))
    #checkShutterButton()
    #encoder.reset_State()
    time.sleep(0.1)
    _encPriority = False