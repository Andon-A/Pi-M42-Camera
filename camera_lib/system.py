# Camera systems controller.
# Handles various system pieces, including some hardware.

import os # We need OS to control services
#from rpi_backlight import Backlight # And our backlight
import RPi.GPIO as GPIO # We'll need GPIO for our ADC and thermistor
GPIO.setmode(GPIO.BCM)

# We want our board definitions
import board
import digitalio

# MCP3008 ADC. Used to read thermistor and battery voltage
from adafruit_mcp3xxx.mcp3008  as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

# set up i3c and spi
# The current SPI CE0 pin has been changed to GPIO26/Pin 37
# A future hardware update should address this.
i2c = board.I2C()
spi = board.SPI()

# Set up our backlight
#backlight = Backlight()
#backlight.fade_duration = 0
#backlight.brightness = 12 # 0 to 100. 12% is a decent brightness in most situations.

# Our services to handle.
class Service:
    def __init__(self, serv):
        self.name = serv
        self.status = self.IsRunning()
        
    @property
    def isRunning(self):
        # Returns the status of the service.
        status = os.system('systemctl is-active --quiet %s.service' % self.name)
        if status == 0:
            return True
        else:
            return False
    
    def start(self):
        # Makes sure the service is started if it isn't running already.
        if self.IsRunning:
            return True
        else:
            os.system('systemctl start --quiet %s.service' % self.name)
            return self.IsRunning
        
    def stop(self):
        # Makes sure the service is stopped if it is running.
        if not self.IsRunning:
            return False
        else:
            os.system('systemctl stop --quiet %s.service' % self.name)
            return self.IsRunning
    
    def restart(self):
        # Restarts the service.
        os.system('systemctl restart --quiet %s.service' % self.name)
        return self.IsRunning

class ADC:
    # A simple class for the ADC.
    def __init__(self, spi, cs=board.CE0):
        self.cs = digitalio.DigitalInOut(cs) # Set up our chip select pin
        self.ADC = MCP.MCP3008(spi, self.cs) # Set ourselves up
        # Pins 0 through 7. We only use 0 and 2, but the others are available.
        self.Pin0 = AnalogIn(self.ADC, MCP.P0)
        self.Pin1 = AnalogIn(self.ADC, MCP.P1) # Batt thermistor. Doesn't physically exist.
        self.Pin2 = AnalogIn(self.ADC, MCP.P2)
        self.Pin3 = AnalogIn(self.ADC, MCP.P3) # 3 through 7 are avaiable to be soldered to.
        self.Pin4 = AnalogIn(self.ADC, MCP.P4)
        self.Pin5 = AnalogIn(self.ADC, MCP.P5)
        self.Pin6 = AnalogIn(self.ADC, MCP.P6)
        self.Pin7 = AnalogIn(self.ADC, MCP.P7)
        
class Thermistor:
    def __init__(self, pin, Res=10000.0, Ro=10000.0, To=25.0, Beta=3950.0):
        self.pin = pin # Which pin of the ADC we're connected to.
        self.Res = Res # The resistance of the resistor that's connected for our use.
        self.Ro = Ro # The resistance of this thermistor at normal temperature value
        self.To = To # The above mentioned normal temperature value
        self.Beta = Beta # The beta coefficient value for the thermistor.
    
    def steinhart_temperature_C(self):
        # This is from the adafruit learn guide: https://learn.adafruit.com/thermistor/circuitpython
        # It turns raw information into temperature (in C)
        steinhart = math.log(self.get_R() / self.Ro) / self.beta      # log(R/Ro) / beta
        steinhart += 1.0 / (self.To + 273.15)         # log(R/Ro) / beta + 1/To
        steinhart = (1.0 / steinhart) - 273.15   # Invert, convert to C
        return steinhart    
    
    def get_R(self):
        # Gets the current resistance of the thermistor.
        R = self.Res / (65525/self.pin.value - 1)
        return R
        
    def get_temp(self, type="C"):
        # Returns the current temperature in the measurement specified.
        temp = self.steinhart_temperature_c()
        if type == "F":
            # Fahrenheit
            temp = ((temp * (9/5)) + 32)
            return temp
        elif type == "K":
            # Kelvin. Easy.
            temp = temp + 273.15
        # Default to Celcius (No conversion required) and return the value.
        return temp