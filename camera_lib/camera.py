from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder
from libcamera import Transform
import threading
import cam_config

# Our camera setup lives here.

class Camera:
    # A wrapper for the regular camera class
    def __init__(self):
        # Start the camera
        self.camera = Picamera2()
        
        # Are we recording?
        self.recording = False 
        # Video encoder
        self.encoder = H264Encoder(10000000)
        # What's our mode?
        # 0 is Auto
        # 1 is Video
        self._exposure = 0
        self._mode = 0
        self._iso = 0
        self.mode = config.cfg["Settings"].getint("Mode")
        self.exposure = config.cfg["Settings"].getfloat("Exposure")
        self.ISO = config.cfg["Settings"].getint("ISO")
        
        # Our configurations
        self.auto_still = self.camera.create_still_configuration(main={"size": (4056, 3040)},
                                                            lores={"size": (800, 480)}, display="lores",
                                                            transform=Transform(hflip=1, vflip=1),
                                                            raw={}
                                                            )

        self.exp_still = self.camera.create_still_configuration( main={"size": (4056, 3040)},
                                                            lores={"size": (800, 480)}, display="lores",
                                                            transform=Transform(hflip=1, vflip=1),
                                                            raw={},
                                                            controls={"ExposureTime": self.getExposure()}
                                                            )
        
        self.iso_still = self.camera.create_still_configuration( main={"size": (4056, 3040)},
                                                            lores={"size": (800, 480)}, display="lores",
                                                            transform=Transform(hflip=1, vflip=1),
                                                            raw={},
                                                            controls={"AnalogueGain": self.getAnalougeGain()}
                                                            )
        
        self.exp_iso_still = self.camera.create_still_configuration( 
                                                            main={"size": (4056, 3040)},
                                                            lores={"size": (800, 480)}, display="lores",
                                                            transform=Transform(hflip=1, vflip=1),
                                                            raw={},
                                                            controls={"ExposureTime": self.getExposure(),
                                                            "AnalogueGain": self.getAnalougeGain()}
                                                            )

        self.video = self.camera.create_video_configuration(     main={"size": (2048, 1536)},
                                                            lores={"size": (800, 480)}, display="lores",
                                                            transform=Transform(hflip=1, vflip=1)
                                                            )
        # Set ourselves up.
        self.setConfigure()
    
    @property
    def exposure(self):
        return self._exposure
    
    @property
    def mode(self):
        return self._mode
    
    @property
    def ISO(self):
        return self._iso
    
    @exposure.setter
    def exposure(self, exp):
        # Max of 239. Min of 0 (For auto).
        if exp > 239:
            exp = 239.00
        if exp < 0:
            exp = 0
        config.cfg["Settings"]["Exposure"] = str(exp)
        config.save_config()
        self._exposure = exp
        return exp
    
    @ISO.setter
    def ISO(self, iso):
        # Below 100 is not allowed, unless it's 0 for auto
        if iso < 100 and iso != 0:
            iso = 100
        # Max of 1600
        if iso > 1600:
            iso = 1600
        config.cfg["Settings"]["ISO"] = str(iso)
        config.save_config()
        self._iso = iso
        return iso
    
    @mode.setter
    def mode(self, newMode):
        # 0 is still
        # 1 is video
        if newMode < 0:
            newMode = 0
        elif newMode > 1:
            newMode = 1
        else:
            newMode = int(newMode)
        config.cfg["Settings"]["Mode"] = str(newMode)
        config.save_config()
        self._mode = newMode
        return newMode
    
    def getExposure(self):
        # self.exposure is measured in seconds
        # But we need microseconds. A second has one million microseconds
        # No error or mode checking here, it's done elsewhere.
        exposure = self.exposure * 1000000
        return exposure
    
    def getAnalogGain(self):
        # self.ISO is measured in, well. "Effective" ISO.
        # We want this to be a number for AnalougeGain
        # We treat ISO as being 100x the gain.
        gain = ISO / 100.00
        return gain
    
    def setConfig(self):
        # Sets the configuration depending on the mode.
        if mode == 1 and not self.recording: # Video mode. Use our video config.
            # Don't change the config if we're recording
            self.camera.configure(self.video)
        elif mode == 0: # Camera mode.
            if self.exposure > 0 and self.ISO == 0:
                self.camera.configure(self.exp_still)
            elif self.exposure == 0 and self.ISO > 0:
                self.camera_configure(self.iso_still)
            elif self.exposure > 0 and self.ISO > 0:
                self.camera_configure(self.exp_iso_still)
            else:
                self.camera.configure(self.auto_still)
        else:
            pass
    
    def shutter(self):
        # Video stuff. WIP.
        self.setConfig()
        if self.mode == 1 and not self.recording:
            self.recording = True
            self.camera.start_recording(encoder, self.get_video_filename())
        elif self.mode == 1 and self.recording:
            self.recording = False
            self.camera.stop_recording()
        elif self.mode == 0:
            self.recoring = False # Just in case.
            # self.camera.stop_recording() # Will this error?
            # Save the picture
            saver = threading.Thread(target=self.save_image)
    
    def get_video_filename(self):
        base_path = config.cfg["Info"]["VidPath"] + "VID_"
        next_vid = config.cfg["Info"].getint("NextVid")
        filename = base_path + str(next_vid) + ".h264"
        next_vid += 1
        config.cfg["Info"]["NextVid"] = str(next_vid)
        config.save_config()
        return filename
    
    def save_image(self):
        # Saves the still image as a JPEG and/or DNG as requested
        request = self.camera.capture_request()
        base_path = config.cfg["Info"]["ImgPath"] + "IMG_"
        next_image = config.cfg["Info"].getint("NextImg")
        filename = base_path + str(next_image)
        if config.cfg["Settings"].getboolean("JPEG"):
            request.save("main", filename + ".jpg")
        if config.cfg["Settings"].getboolean("DNG"):
            request.save_dng(filename + ".dng")
        request.delete
        next_image += 1
        config.cfg["Info"]["NextImg"] = str(next_image)
        config.save_config()
        return True