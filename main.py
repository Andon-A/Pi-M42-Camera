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

# For our overlay
import cv2
import numpy as np

# Pin assignments
_shutterPin = 14
_encIntPin  = 17


# Are we in settings?
_settingsMode = False

# Did we have an interrupt fire when another one was firing?
_encPriority = False
_lastEnc = 0
_needsConfig = False

# Our interfaces
adc         = system.ADC()
boardTemp   = system.Thermistor(adc.Pin0, Res=9980, Beta=3435)
cpuTemp     = system.CPU()
battery     = system.Battery(adc.Pin2)

def menuNextOption():
    # Selects the next option from the appropriate menu.
    global _settingsMode
    if _settingsMode:
        # TODO: Settings menu.
        # menu.settingsMenu.nextOption()
        menu.liveMenu.nextOption()
    else:
        menu.liveMenu.nextOption()

def menuPrevOption():
    # Previous option from the appropriate menu.
    global _settingsMode
    if _settingsMode:
        # TODO: Settings menu
        # menu.settingsMenu.nextOption()
        menu.liveMenu.prevOption()
    else:
        menu.liveMenu.prevOption()

def menuNextMenu():
    # Next menu item
    global _settingsMode
    if _settingsMode:
        # TODO: Settings menu
        # menu.settingsMenu.nextMenu()
        menu.liveMenu.nextMenu()
    else:
        menu.liveMenu.nextMenu()

def getCurrentSelectMenu():
    # Gets the current item from the appropriate menu
    global _settingsMode
    if _settingsMode:
        # TODO: Settings menu
        # menu.settingsMenu.getCurrentSelect()
        return menu.liveMenu.getCurrentSelect()
    else:
        return menu.liveMenu.getCurrentSelect()
        
def handleAdjust(item):
    # Sets things depending on what the menu was.
    global _settingsMode
    if _settingsMode:
        # TODO: Settings menu
        # handleSettingsMenu(item[0], item[1])
        handleLiveMenu(item[0], item[1])
    else:
        handleLiveMenu(item[0], item[1])
    
def handleLiveMenu(menu, item):
    # Converts our ISO or Exposure and passes them to the camera.
    global _needsConfig
    iso = None
    exp = None
    if menu == "ISO":
        # We have ISO, so set it.
        iso = 0
        if item != "AUTO":
            iso = item
        if iso != cam.ISO:
            cam.ISO = iso
            print("Updating camera ISO to {0}".format(iso))
            _needsConfig = True
            return True
        else:
            return False
    if menu == "Exposure":
        s = 0
        if item != 'AUTO':
            if item[-1:] == '"':
                # We have an exposure denoted in seconds, so don't worry about division.
                s = float(item[:-1])
            elif item[1] == '/':
                # We have an exposure denoted by a divisor.
                s = 1.0 / float(item[2:])
        exp = s
        if exp != cam.exposure:
            cam.exposure = exp
            print("Updating camera exposure to {0}".format(exp))
            _needsConfig = True
            return True
        else:
            return False
    if menu == "Mode":
        m = 0
        if item == "Still":
            m = 0
        elif item == "Video":
            m = 1
        if m != cam.mode:
            cam.mode = m
            print("Setting camera mode to {0}".format(item))
            _needsConfig = True
            return True
        else:
            return False
        
def handleEncoder(enc):
    global _settingsMode, _encPriority, _lastEnc
    _lastEnc = time.monotonic()
    _encPriority = True
    # Handle's the encoder's direction.
    if enc.direction == "Left":
        menuPrevOption()
        handleAdjust(getCurrentSelectMenu())
    elif enc.direction == "Right":
        menuNextOption()
        handleAdjust(getCurrentSelectMenu())
    # Handle the button press.
    if enc.pressedChange and enc.pressed:
        print("Pressed")
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
            menuNextMenu()
            print("Switched to menu {0}".format(getCurrentSelectMenu()[0]))
    time.sleep(0.02) # Make sure we don't overwhelm the i2c bus
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

def updateRegOverlay():
    # Creates and assigns the overlay for the base info
    # Text info
    color = (255, 255, 255, 255)
    origin = (10, 30)
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 1
    thickness = 2
    overlay = np.zeros((800, 480, 4), dtype=np.uint8)
    cv2.putText(overlay, str("ISO: {0}\nExposure: {1}".format(cam.ISO, cam.exposure)), origin,
                font, scale, color, thickness)
    cam.camera.set_overlay(overlay)
    
    

# Shutter is hooked up to GPIO 14.
# Encoder interrupt is hooked up to 17.
shutter     = controls.button(_shutterPin, bounce=250, callback=handleShutterButton)
encoder     = controls.encoder(_encIntPin, timeout=10, callback=handleEncoder)
encoder.resetState() # Make sure we clear any lurking interrupts

# Camera
cam = camera.Camera()
cam.startCam()

while True:
    #print("Interface Board temp: " + str(round(boardTemp.temp_F, 2)))
    #print("CPU Temp: " + str(round(cpuTemp.temp_F, 2)))
    #print("Battery Voltage: " + str(round(battery.voltage, 2)))
    #print(GPIO.input(encoder.int_pin))
    #checkShutterButton()
    #encoder.reset_State()
    time.sleep(0.2)
    if (time.monotonic() > _lastEnc + 0.5) and _needsConfig:
        cam.reconfigure()
        _needsConfig = False
    _encPriority = False
    updateRegOverlay()
    encoder.resetState() # Don't want any lurking interrupts