# Camera systems controller.
# Handles various system pieces, including some hardware.

import os # We need OS to control services
import serial
import time

from gpiozero import CPUTemperature

# We want our board definitions
#import board

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

class Battery:
    # Uses the RPi Battery Backup information
    # Based off of https://github.com/rcdrones/UPSPACK_V3/blob/master/README_en.md
    # Example return string: 
    # '$ SmartUPS V3.2P,VIN NG,BATCAP 39,Vout 5250 $'
    # This is a simple serial connection.
    def __init__(self):
        self.ser = serial.Serial("/dev/ttyAMA0", 9600) # Our battery serial port.
        self.cap = 0
        self.Vout = 0
        self.charging = False
        self.lastUpdate = 0
        
    def _getLastSerialData(self):
    # Grabs the latest serial data.
        data = self.ser.read(self.ser.inWaiting())
        data = data.decode('ascii','ignore').split("\n")
        if len(data) >= 2: # Always ignore the last one, since it is likely imcomplete.
            data = data[-2]
        else:
            data = data[0] # Unless it's the only one we have.
        return data
    
    def updateInfo(self):
        info = self._getLastSerialData()
        info = info[2:-2] # Trim the $s
        info = info.split(",") # Split it into it's components.
        for comp in info:
            # check our components.
            if "Vin" in comp:
                # Are we charging?
                if "NG" in comp:
                    self.charging = False
                else:
                    self.charging = True
            if "BATCAP" in comp:
                self.cap = int(comp.split(" ")[1])
            if "Vout" in comp:
                self.Vout = float(comp.split(" ")[1])/1000.00
        self.lastUpdate = round(time.monotonic(), 2)

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