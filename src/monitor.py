import peakutils
import RPi.GPIO as GPIO
import time
import Adafruit_ADS1x15

# initialize ADC
adc = Adafruit_ADS1x15.ADS1115()
GAIN = 1
ADC_IN = 0

# initialize piezo
PIN = 18                                # Use GPIO pin 18 as output
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.OUT)

# alarm conditions
LL = 10                                 # lower limit: 10 breaths per minute
UL = 70                                 # upper limit: 70 breaths per minute

RR = 0
WINDOW_SIZE = 10                        # Determined RR from a 10-second window
FS = 100                                # Sample at 100 Hz
DELAY = 1/FS
DATA = []

def power_on_sound():
    pass

def init_LCD(init_RR):
    pass

def update_LCD():
    pass

def check_alarm_conditions():
    pass

def init_data():
    pass

def sample_data():
    pass

def calc_RR():
    pass

def main():
    # initialize
    power_on_sound()
    init_data() # every x seconds, acquire sample until a window is full
    init_LCD(calc_RR())

    # main loop
    while True:
        # every x seconds, sample resistance
        sample_data()
        # update RR estimate
        calc_RR()
        # check for alarm conditions
        check_alarm_conditions()
        # update LCD
        update_LCD()

if __name__ == "__main__":
    main()
