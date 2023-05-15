# This handles our controls. That is, it tells us what our controls are doing.

# Our GPIO setup
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

# Out I2C setup. We use Sparkfun's qwiic system.
import qwiic_twist

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

class encoder:

    def __init__(self, int_pin, callback, color=(0,0,0), timeout=100):
        self.int_pin = int_pin
        self.callback = callback  # We return pressed and count
        self._color = (0,0,0)     # Our LED color. Default to nothing, it's set later.
        self._timeout = -1        # How long we wait (ms) after the encoder has stopped moving to ping.
                                  # Again, default to a bad value, and we'll be set later.
        self.enabled = False      # Has our encoder properly enabled?
         
        # We want to set up our interrupt pin as a pullup.
        GPIO.setup(self.int_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # We also only care when it goes down.
        GPIO.add_event_detect(self.int_pin, GPIO.FALLING, callback=self.detectInput)
        # Now set up the twist.
        self.twist = qwiic_twist.QwiicTwist()
        if self.twist.connected == False:
            print("Encoder not detected.")
        else:
            self.twist.begin()
            self.enabled = True
            self.color = color # The RGB color of the LED
            self.timeout = timeout
            self.count = 0
            print("Encoder initailized")
        
    @property
    def pressed(self):
        # Returns our current pressed state.
        if self.enabled:
            return self.twist.pressed
        else:
            return false
    
    @property
    def count(self):
        if self.enabled:
            return self.twist.count
        else:
            return 0
    
    @count.setter
    def count(self, count):
        if self.enabled:
            self.twist.count = count
            return self.twist.count
        else:
            return 0
        
    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self, color):
        # Sets the color. Color is an RGP tuple
        if self.enabled:
            self.twist.set_color(color[0], color[1], color[2])
            self._color = color
    
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
            self.twist.set_int_timeout(ms)
            self._timeout = ms
    
    def clear_interrupts(self):
        self.twist.clear_interrupts()
    
    def detectInput(self, channel):
        print("Detect")
        # This is triggered when we detect an interrupt.
        if self.enabled:
            # Only do the callback if we have a callback set and we're enabled.
            self.callback(self.pressed, self.count)
            self.twist.clear_interrupts()
        
    