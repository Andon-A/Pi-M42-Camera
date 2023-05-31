# TODO list

## General
The following won't be included in this repository:
- [ ] Clean up startup on Raspberry Pi
- [X] Set up file system correctly
 - [X] Set up /software folder on Pi
 - [X] Set up /photos
 - [X] Set up /Images folder in photos
 - [X] Set up /Videos folder in photos
- [ ] Set up Samba and WSDD on Raspberry Pi
- [ ] Set up WSDD as a service
- [ ] Set up main program as a service
- [ ] Set up RTC

## Hardware
Hardware is not included in this repository (currently)
- [X] Design 3d printed encoder mount
- [X] Design 3d printed top plate to hold USB port
- [X] Adjust sensor position for better focus (Sensor needs to go forwards)

## Software
### Controls
These are simply setting up the interfaces, not doing anything with them.
- [X] Read shutter button
- [X] Read Encoder
### Camera
These are the program parts that do the things, not necessarily tied in to everything
- [X] Set up default camera profiles (Video and Still)
- [X] Set up camera methods to control modes
- [X] Set up camera preview
- [X] Set up taking a picture and saving it as Raw and JPG
- [X] Set up Automatic mode
- [X] Set up ISO mode (Encoder adjusts ISO)
- [X] Set up Shutter Mode (Encoder adjusts Shutter speed)
- [X] Set up ISO and Shutter mode (Encoder does both, short press to swap)
- [X] Set up  Video Mode
### Hardware Interface
As with camera, the parts that do the things, not the actual doing of things.
- [X] Set up battery voltage monitoring for charge status
- [X] Set up CPU temperature monitoring
### Basic Software
- [ ] Main loop that saves pictures to correct folder
- [ ] Watchdog that detects new software and reboots program
### Moderate Software
- [ ] Overlay over the camera that gives information
- [ ] Camera mode switching (Overlay required)
- [ ] Add logging.
### Complex Software
- [ ] Settings Menu
- [ ] Wifi On and Off toggles in settings menu
- [ ] Option to copy all pictures to plugged in USB
- [ ] Updating settings from plugged in USB
### Bonus Software
These are goals I'm not going to worry too much about initially
- [ ] Incorporate better [color profiles](https://github.com/davidplowman/Colour_Profiles) ([Info](https://github.com/raspberrypi/picamera2/issues/253))
- [ ] On-screen selection of Wifi, inc. Password (On-screen keyboard?!)
- [ ] Battery percentage monitoring (Curve)
- [ ] Battery percentage monitoring (Chunks)