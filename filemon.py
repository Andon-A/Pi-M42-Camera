import os
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import configparser

sys.path.append("./camera_lib") # We need to know where things are.

# Our own files.
import system

watch_path = os.getcwd() # What folder we're watching
wait_time = 10 # Seconds since the last event before we do anything
wait_now = 0

cam_service = system.Service("camera") # Our service for the main camera software.
own_service = system.Service("camera_filemon") # Our own watchdog service.

_restartSelf = False
_restartCam = False

# Our updater config contains all the information we need on files.
fileconfig = configparser.ConfigParser(allow_no_value=True)
fileconfig.read("./camera_lib/config/updater.cfg")

start_tries = 0

if cam_service.isRunning:
    print("Camera service found and running.")
else:
    print("Camera service not running.")
    start_tries = 5 # Don't try to start it, it should start itself. Or we don't want it on.
if own_service.isRunning:
    print("Monitor running as a service.")
else:
    print("Monitor not running as a service.")


def isFileWatched(file):
    for path in fileconfig["Monitor"]:
        fpath = watch_path + "/" + path
        if file == fpath:
            return True, fileconfig["Monitor"][path]
    return False, ""


def doRestarts():
    global _restartCam, _restartSelf
    # Restart the camera first, then us. This way we don't accidentally shut ourselves down first.
    if _restartCam:
        if cam_service.isRunning:
            print("Restarting camera.")
            cam_service.restart()
            _restartCam = False
            time.sleep(0.5)
        else:
            print("Camera cannot be restarted as it is not on.")
            _restartCam = False
    if _restartSelf:
        print("Restarting file monitor.")
        own_service.restart()
        exit()

class MonitorFolder(FileSystemEventHandler):
    def on_modified(self, event):
        global _restartCam, _restartSelf
        watch = isFileWatched(event.src_path)
        if watch[0]:
            print("File {0} modified.".format(event.src_path))
            if (watch[1] == "cam" or watch[1] == "both") and not _restartCam:
                print("Camera restart queued")
                _restartCam = True
            if (watch[1] == "self" or watch[1] == "both") and not _restartSelf:
                print("Self restart queued")
                _restartSelf = True
            wait_now = time.monotonic()
        
if __name__ == "__main__":
    src_path = watch_path
    
    event_handler=MonitorFolder()
    observer = Observer()
    observer.schedule(event_handler, path=src_path, recursive=True)
    print("Monitoring started")
    observer.start()
    try:
        while(True):
            time.sleep(1)
            while not cam_service.isRunning and start_tries < 5:
                # Our camera service is down.
                # Give it a little time, then restart it.
                # But don't try too many times.
                time.sleep(3)
                cam_service.start()
                start_tries += 1
            if start_tries > 0 and cam_service.isRunning:
                start_tries = 0
            if (_restartCam or _restartSelf) and time.monotonic() > wait_now + wait_time:
                doRestarts()
           
    except KeyboardInterrupt:
            observer.stop()
            observer.join()