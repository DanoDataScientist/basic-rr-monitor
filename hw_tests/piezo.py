import RPi.GPIO as GPIO
import time

PIN = 18                                # Use GPIO pin 18 as output
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.OUT)

while True:
    GPIO.output(18, True)
    time.sleep(0.5)
    GPIO.output(18, False)
    time.sleep(0.5)