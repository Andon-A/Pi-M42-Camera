# Pi M42 Camera
 A mirrorless camera powered by the Raspberry Pi 4 and the Pi HQ Camera. Written in Python 3.

The camera uses the classic M42 screw mount, of which lenses for are plentiful and largely inexpensive. I chose this mount because I fit both a focal reducer and a 39mm filter mount behind the lens mount. This means that I only have to have one IR filter to take IR images, and so on.

Without any other fancy things going on, the HQ camera has a crop factor of about 5.5 - This means that, say, a 50mm lens with this sensor is the *equivalent* field of view as a 275mm lens on a full frame camera. And what does this mean, you non-photography-nerd people ask? It means that instead of being a wide angle shot, it's a very close in zoom shot.

I was able to mount the focal reducer at a point where it provides *about* a 0.73x multiplier to the field of view. This pulls the crop factor down to 4x, which while still pretty zoomy, is a significant amount less so. That theoretical 50mm lens is now effectively a 200mm lens. It comes with image quality tradeoffs, but it's worth it and if I want better image quality I can remove it. This crop factor can be reduced further by wide angle converters that can be put on the end of the lens, at the further cost of image quality.

### Hardware
The camera uses some custom hardware:
- A power board that converts battery input into 5v power for the pi
- A [PCF8523](https://www.adafruit.com/product/3295) real-time clock
- An interface board that connects each of the above to the Pi

It also uses some off-the-shelf hardware:
- A Raspberry Pi 4 - I'm using a 4gb version, but I expect it would work just as well on a 2gb version.
- A Raspberry Pi HQ Camera. I took off the standard mount, as I was providing my own.
- [The smallest DSI screen I could get my hands on.](https://www.amazon.com/gp/product/B08634Y16L)
- A [tiny USB3 drive](https://www.amazon.com/gp/product/B07XHYVN62) is used instead of an SD card for accessibility purposes
- A [Sparkfun Qwiic Twist rotary encoder](https://www.sparkfun.com/products/15083)

### Software
Due to the above hardware, the following are required:
- [Adafruit's Blinka](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux)
- Adafruit's [MCP3xxx library](https://github.com/adafruit/Adafruit_CircuitPython_MCP3xxx)
- Sparkfun's [Qwiic Twist library](https://github.com/sparkfun/Qwiic_Twist_Py)
- [Setup for the above RTC](https://learn.adafruit.com/adding-a-real-time-clock-to-raspberry-pi)

The following are used, but not necessary for the camera functions:
- Samba and [WSDD](https://github.com/christgau/wsdd) for easy access to the camera's pictures

I've also done the following:
- Cleaned up startup for a faster boot. I used [this tutorial](https://singleboardbytes.com/637/how-to-fast-boot-raspberry-pi.htm) for some cleaning. I didn't go to extreme, but every bit helps.
- Set the main python file as a service. I followed [this tutorial](https://www.dexterindustries.com/howto/run-a-program-on-your-raspberry-pi-at-startup/) and used the systemd method.
- Set the software updater [watchdog](https://stackoverflow.com/questions/182197/how-do-i-watch-a-file-for-changes) as a service as well

### Setup
I'm still writing the code, so there's nothing here.
