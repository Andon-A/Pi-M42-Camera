# Camera systems controller.
# Handles various system pieces, including some hardware.

import os # We need OS to control services
#from rpi_backlight import Backlight # And our backlight
import RPi.GPIO as GPIO # We'll need GPIO for our ADC and thermistor
GPIO.setmode(GPIO.BCM)

from gpiozero import CPUTemperature

# We want our board definitions
import board

# MCP3008 ADC. Used to read thermistor and battery voltage
# TODO: Update to new ADC
import math
import adafruit_pcf8591.pcf8591 as PCF
from adafruit_pcf8591.analog_in import AnalogIn
from adafruit_pcf8591.analog_out import AnalogOut

# Our services to handle.
class Service:
    def __init__(self, serv):
        self.name = serv
        self.status = self.isRunning
        
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
        if self.isRunning:
            return True
        else:
            os.system('systemctl start --quiet %s.service' % self.name)
            return self.isRunning
        
    def stop(self):
        # Makes sure the service is stopped if it is running.
        if not self.isRunning:
            return False
        else:
            os.system('systemctl stop --quiet %s.service' % self.name)
            return self.isRunning
    
    def restart(self):
        # Restarts the service.
        os.system('systemctl restart --quiet %s.service' % self.name)
        return self.isRunning

class ADC:
    # A simple class for the ADC.
    def __init__(self, i2c=board.I2C()):
        self.pcf = PCF.PCF8591(i2c)
        self.Pin0 = AnalogIn(self.pcf, PCF.A0)
        self.Pin1 = AnalogIn(self.pcf, PCF.A1)
        self.Pin2 = AnalogIn(self.pcf, PCF.A2)
        self.Pin3 = AnalogIn(self.pcf, PCF.A3)
        self.DAC  = AnalogOut(self.pcf, PCF.OUT)     

class Battery:
    # Basic battery voltage monitoring.
    def __init__(self, pin, cells=2):
        self._pin = pin
        self._cells = cells # Number of cells the battery pack has.
        # TODO: Low and high voltage levels
        # Maybe: Add a voltage curve to monitor
        # Maybe: Add a few voltage points (10%, 25%, 50%, 75%, 100%)
        self.yel_pct = 0.35 # Indicator should be yellow at 35% battery
        self.red_pct = 0.25 # Indicator should be red at 25% battery.
        # We turn the system off at a certain voltage because percent doesn't read that finely.
        self.cutoff_voltage = 3.71 * self._cells # About 15%
        self.high_voltage = 0.00
    
    @property
    def voltage(self):
        # We have to run the input voltage through a divider
        v = self._pin.voltage
        # Divider is 430 ohm (R1) and 220 ohm (R2)
        # So math says Real Voltage is 2.955x Input
        v = round(v * 2.955, 5)
        return v
    
    @property
    def chargePct(self):
        # Returns the percentage of the battery's value.
        # These use info from: https://blog.ampow.com/lipo-voltage-chart/
        # We use the next level to determine. IE, > 4.15 is 100%, > 4.11 = 95%, etc
        cells = self._cells
        if self.voltage > (4.20 * cells):
            print("Voltage higher than expected for number of cells.")
            return 1.00
        elif self.voltage > (4.15 * cells):
            return 1.00
        elif self.voltage > (4.11 * cells):
            return 0.95
        elif self.voltage > (4.08 * cells):
            return 0.90
        elif self.voltage > (4.02 * cells):
            return 0.85
        elif self.voltage > (3.98 * cells):
            return 0.80
        elif self.voltage > (3.95 * cells):
            return 0.75
        elif self.voltage > (3.91 * cells):
            return 0.70
        elif self.voltage > (3.87 * cells):
            return 0.65
        elif self.voltage > (3.85 * cells):
            return 0.60
        elif self.voltage > (3.84 * cells):
            return 0.55
        elif self.voltage > (3.82 * cells):
            return 0.50
        elif self.voltage > (3.80 * cells):
            return 0.45
        elif self.voltage > (3.79 * cells):
            return 0.40
        elif self.voltage > (3.77 * cells):
            return 0.35
        elif self.voltage > (3.75 * cells):
            return 0.30
        elif self.voltage > (3.73 * cells):
            return 0.25
        elif self.voltage > (3.71 * cells):
            return 0.20
        elif self.voltage > (3.69 * cells):
            return 0.15
        elif self.voltage > (3.61 * cells):
            return 0.10
        elif self.voltage > (3.27 * cells):
            return 0.05
        elif self.voltage <= (3.27 * cells):
            return 0.00

class CPU:
    # Basic CPU temperature monitoring
    def __init__(self):
        self.cpu = CPUTemperature()
    
    def get_temp(self, type="C"):
        # Converts the temperature to the chosen units.
        temp = self.cpu.temperature
        if type == "F":
            # Fahrenheit
            temp = ((temp * (9/5)) + 32)
            return temp
        elif type == "K":
            # Kelvin. Easy.
            temp = temp + 273.15
        # Default to Celcius (No conversion required) and return the value.
        return temp
    
    @property
    def temp_F(self):
        return self.get_temp("F")
    
    @property
    def temp_C(self):
        return self.get_temp("C")
    
    @property
    def temp_K(self):
        return self.get_temp("K")