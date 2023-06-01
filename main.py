# Main Python code for the Pi Camera

# Notes: Board thermistor's Res = 9980, Beta = 3435

# Run our updater.
# Once the watchdog is in play, we'll be able to restart automatically with this, too.
#import updater
#updater.update()

# Set our paths
import sys
sys.path.append('./camera_lib')

import system, controls, camera, menu, cam_config # Our own libraries
import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

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
            _needsConfig = True
            return True
        else:
            return False
    elif menu == "Exposure":
        exp = item
        if cam.exposure[0].lower() != exp.lower():
            cam.exposure = exp
            print("Camera exposure set to {0}".format(cam.exposure))
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
            print("Setting camera mode to {0}".format(cam.mode))
            _needsConfig = True
            return True
        else:
            return False
        
def handleEncoder(enc):
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
    overlay.showOverlay()
    
    

shutter     = controls.button(_shutterPin, bounce=50, callback=handleShutterButton)
encoder     = controls.encoder(_encIntPin, timeout=10, callback=handleEncoder)
encoder.resetState()

# Camera
cam = camera.Camera()
cam.startCam()

# Regular (Camera view) overlay
regOverlay = camera.Overlay(camera=cam, textOrigin=(10, 25))

# We'll need an Overlay for each of our text menus.

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
        encoder.resetState() # Clear lurking interrupts after a few seconds.
    if round(timenow, 0) % 5 == 0:
        # Make sure we save our config regularly.
        cam_config.saveConfig
    updateRegOverlay(regOverlay)
    #encoder.resetState() # Don't want any lurking interrupts