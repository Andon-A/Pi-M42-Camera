from picamera2 import Picamera2, Preview
from libcamera import Transform
import time

# Screen resolution: 800 x 480

camera = Picamera2()
# default config:
camera_default = camera.create_preview_configuration()

# Transformed config:
camera_transform = camera.create_preview_configuration(transform=Transform(hflip=1, vflip=1)

camera_still = camera.create_still_configuration(lores={"size": (800, 480)}, display="lores", transform=Transform(hflip=1, vflip=1)

camera.configure(camera_default)
camera.start_preview(Preview.DRM, x=0, y=0, width=800, height=480)
camera.start()

time.sleep(10)

camera.stop_preview()
camera.stop()

time.sleep(2)

camera.configure(camera_transform)
camera.start_preview(Preview.DRM, x=0, y=0, width=800, height=480)
camera.start()

time.sleep(10)

camera.stop_preview()
camera.stop()

time.sleep(2)

camera.configure(camera_still)
camera.start_preview(Preview.DRM, x=0, y=0, width=800, height=480)
camera.start()

time.sleep(10)

camera.stop_preview()
camera.stop()


exit()