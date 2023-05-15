# Main Python code for the Pi Camera

# Notes: Board thermistor's Res = 9980, Beta = 3435

# Run our updater.
# Once the watchdog is in play, we'll be able to restart automatically with this, too.
import updater
#updater.update()

from camera_lib import system, controls # Our own libraries
import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

# Pin assignments
_shutterPin = 14
_encIntPin  = 17 # CHANGE THIS when it's actually connected

# Encoder variables.
_lastCount = 0 # The last count that we had our encoder at.
_shutterPressed = False
_encPressed = False
_encDir = "Stopped"

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
    

def printEncoder(pressed, count):
    global _lastCount, _encPressed, _encDir,
    # Nor will this.
    if pressed and not _encPressed:
        print("Encoder Pressed.")
        _encPressed = pressed
    if not pressed and _encPressed:
        print("Encoder Released.")
        _encPressed = pressed
    if count != _lastCount:
        # Encoder wraps around at 65535
        # We should take this into account.
        countDif = count - _lastCount
        _lastCount = count
        if countDif < 0:
            _encDir = "Left"
        else:
            _encDir = "Right"
        print("Encoder Spun {0}, count {1}, dif {2}".format(_encDir, count, countDif))
    else:
        _encDir = "Stopped"
        print("Encoder stopped at count {0}".format(count))

# Our interfaces
adc         = system.ADC()
boardTemp   = system.Thermistor(adc.Pin0, Res=9980, Beta=3435)
cpuTemp     = system.CPU()
battery     = system.Battery(adc.Pin2)
# Shutter is hooked up to GPIO 14
shutter     = controls.button(_shutterPin, False, printShutterButton)
encoder     = controls.encoder(_encIntPin, printEncoder, timeout=1)


while True:
    print("Interface Board temp: " + str(round(boardTemp.temp_F, 2)))
    print("CPU Temp: " + str(round(cpuTemp.temp_F, 2)))
    print("Battery Voltage: " + str(round(battery.voltage, 2)))
    print("Shutter button: " + str(_shutterPressed))
    print("Encoder Count: " + str(encoder.count))
    checkShutterButton()
    encoder.clear_interrupts()
    time.sleep(10)