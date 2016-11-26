import peakutils
import RPi.GPIO as GPIO
import time
import Adafruit_ADS1x15
from collections import deque

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

SECONDS_PER_MINUTE = 60
FS = 100                                # Sample at 100 Hz
DELAY = float(1)/FS
WINDOW_DURATION = 30                      # Determine RR from a 30-second window
WINDOW_SIZE = int(WINDOW_DURATION / DELAY)
WINDOW = deque([], WINDOW_SIZE)


def power_on_sound():
    """
    Sound the piezo buzzer for 1 second to indicate start up.
    :return:
    """
    GPIO.output(PIN, True)
    time.sleep(1)
    GPIO.output(PIN, False)


def init_lcd():
    """
    Initialize LCD with initial RR and error message if needed.
    :return:
    """
    print(RR)


def update_lcd():
    """
    Update LCD with RR and error message if needed.
    """
    print(RR)


def sound_alarm():
    """
    Sound the piezo buzzer.
    :return:
    """
    for i in range(5):
        GPIO.output(PIN, True)
        time.sleep(0.01)
        GPIO.output(PIN, False)
        time.sleep(0.01)


def check_alarm_conditions():
    """
    Check that respiratory rate is within acceptable limits
    :return: return error message if outside of acceptable limits.
    """
    if RR < LL:
        return "Respiration rate is too low!"
    elif RR > UL:
        return "Respiration rate is too high!"
    return ""


def init_data():
    """
    Initialize a full window of data to make initial RR estimate.
    """
    for i in range(WINDOW_SIZE):
        sample_data()
    calc_rr()


def sample_data():
    """
    Samples from the ADC and appends the current value to the window of data.
    """
    val = adc.read_adc_difference(ADC_IN, gain=GAIN)
    WINDOW.append(val)
    time.sleep(DELAY)


def calc_rr():
    """
    Uses most recent 10 seconds of data to calculate average RR
    """
    total = 0
    peaks = peakutils.peak.indexes(WINDOW)
    for i in range(0, len(peaks) - 1):
        total += DELAY * (peaks[i + 1] - peaks[i])

    try:
        seconds_per_beat = total / (len(peaks) - 1)
        RR = SECONDS_PER_MINUTE / seconds_per_beat
    except ZeroDivisionError:
        RR = -1


def main():
    # initialize
    init_data() # every x seconds, acquire sample until a window is full
    init_lcd()
    power_on_sound()
    
    # main loop
    while True:
        # every x seconds, sample resistance
        sample_data()
        # update RR estimate
        calc_rr()
        # check for alarm conditions
        check_alarm_conditions()
        # update LCD
        update_lcd()

        time.sleep(DELAY)

if __name__ == "__main__":
    main()
