# This handles our controls. That is, it tells us what our controls are doing.

# Our GPIO setup
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
import time

# Out I2C setup. We use Sparkfun's qwiic system.
import qwiic_twist

class button:
    def __init__(self, pinIn, pinOut, bounce=100, callback=None):
        # Set up a button.
        self.pinIn = pinIn
        self.pinOut = pinOut
        self.callback = callback
        GPIO.setup(self.pinIn, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.pinOut, GPIO.OUT)
        GPIO.output(self.pinOut, 1)
        GPIO.add_event_detect(self.pinIn, GPIO.RISING, bouncetime=bounce, callback=self.getPressed)

    @property
    def pressed(self):     
        return GPIO.input(self.pinIn)
    
    def getPressed(self, channel):
        self.callback(self)
        return self.pressed

class encoder:

    def __init__(self, callback, color=(0,0,0), timeout=100):
        self.callback = callback    # We return pressed and count
        self._color = (0,0,0)       # Our LED color. Default to nothing, it's set later.
        self._timeout = -1          # How long we wait (ms) after the encoder has stopped moving to ping.
                                    # Again, default to a bad value, and we'll be set later.
        self.enabled = False        # Has our encoder properly enabled?
        self.isPressed = False      # Is our button (still) pressed?
        self.direction = "None"     # What direction did we last move?
        self.pressedChange = False  # Has our pressed state changed?
        # Now set up the twist.
        self.twist = qwiic_twist.QwiicTwist()
        if self.twist.connected == False:
            print("Encoder not detected.")
        else:
            self.twist.begin()
            self.enabled = True
            self.color = color # The RGB color of the LED
            self.timeout = timeout
            self.count = 5
            self.twist.clear_interrupts() # Make sure nothing is lurking.
            print("Encoder initailized")
    
    @property
    def pressed(self):
        # Returns our current pressed state.
        if self.enabled:
            pressed = None
            while pressed is None:
                try:
                    # print("Attempting get pressed")
                    pressed = self.twist.pressed
                except:
                    # I2c error.
                    time.sleep(0.05)
            return pressed
        else:
            return False
    
    @property
    def count(self):
        if self.enabled:
            count = None
            while count is None:
                try:
                    # print("Attempting count get")
                    count = self.twist.count
                except:
                    # I2c error.
                    time.sleep(0.05)
            return count
        else:
            return 0
    
    @count.setter
    def count(self, count):
        if self.enabled:
            c = None
            while c is None:
                try:
                    # print("Attempting count set")
                    self.twist.count = count
                    c = True
                except:
                    time.sleep(0.05)
            return self.count
        else:
            return 0
        
    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self, color):
        # Sets the color. Color is an RGP tuple
        if self.enabled:
            c = None
            while c is None:
                try:
                    # print("Attemtping color")
                    self.twist.set_color(color[0], color[1], color[2])
                    c = True
                except:
                    time.sleep(0.05)                
            self._color = color
            return True
        else:
            return False
    
    @property
    def timeout(self):
        return self._timeout
    
    @timeout.setter
    def timeout(self, ms):
        # Sets the timeout of the interrupt pin
        # It waits this long after the encoder has stopped moving to trigger the interrupt
        # Min is 1ms, max is 65000 ms (65 sec), which we constrain to.
        if self.enabled:
            if ms < 1:
                ms = 1
            elif ms > 65000:
                ms = 65000
            tm = None
            while tm is None:
                try:
                    # print("Attemtping timout")
                    self.twist.set_int_timeout(ms)
                    tm = True
                except:
                    time.sleep(0.05)
            self._timeout = ms
            return self._timeout
        else:
            return 0
    
    def resetState(self):
        self.count = 5
        self.direction = "None"
        self.pressedChange = False
        # Attempt to clear our interrupts
        try:
            self.twist.clear_interrupts()
        except:
            pass
    
    def detectInput(self, channel):
        # This is triggered when we detect an interrupt.
        if self.enabled:
            # Only do the callback if we have a callback set and we're enabled.
            if self.pressed and not self.isPressed:
                self.isPressed = True
                self.pressedChange = True
            elif not self.pressed and self.isPressed:
                self.isPressed = False
                self.pressedChange = True
            r = self.count - 5 # We know where this starts. Negative = left, positive = right
            if r > 0:
                self.direction = "Right"
            elif r < 0:
                self.direction = "Left"
            self.callback(self)
        

class encoder2:
    # This is a version of the encoder that utilizes polling instead of interrupts.
    
    def __init__(self, color=(0,0,0)):
        self.twist = qwiic_twist.QwiicTwist()
        if self.twist.connected == False:
            print("Encoder not detected.")
            self._color = None
            self.enabled = False
            self.isPressed = None
            self.pressedChange = 0
            self.direction = "None"
            self.lastUpdate = 0
        else:
            self.twist.begin()
            self.enabled = True
            self._color = None
            self.color = color
            self.isPressed = None
            self.pressedChange = 0
            self.direction = "None"
            self.twist.count = 32000
            print("Encoder initialized")
            self.lastUpdate = 0
            self.updateInfo()
    
    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self, color):
        # Sets the color, an RGB tuple.
        if self.enabled == False:
            return False
        else:
            c = None
            while c is None:
                try:
                    self.twist.set_color(color[0], color[1], color[2])
                    c = True
                except:
                    time.sleep(0.05)
            self._color = color
            return True
    
    def updateInfo(self):
        # Updates our statuses
        if self.enabled == False:
            return
        else:
            update = False
            count = None
            pressed = None
            while update == False:
                try:
                    count = self.twist.count
                    pressed = self.twist.pressed
                    update = True
                except:
                    time.sleep(0.05)
            # Since our count is "fixed" at 32000, we can figure out left, right, or not moved.
            if count < 32000:
                self.direction = "Left"
            elif count > 32000:
                self.direction = "Right"
            else:
                self.direction = "None"
            if self.direction != "None":
                self.lastUpdate = round(time.monotonic(), 2)
            time.sleep(0.05)
            while True:
                try:
                    self.twist.count = 32000 # Reset the count for next time.
                    break
                except:
                    time.sleep(0.05)
            if self.isPressed != pressed:
                # When was the last time we were pressed?
                self.pressedChange = round(time.monotonic(), 2)
                self.lastUpdate = round(time.monotonic(), 2)
            self.isPressed = pressed