#!/usr/bin/python
"""
    Starting for usage at the computer
    Do not delete the except Typer error. GPS data error, added when include GPS
"""
import time
import math
import sys
import signal
import inspect

from core.bebop import *
drone=Bebop()

dX = 2 # 2 mts Forward
dY = 0
dZ = 0
dPsi = (math.pi/2) #90 degrees rotation

def main():
    signal.signal(signal.SIGINT, signal_handler)
    try:
        drone.takeoff()
        time.sleep(2)
        drone.moveBy( dX, dY, dZ, dPsi)
        time.sleep(3)
        drone.hover()
        drone.land()
        sys.exit(0)
    except (TypeError):
        pass

def signal_handler(signal, frame):
    drone.hover()
    print('You pressed Ctrl+C!')
    print('Landing')
    drone.hover()
    if drone.flyingState is None or drone.flyingState == 1: # taking off
        drone.emergency()
    drone.land()
    sys.exit(0)


if __name__ == "__main__":
    main()
