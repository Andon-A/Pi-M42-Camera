import os
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import configparser

sys.path.append("./camera_lib") # We need to know where things are.

# Our own files.
#from system import Service

watch_path = "/software" # What folder we're watching
self_path = "/software/filemon.py"
wait_time = 10 # Seconds since the last event before we do anything
exclude = ["config.cfg"]

#cam_service = system.Service("camera") # Our service for the main camera software.
#own_service = system.Service("camera_filemon") # Our own watchdog service.

_queue = [] # Our queue of items
_restartSelf = False
_restartCam = False

# Our updater config contains all the information we need on files.
fileconfig = configparser.ConfigParser(allow_no_value=True)
fileconfig.read("./camera_lib/config/updater.cfg")


def addToQueue(path):
    # Add an item to the queue
    if path not in _queue:
        _queue.append(path)
        
def processQueue():
    # Checks the queue to see what services we need to restart.
    if self_path in _queue:
        # We've been updated, so we need to restart.
        _restartSelf = True
        pass 
    for file in fileconfig["Files"]:
        if file in _queue and file != self_path:
            if file[file.rfind("/")+1:] not in exclude and not os.path.isdir (file):
                # We don't want to force a restart just because of a folder change.
                # Also make sure we're not restarting on one of our excluded files.
                _restartCam = True
        if file in _queue and file == "/software/camera_lib/system.py":
            # We depend on this one.
            _restartSelf = True
    #doRestarts()

def doRestarts():
    # Restart the camera first, then us. This way we don't accidentally shut ourselves down first.
    if _restartCam:
        if cam.isRunning:
            cam_service.restart()
    if _restartSelf:
        own_service.restart()       

class MonitorFolder(FileSystemEventHandler):
    def on_modified(self, event):
        print("File {0} modified".format(event.src_path))
        addToQueue(event.src_path)
        
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
           
    except KeyboardInterrupt:
            observer.stop()
            observer.join()