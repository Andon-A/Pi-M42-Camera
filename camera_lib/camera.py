# Camera imports
from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder
from libcamera import Transform

# Camera related imports
import cv2
import numpy

# General imports
import threading
import cam_config
import os

# Our camera setup lives here.

class Camera:
    # A wrapper for the regular camera class
    def __init__(self):
        global cam_config
        # Start the camera
        self.camera = Picamera2()
        # Are we recording?
        self._recording = False 
        # Video encoder
        self.encoder = H264Encoder(10000000)
        # What's our mode?
        # 0 is Auto
        # 1 is Video
        self._exposure = 0 # In seconds. 0 for auto.
        self._mode = 0 # 0 for still, 1 for video.
        self._iso = 0 # 0 for still, then typical 100/200/400/800/1600 settings
        self._currentCFG = None
        self._needsConfig = False
        self.mode = cam_config.cfg["Settings"].getint("Mode")
        self._exp_raw = 0
        self._iso_raw = 0
        self._exp_str = "Auto"
        self._iso_str = "Auto"
        self.Exposure = cam_config.cfg["Settings"]["Exposure"]
        self.ISO = cam_config.cfg["Settings"]["ISO"]
        self._lastSavedImg = None
        self.isSaving = False
        
        # Our configurations
        self.still = self.camera.create_still_configuration(main={"size": (4056, 3040)},
                                                            lores={"size": (800, 480)}, display="lores",
                                                            raw={}, buffer_count=2,
                                                            )
        self.video = self.camera.create_video_configuration(
                                                            main={"size": (2048, 1536)},
                                                            lores={"size": (800, 480)}, display="lores",
                                                            buffer_count=2
                                                            )
    
    @property
    def exposure(self):
        return (self._exp_str, self._exp_raw)
    
    @property
    def mode(self):
        if self._mode == 0:
            if self.exposure[1] != 0 and self.ISO[1] != 0:
                return "Manual Still", self._mode
            elif self.exposure[1] == 0 and self.ISO[1] != 0:
                return "ISO-Select Still", self._mode
            elif self.exposure[1] != 0 and self.ISO[1] == 0:
                return "Exposure-Select Still", self._mode
            else:
                return "Auto Still", self._mode
        elif self._mode == 1:
            return "Video", self._mode
    
    @property
    def ISO(self):
        return (self._iso_str, self._iso_raw)
    
    @exposure.setter
    def exposure(self, exp):
        self._exp_str = exp # Set the string.
        # Now parse it into into a number.
        if exp.lower() == 'auto':
            # Our functions want a number, so we treat "0" as auto.
            self._exp_raw = 0
        else:
            if exp[-1:] == '"':
                # We have an exposure denoted in seconds. This is an easy convert.
                self._exp_raw = float(exp[:-1])
            else:
                # We have an exposure denoted by division, IE, 1/XXXX
                self._exp_raw = 1.0 / float(exp[2:])
        # Make sure we have good data
        if self._exp_raw > 239:
            self._exp_raw = 239
            self._exp_str = '239"'
        elif self._exp_raw < 0:
            self._exp_raw = 0
            self._exp_str = 'Auto'
        self._needsConfig = True # Make sure we reconfigure the camera.
        cam_config.cfg["Settings"]["Exposure"] = self._exp_str
        return self.exposure
    
    @ISO.setter
    def ISO(self, iso):
        self._iso_str = str(iso)
        # We're passed a string which is a number or 'Auto'
        if type(iso) == str:
            if iso.lower() == 'auto':
                self._iso_raw = 0
        else:
            iso = int(iso)
            if iso < 0:
                # Treat negative as auto
                self._iso_str = 'Auto'
                self._iso_raw = 0
            elif iso < 100:
                self._iso_raw = 100
                self._iso_str = "100"
            elif iso > 1600:
                self._iso_raw = 1600
                self._iso_str = "1600"
            else:
                self._iso_raw = iso
        self._needsConfig = True
        cam_config.cfg["Settings"]["ISO"] = self._iso_str
        return self.ISO
    
    @mode.setter
    def mode(self, newMode):
        # Sets the mode of the camera.
        if type(newMode) is str:
            if newMode.lower() == "stil":
                newMode = 0 # 0 is still. Still sub-modes are determined by exposure and ISO
            elif newMode.lower() == "video":
                newMode = 1 # 1 is video
            else:
                # Just in case.
                newMode = 0
        if type(newMode) != int:
            try:
                # If we have a float or other int-able thing.
                newMode = int(newMode)
            except:
                # Guess not. Default to still.
                newMode = 0
        if newMode < 0:
            newMode = 0
        elif newMode > 1:
            newMode = 1
        else:
            newMode = int(newMode)
        cam_config.cfg["Settings"]["Mode"] = str(newMode)
        self._mode = newMode
        self._needsConfig = True # Make sure we reconfigure the camera if this changes.
        return newMode
    
    def startCam(self):
        # We need to set up our preview
        # And also start the camera.
        self.camera.configure(self.getConfig())
        self._currentCFG = self.getConfig()
        self.camera.start_preview(Preview.DRM, width=800, height=480, transform=Transform(hflip=1, vflip=1))
        self.camera.start()
        return True
    
    def stopCam(self):
        # Stop the camera
        # And the preview.
        self.camera.stop_preview()
        self.camera.stop()
    
    def setControls(self):
        # Sets the camera's exposure and ISO.
        if self.exposure[0] != "Auto" and self.ISO[0] != "Auto":
            # Manual
            self.camera.set_controls({"ExposureTime": self.getExposure(), "AnalogueGain": self.getAnalogueGain()})
        elif self.exposure[0] != "Auto" and self.ISO[0] == "Auto":
            # Auto ISO, manual exposure
            self.camera.set_controls({"ExposureTime": self.getExposure(), "AwbEnable": True})
        elif self.exposure[0] == "Auto" and self.ISO[0] != "Auto":
            # Auto Exposure, manual ISO
            self.camera.set_controls({"AnalogueGain": self.getAnalogueGain(), "AeEnable":True})
        else:
            # Full auto.
            self.camera.set_controls({"AeEnable":True, "AwbEnable": True})
        # This won't re-start the stream.
    
    def reconfigure(self):
        # Stops the camera, reconfigures, then restarts the preview.
        # Only applies if the configuration is actually different.
        new_cfg = self.getConfig()
        if ((self._currentCFG != new_cfg) or self._needsConfig) and not self._recording:
            self.camera.stop()
            self.camera.configure(new_cfg)
            self.setControls() # Set our exposure and ISO
            self._currentCFG = new_cfg
            self.camera.stop_preview()
            self.camera.start_preview(Preview.DRM, width=800, height=480, transform=Transform(hflip=1, vflip=1))
            self.camera.start()
            self._needsConfig = False
    
    def getExposure(self):
        # self.exposure is measured in seconds
        # But we need microseconds. A second has one million microseconds
        # No error or mode checking here, it's done elsewhere.
        exposure = int(round(self.exposure[1] * 1000000))
        return exposure
    
    def getAnalogueGain(self):
        # self.ISO is measured in, well. "Effective" ISO.
        # We want this to be a number for AnalogueGain
        # We treat ISO as being 100x the gain.
        gain = self.ISO[1] / 100.00
        return gain
        
    def getConfig(self, mode=None):
        # Returns the correct configuration for the mode.
        if mode is None:
            mode = self.mode[1]
        if mode == 1:
            # Video mode.
            return self.video
        elif mode == 0:
            return self.still
        else:
            return None
    
    def shutter(self):
        # Video stuff. WIP.
        #self.reconfigure()
        print("Shutter Pressed. Mode: {0}".format(self.mode))
        if self.mode[1] == 1 and not self._recording:
            self._recording = True
            self.camera.start_recording(encoder, self.get_video_filename())
            print("Starting Video.")
        elif self.mode[1] == 1 and self._recording:
            self._recording = False
            self.camera.stop_recording()
            print("Stopping Video.")
        elif self.mode[1] == 0:
            if self._recording:
                # Stop the recording.
                self.camera.stop_recording()
                self._recoring = False
                self.reconfigure()
            # self.camera.stop_recording() # Will this error?
            # Save the picture
            print("Starting picture save.")
            saver = threading.Thread(target=self.save_image)
            saver.start()
    
    # Our method for determining the next image or video.
    # We create a file in the main folder with the extension .icount or .vcount
    # And increment that.
    # This way we don't have to worry about writing the config file a million times,
    # Or potentially corrupting it. Again.
    
    def getCount(self):
        ext = ""
        if self.mode[1] == 0: # Still
            ext = ".icount"
        elif self.mode[1] == 1:
            ext = ".vcount"
        else:
            return -1
        # Get our files.
        flist = os.listdir()
        file = ""
        # And find our specific file.
        for f in flist:
            if ext == f[-7:]:
                file = f # Keep looping. We want the largest number one, if it exists.
        if file != "":
            count = int(file[:-7])
        else:
            count = 0 # We currently have zero.
        return count
        
    def increaseCount(self):
        count = self.getCount() # Determine what our count is.
        ext = ""
        if self.mode[1] == 0: # Still
            ext = ".icount"
        elif self.mode[1] == 1:
            ext = ".vcount"
        else:
            return False
        # First, make our new file.
        with open(str(count + 1) + ext, 'w') as newfile:
            pass
        # Now, remove the old one.
        oldfile = str(count) + ext
        if os.path.isfile(oldfile):
            os.remove(str(oldfile))
        return True
    
    def get_video_filename(self):
        base_path = cam_config.cfg["Info"]["VidPath"]
        if not os.path.isdir(base_path):
            os.makedirs(base_path)
        next_vid = self.getCount() + 1
        # Our pad keeps us at a minimum of 4 digits.
        # If we go to 10k videos (Or images, that works the same)
        # Then the number will expand just fine.
        pad = ""
        if next_vid < 10:
            pad = "000"
        elif next_vid < 100:
            pad = "00"
        elif next_vid < 1000:
            pad = "0"
        filename = base_path + "VID_" + pad + str(next_vid) + ".h264"
        self.increaseCount()
        return filename
    
    def save_image(self):
        # Saves the still image as a JPEG and/or DNG as requested
        self.isSaving = True
        request = self.camera.capture_request(flush=True)
        base_path = cam_config.cfg["Info"]["ImgPath"]
        if not os.path.isdir(base_path):
            os.makedirs(base_path)
        next_image = self.getCount() + 1
        pad = ""
        if next_image < 10:
            pad = "000"
        elif next_image < 100:
            pad = "00"
        elif next_image < 1000:
            pad = "0"
        filename = base_path + "IMG_" + pad + str(next_image)
        if filename != self._lastSavedImg:
            self._lastSavedImg = filename
            self.increaseCount()
            if cam_config.cfg["Settings"].getboolean("JPEG"):
                print("Saving {0}.jpg".format(filename))
                request.save("main", filename + ".jpg")
            if cam_config.cfg["Settings"].getboolean("DNG"):
                print("Saving {0}.dng".format(filename))
                request.save_dng(filename + ".dng")
        else:
            print("Already saving that image.")
        request.release()
        print("Released")
        self.isSaving = False
        return True
    
    def write_overlay(self, overlay):
        self.camera.set_overlay(overlay)
        return True
    
    def clear_overlay(self):
        # Writes an empty array as the overlay
        self.camera.set_overlay(numpy.zeros((800, 480, 4), dtype=numpy.uint8))
        return True
        
