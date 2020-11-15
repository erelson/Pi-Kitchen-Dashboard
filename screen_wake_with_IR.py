#! /usr/bin/env python3
import os
import RPi.GPIO as GPIO
import time
from subprocess import call


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(8, GPIO.IN)
GPIO.setup(10, GPIO.OUT)

disp = os.getenv("DISPLAY", None)

if disp is not None:
    print("OK: Got DISPLAY variable {0}".format(disp))
    GPIO.output(10, 1)
    time.sleep(1)
    GPIO.output(10, 0)
else:
    print("ERROR: DISPLAY variable is not set, can't wake screen, so exiting...")

# Set screen to turn off after 2 minutes of idle
call(["xset", "dpms", "120", "120", "120"])

if __name__ == "__main__":
    # LED off
    GPIO.output(10, 0)
    active = False
    print("Started!")

    try:
        while True:
            time.sleep(1)
            if GPIO.input(8):
                GPIO.output(10, 1)  # LED on
                if active:
                    continue
                else:
                    active = True
                    # Wake the screen
                    call(["xset", "dpms", "force", "on"])
            else:
                GPIO.output(10, 0)  # LED off
                if active:
                    active = False
                else:
                    continue

    except KeyboardInterrupt as e:
        GPIO.output(10, 0)
    print("Bye!")
