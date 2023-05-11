# This handles our controls. That is, it tells us what our controls are doing.

import board
import digitalio
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

# MCP23008 GPIO
from adafruit_mcp230xx.mcp23008 import MCP23008

i2c = board.I2C()

class modeKnob:
    # Our mode knob goes through an MCP23008 with an address of 0x20
    # Initially, I tried getting the Encoder through another one
    # But that just didn't work.
    def __init__(self, mcp_i2c=i2c, address=0x20):
        self.MCP = MCP23008(mcp_i2c, address=address)
        # Set up our common pin.
        self.common = self.MCP.get_pin(7)
        self.common.direction = digitalio.Direction.OUTPUT
        self.common.value = False # Drive it low.
        # Set up our other pins.
        # They are all pulled up.
        # The current mode select is only a 5-position one, but they make them up to 7 that work
        # largely in the same way.
        self.select = []
        for p in range(0,6):
            self.select.append(self.MCP.get_pin(p))
            self.select[p].direction = digitalio.Direction.INPUT
            self.select[p].pull = digitalio.Pull.UP
        
    @property
    def position(self):
        # This presumes that only one is ever selected.
        # Which is how the rotary switch should work.
        # So it simply selects the first one it finds.
        # Returns 7 if none are selected somehow.
        pos = 7
        for pin in range(0,6):
            if self.select[pin].value == False:
                pos = pin
                break #Found our pin, no need to continue.
        return pos

# Our Shutter Sense switch is on GPIO 1
# Our Encoder switch is on GPIO 25, and is inverted.

class button:
    def __init__(self, pin, inverted=False, callback=None):
        # Set up a button.
        self.pin = pin
        self.inverted = inverted
        self.callback = callback
        if self.inverted:
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(self.pin, GPIO.BOTH, bouncetime=100, callback=self.getPressed)
        else:
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.add_event_detect(self.pin, GPIO.BOTH, bouncetime=100, callback=self.getPressed)
    
    @property
    def pressed(self):
        status = GPIO.input(self.pin)
        if self.inverted:
            status = not status
        return status
    
    def getPressed(self, channel):
        self.callback(self.pressed)
        return self.pressed

# Encoder class, from https://github.com/nstansby/rpi-rotary-encoder-python
# Encoder A pin is GPIO24
# Encoder B pin is GPIO7
class encoder:

    def __init__(self, leftPin, rightPin, callback=None):
        self.leftPin = leftPin
        self.rightPin = rightPin
        self.value = 0
        self.state = '00'
        self.direction = None
        self.callback = callback
        GPIO.setup(self.leftPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.rightPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.leftPin, GPIO.BOTH, callback=self.transitionOccurred)  
        GPIO.add_event_detect(self.rightPin, GPIO.BOTH, callback=self.transitionOccurred)  

    def transitionOccurred(self, channel):
        p1 = GPIO.input(self.leftPin)
        p2 = GPIO.input(self.rightPin)
        newState = "{}{}".format(p1, p2)

        if self.state == "00": # Resting position
            if newState == "01": # Turned right 1
                self.direction = "R"
            elif newState == "10": # Turned left 1
                self.direction = "L"

        elif self.state == "01": # R1 or L3 position
            if newState == "11": # Turned right 1
                self.direction = "R"
            elif newState == "00": # Turned left 1
                if self.direction == "L":
                    self.value = self.value - 1
                    if self.callback is not None:
                        self.callback(self.value, self.direction)

        elif self.state == "10": # R3 or L1
            if newState == "11": # Turned left 1
                self.direction = "L"
            elif newState == "00": # Turned right 1
                if self.direction == "R":
                    self.value = self.value + 1
                    if self.callback is not None:
                        self.callback(self.value, self.direction)

        else: # self.state == "11"
            if newState == "01": # Turned left 1
                self.direction = "L"
            elif newState == "10": # Turned right 1
                self.direction = "R"
            elif newState == "00": # Skipped an intermediate 01 or 10 state, but if we know direction then a turn is complete
                if self.direction == "L":
                    self.value = self.value - 1
                    if self.callback is not None:
                        self.callback(self.value, self.direction)
                elif self.direction == "R":
                    self.value = self.value + 1
                    if self.callback is not None:
                        self.callback(self.value, self.direction)
                
        self.state = newState

    def getValue(self):
        return self.value