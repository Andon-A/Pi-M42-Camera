# Main Python code for the Pi Camera

# Notes: Board thermistor's Res = 9980, Beta = 3435

# Run our updater.
# Once the watchdog is in play, we'll be able to restart automatically with this, too.
#import updater
#updater.update()

# Set our paths
import sys
sys.path.append('./camera_lib')
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
_shutterPin = 12
_encIntPin  = 6


# Are we in settings?
_settingsMode = False

# Did we have an interrupt fire when another one was firing?
_lastEnc = 0
_lastPress = 0
_needsConfig = False

# Our interfaces
#adc         = system.ADC()
cpuTemp     = system.CPU()
#battery     = system.Battery(adc.Pin2)

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
    global _settingsMode, _lastEnc
    _lastEnc = time.monotonic()
    # Handle's the encoder's direction.
    if enc.direction == "Left":
        menuPrevOption()
        handleAdjust(getCurrentSelectMenu())
    elif enc.direction == "Right":
        menuNextOption()
        handleAdjust(getCurrentSelectMenu())
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
            menuNextMenu()
            print("Switched to menu {0}".format(getCurrentSelectMenu()[0]))
    time.sleep(0.02) # Make sure we don't overwhelm the i2c bus
    enc.resetState()
    # Now we need to handle our items.
    
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
    batt_pct = int(batt.chargePct * 100)
    if batt_pct < batt.red_pct:
        overlay.addTextAtLoc("Batt: {0}%".format(batt_pct), color=(255, 0, 0, 255), loc=battXY)
    elif batt_pct < batt.yel_pct:
        overlay.addTextAtLoc("Batt: {0}%".format(batt_pct), color=(255, 255, 0, 255), loc=battXY)
    else:
        overlay.addTextAtLoc("Batt: {0}%".format(batt_pct), loc=battXY)
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

shutter     = controls.button(_shutterPin, bounce=50, callback=handleShutterButton)
encoder     = controls.encoder(_encIntPin, timeout=10, callback=handleEncoder)
encoder.resetState()

# ADC and battery
ADC = system.ADC()
batt = system.Battery(ADC.Pin2)

# Camera
cam = camera.Camera()
cam.startCam()

# Regular (Camera view) overlay
regOverlay = camera.Overlay(camera=cam, textOrigin=(10, 25))

# We'll need an Overlay for each of our text menus.

_isPressed = False


while True:
    #print("Interface Board temp: " + str(round(boardTemp.temp_F, 2)))
    #print("CPU Temp: " + str(round(cpuTemp.temp_F, 2)))
    #print("Battery Voltage: " + str(round(battery.voltage, 2)))
    #print(GPIO.input(encoder.int_pin))
    #checkShutterButton()
    #encoder.reset_State()
    time.sleep(0.1)
    timenow = round(time.monotonic(), 2)
    if (timenow > _lastEnc + 0.5) and _needsConfig:
        cam.reconfigure()
        _needsConfig = False
        encoder.resetState()
    if timenow > _lastEnc + 2 and encoder.hasInterrupt:
        # print("Encoder has interrupt. Clearing.")
        encoder.resetState() # Clear lurking interrupts after a few seconds.
    if round(timenow, 0) % 5 == 0:
        # Make sure we save our config regularly.
        cam_config.saveConfig
    if batt.voltage <= batt.cutoff_voltage: # We're running into battery damage range.
        cam_config.saveConfig # Make sure our current state is saved.
        queueShutdown()
    # Pressing the button doesn't seem like it's triggering the interrupt.
    if encoder.pressed and not _isPressed:
        _isPressed = True
        encoder.isPressed = True
        encoder.pressedChange = True
        handleEncoder(encoder)
        time.sleep(0.5) # Give us a little debounce time.
    elif not encoder.pressed and _isPressed:
        _isPressed = False
        encoder.isPressed = False
        encoder.pressedChange = True
        handleEncoder(encoder)
        time.sleep(0.5)
    updateRegOverlay(regOverlay)
    #encoder.resetState() # Don't want any lurking interrupts