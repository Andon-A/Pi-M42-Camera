# Main Python code for the Pi Camera

# Notes: Board thermistor's Res = 9980, Beta = 3435

# Run our updater.
# Once the watchdog is in play, we'll be able to restart automatically with this, too.
#import updater
#updater.update()

# Set our paths
import sys
sys.path.append('/home/camera/Software/camera_lib')
import os

import system, controls, camera, menu, cam_config # Our own libraries
import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

# Our backlight control.
from rpi_backlight import Backlight # And our backlight
backlight = Backlight()
# Set the brightness.
backlight.fade_duration = 0 # We want changes instantly
backlight.brightness = 75

# Pin assignments
_shutterPinIn = 20 #d21
_shutterPinOut = 21 #d20
_powerPin = 16 #d16


# Are we in settings?
_settingsMode = False
_changedSettingsMode = False

_lastEnc = 0
_lastPress = 0
_needsConfig = False

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
        iso = item
        if cam.ISO[0].lower() != str(iso).lower():
            cam.ISO = iso
            print("Camera ISO set to {0}".format(cam.ISO))
            cam.setControls()
            return True
        else:
            return False
    elif menu == "Exposure":
        exp = item
        if cam.exposure[0].lower() != exp.lower():
            cam.exposure = exp
            print("Camera exposure set to {0}".format(cam.exposure))
            cam.setControls()
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
            print("Setting camera mode to {0}".format(cam.mode))
            _needsConfig = True
            return True
        else:
            return False
        
def handleEncoder(enc):
    #print("Handling Encoder")
    global _settingsMode, _changedSettingsMode
    enc.updateInfo()
    # Handle's the encoder's direction.
    if enc.direction == "Left":
        menuPrevOption()
        handleAdjust(getCurrentSelectMenu())
    elif enc.direction == "Right":
        menuNextOption()
        handleAdjust(getCurrentSelectMenu())
    # Do we want to do something about our button press?
    # Have we been held for more than 5 seconds?
    if enc.isPressed == True and (enc.pressedChange > time.monotonic() + 5):
        # enter settings mode
        _settingsMode = not _settingsMode
        if _settingsMode:
            print("Entering Settings Mode")
        elif not _settingsMode:
            print("Exiting Settings Mode")
        _changedSettingsMode = True
    elif enc.isPressed == False and (enc.pressedChange > time.monotonic() - 0.25) and _changedSettingsMode == False:
        # Regular button press.
        menuNextMenu()
        print("Switched to menu {0}".format(getCurrentSelectMenu()[0]))
        time.sleep(0.25) # Make sure we don't ping the thing too many times.
    elif enc.isPressed == False and _changedSettingsMode == True:
        # If we recently changed into or out of settings mode, don't do anything when releasing
        # the button except resetting that flag.
        _changedSettingsMode == False
    
def handleShutterButton(button):
    global _lastEnc, _needsConfig, _lastPress
    # This will need a lot of work to be good.
    # But it'll do for now.
    # Wait until we're done twirling the encoder and make sure we're not in need of a reconfigure.
    timenow = time.monotonic()
    if ((timenow > _lastEnc + 0.5)
        and timenow > _lastPress + 0.2
        and not _needsConfig
        and button.pressed):
        print("Click {0}".format(round(time.monotonic(),2)))
        _lastPress = time.monotonic()
        cam.shutter()

battXY = (360,760)

def updateRegOverlay(overlay):
    # Updates our regular overlay.
    overlay.clearLines() # We're updating dynamic info, so these need to be cleaned and rewritten.
    current = menu.liveMenu.getCurrentSelect()[0]
    if current.lower() == "iso":
        overlay.addLine("ISO: {0}".format(cam.ISO[0]), color=(255, 255, 0, 255))
    else:
        overlay.addLine("ISO: {0}".format(cam.ISO[0]))
    if current.lower() == "exposure":
        overlay.addLine("Exposure: {0}".format(cam.exposure[0]), color=(255, 255, 0, 255))
    else:
        overlay.addLine("Exposure: {0}".format(cam.exposure[0]))
    if current.lower() == "mode":
        overlay.addLine("Mode: {0}".format(cam.mode[0]), color=(255, 255, 0, 255))
    else:
        overlay.addLine("Mode: {0}".format(cam.mode[0]))
    if batt.charging:
        overlay.addTextAtLoc("Batt: {0}%".format(batt.cap), color=(0, 255, 0, 255),loc=battXY)
    if batt.cap < 33:
        overlay.addTextAtLoc("Batt: {0}%".format(batt.cap), color=(255, 0, 0, 255), loc=battXY)
    elif batt.cap < 40:
        overlay.addTextAtLoc("Batt: {0}%".format(batt.cap), color=(255, 255, 0, 255), loc=battXY)
    else:
        overlay.addTextAtLoc("Batt: {0}%".format(batt.cap), loc=battXY)
    if not cam.isSaving:
        # If we're saving, don't worry about updating.
        overlay.showOverlay()
    
def queueShutdown(override=False):
    # Cleanly shuts down the camera.
    # Needs hardware support, but works for low battery.
    while cam.isSaving and not override:
        # Wait for our save to complete. If we have the override, skip this.
        pass
    print("Shutting down.")
    filemon = system.Service("camera_filemon")
    filemon.stop() # Turn off our file monitor so we don't auto restart just to shut down.
    os.system('sudo shutdown -h now') # Turn off the machine.
    exit()

shutter     = controls.button(_shutterPinIn, _shutterPinOut, bounce=50, callback=handleShutterButton)
encoder     = controls.encoder2()

# Battery
batt = system.Battery()

# Camera
cam = camera.Camera()
cam.startCam()

# Regular (Camera view) overlay
regOverlay = camera.Overlay(camera=cam, textOrigin=(10, 25))

# We'll need an Overlay for each of our text menus.



batt.updateInfo()
while True:
    #print("Interface Board temp: " + str(round(boardTemp.temp_F, 2)))
    #print("CPU Temp: " + str(round(cpuTemp.temp_F, 2)))
    #print("Battery Voltage: " + str(round(battery.voltage, 2)))
    #print(GPIO.input(encoder.int_pin))
    #checkShutterButton()
    #encoder.reset_State()
    time.sleep(0.1)
    timenow = round(time.monotonic(), 2)
    # Time is given in seconds.
    if round(timenow, 0) % 5 == 0:
        # Every 5 seconds:
        # Make sure we save our config regularly.
        cam_config.saveConfig
        # Update our battery info
        batt.updateInfo()
    # Always check our encoder.
    handleEncoder(encoder)
    # Update our camera config if we need to. But wait until we're not doing anything.
    if (encoder.lastUpdate < timenow - 0.5) and encoder.isPressed == False and _needsConfig:
        print ("Reconfiguring camera")
        cam.reconfigure()
        _needsConfig = False
    updateRegOverlay(regOverlay)