import RPi.GPIO as GPIO
import time

def power_on_sound():
    """
    Sound the piezo buzzer for 1 second to indicate start up.
    :return:
    """
    for i in range(3):
        GPIO.output(PIN, True)
        time.sleep(0.1)
        GPIO.output(PIN, False)
        time.sleep(0.1)

if __name__ == "__main__":
    # initialize piezo
    PIN = 18  # Use GPIO pin 18 as output
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN, GPIO.OUT)

    power_on_sound()