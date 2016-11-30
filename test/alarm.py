import RPi.GPIO as GPIO
import time

def sound_alarm():
    """
    Sound the piezo buzzer.
    :return:
    """
    for i in range(10):
        GPIO.output(PIN, True)
        time.sleep(0.5)
        GPIO.output(PIN, False)
        time.sleep(0.1)


if __name__ == "__main__":
    # initialize piezo
    PIN = 18  # Use GPIO pin 18 as output
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN, GPIO.OUT)