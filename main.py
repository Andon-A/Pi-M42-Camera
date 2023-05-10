# Main Python code for the Pi Camera

# Notes: Board thermistor's Res = 9980, Beta = 3435
# Notes: 
from camera_lib import interface
import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

encoder = 25
shutter = 1
GPIO.setup(shutter, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(encoder, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(encoder, GPIO.BOTH, bouncetime=100)
GPIO.add_event_detect(shutter, GPIO.BOTH, bouncetime=100)

modeKnob = interface.modeKnob()
mode = modeKnob.position

while True:
    # Our main loop.
    if GPIO.event_detected(encoder):
        if GPIO.input(encoder):
            print("Encoder released.")
        else:
            print("Encoder pressed.")
    if GPIO.event_detected(shutter):
        time.sleep(0.01)
        if GPIO.input(shutter):
            print("Shutter pressed.")
        else:
            print("Shutter released")
    if mode != modeKnob.position:
        time.sleep(0.125) # Delay a little to get the new mode.
        mode = modeKnob.position
        print("Mode: " + str(modeKnob.position))