class Overlay:
    # A class to run our overlay.
    def __init__(self, camera, lineheight=18, textOrigin=(0,0), thickness=2,
                        bg=None):
        self._linePadding = 0.4     # We want 30% of our text height to be used as padding.
                                    # 12 lineheight = 10 text, 2 padding
                                    # Padding is added below the text.
        self._originX = textOrigin[0]   # X pos for the start of all lines
        self._originY = textOrigin[1]   # Y pos for the start of the first line.
        self._linesWritten = 0      # Number of lines we have currently written
        self._scale = 0             # OpenCV uses text scale instead of pixels, so we convert
        self._lineHeight = 0
        self._font = cv2.FONT_HERSHEY_PLAIN
        self._camera = camera
        self.lineHeight = lineheight
        self._thickness = thickness
        self._bg = bg               # (0, 0, 0) RGB style
        self._lines = []            # We'll shove our lines of text into here.
        self._otherTxt = []         # other text goes here.

    # Get and set our origin
    @property
    def origin(self):
        return (self._originX, self.originY)
    
    @origin.setter
    def origin(self, pos):
        self._originX = pos[0]
        self._originY = pos[1]
        return self.origin

    @property
    def padding(self):
        return self._linePadding
    
    @padding.setter
    def padding(self, pad):
        self._linePadding = pad
        return self._linePadding
    
    @property
    def lineHeight(self):
        return self._lineHeight

    @lineHeight.setter
    def lineHeight(self, lineheight):
        # Sets our text scale based on line height.
        # Calculate the text size, in pixels, based on line height.
        # Round to nearest pixel.
        textHeight = float(round(lineheight / (1 + self._linePadding)))
        # Get our default text height based off of a scale of 1.0 and thickness of 2
        default = cv2.getTextSize("Test", self._font, 1.0, 2)[0][1]
        self._scale = textHeight / default # We could round this, but nobody will see it.
        self._lineHeight = lineheight
        return self._lineHeight
    
    def makeOverlay(self):
        # Create a blank overlay.
        base = numpy.zeros((800, 480, 4), dtype=numpy.uint8)
        if self._bg is not None:
            # We want a background.
            bgcolor = (self._bg[2], self._bg[1], self._bg[0]) # OpenCV takes BGR
            cv2.rectangle(base, (0,0), (800, 480), bgcolor, thickness=-1)
        self.writeLines(base)
        base = cv2.flip(base, -1) # Rotate 180 degrees
        return base        
        
    def addLine(self, text, color=(255,255,255,255), bold=False, linenum = -1):
        # Add another line by default.
        if linenum < 0:
            linenum = len(self._lines) # Add another line.
        # Make sure we have enough lines in the list.
        while linenum >= len(self._lines):
            self._lines.append(((255,255,255,255),""))
        # Now write the line.
        thick = self._thickness
        if bold:
            thick = self._thickness * 2
        self._lines[linenum] = (color, thick, text)
        return True
    
    def addTextAtLoc(self, text, loc, color=(255,255,255,255), bold=False, scale=None):
        # Adds a line at a specific X, Y location.
        thick = self._thickness
        if bold:
            thick = self._thickness * 2
        if scale is None:
            scale = self._scale
        self._otherTxt.append((color, thick, text, loc, scale))
        return True
    
    def clearLines(self):
        self._lines = []
        self._otherTxt = []
        return True
    
    def showOverlay(self):
        # Rebuilds the overlay, then shows it on the camera.
        overlay = self.makeOverlay()
        #self._camera.clear_overlay()
        self._camera.write_overlay(overlay)
        return True
            
    
    def writeLines(self, overlay):
        # Write each of our lines
        # Start with standard lines.
        for idx in range(0, len(self._lines)):
            line = self._lines[idx]
            text = line[2]
            if text != "":
                # Only proceed with non-empty lines.
                color = line[0]
                thickness = line[1]
                xpos = self._originX
                ypos = self._originY + (idx * self.lineHeight)
                cv2.putText(overlay, text, (xpos, ypos), self._font, self._scale, color, thickness)
        # And our location-specified lines.
        for line in self._otherTxt:
            text = line[2]
            color = line[0]
            thickness = line[1]
            pos = line[3]
            scale = line[4]
            cv2.putText(overlay, text, pos, self._font, scale, color, thickness)
        return True
