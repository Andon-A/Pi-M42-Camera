# TODO list

## General
The following won't be included in this repository:
- [ ] Clean up startup on Raspberry Pi
- [ ] Set up file system correctly
 - [ ] Set up /software folder on Pi partition
 - [ ] Set up /DCIM folder in photos partition
- [ ] Set up Samba and WSDD on Raspberry Pi
- [ ] Set up WSDD as a service
- [ ] Set up main program as a service
- [ ] Set up RTC
- [X] Set up alternate CS pin (Move CS0 to GPIO26/Pin 37)

## Hardware
Hardware is not included in this repository (currently)
- [ ] Design 3d printed knob for mode selector
- [ ] Design 3d printed bottom plate that includes USB-C and USB mounts

## Software
### Controls
These are simply setting up the interfaces, not doing anything with them.
- [ ] Read shutter button
- [ ] Read Encoder button
- [ ] Read Encoder
- [ ] Read Mode Selector
### Camera
These are the program parts that do the things, not necessarily tied in to everything
- [ ] Set up camera profiles (Video, Still, Raw, and Preview)
- [ ] Set up camera preview
- [ ] Set up taking a picture and saving it as Raw and JPG
- [ ] Set up Automatic mode
- [ ] Set up ISO mode (Encoder adjusts ISO)
- [ ] Set up Shutter Mode (Encoder adjusts Shutter speed)
- [ ] Set up ISO and Shutter mode (Encoder does both, short press to swap)
- [ ] Set up  Video Mode
### Hardware Interface
As with camera, the parts that do the things.
- [ ] Set up battery voltage monitoring for charge status
- [ ] Set up internal thermistor for heat status
- [ ] Set up CPU temperature monitoring
### Basic Software
- [ ] Main loop that saves pictures to correct folder
- [ ] Watchdog that detects new software and reboots program
### Moderate Software
- [ ] Overlay over the camera that gives information
- [ ] Camera mode switching
### Complex Software
- [ ] Settings Menu
- [ ] Wifi On and Off toggles in settings menu
- [ ] Option to copy all pictures to plugged in USB
- [ ] Updating settings from plugged in USB
### Bonus Software
These are goals I'm not going to worry too much about initially
- [ ] Incorporate better [color profiles](https://github.com/davidplowman/Colour_Profiles) ([Info](https://github.com/raspberrypi/picamera2/issues/253))
- [ ] On-screen selection of Wifi, inc. Password (On-screen keyboard?!)