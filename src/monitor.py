import peakutils
import RPi.GPIO as GPIO
import time
import Adafruit_ADS1x15
from collections import deque
from subprocess import call

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style

import Tkinter as tk
import numpy as np

import threading

SCREEN_WIDTH = 320
SCREEN_HEIGHT = 240


def shutdown(pin):
    call('halt', shell=False)


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


def update_lcd():
    """
    Update LCD with RR and error message if needed.
    """
    from numpy import array
    a.clear()
    a.plot(TIMES, moving_avg(array(WINDOW)))
    a.axis('off')

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


def check_alarm_conditions(RR):
    """
    Check that respiratory rate is within acceptable limits
    :return: return error message if outside of acceptable limits.
    """
    global ALARM_TRIGGER_COUNTER
    message = ""
    if float(RR) < LL:
        message = "Respiration rate is too low!"
    elif float(RR) > UL:
        message = "Respiration rate is too high!"

    if message != "":
        if threading.active_count() < 2 and ALARM_TRIGGER_COUNTER >= 20:
            thread = AlarmThread()
            thread.start()
        ALARM_TRIGGER_COUNTER = ALARM_TRIGGER_COUNTER + 1
    else:
        ALARM_TRIGGER_COUNTER = 0


    return message


def sample_data():
    """
    Samples from the ADC and appends the current value to the window of data.
    """
    val = adc.read_adc_difference(ADC_IN, gain=GAIN)
    WINDOW.append(val)
    TIMES.append(time.time() - START_TIME)

def moving_avg(arr):
    ret = []
    ret.append(arr[0])
    for i in range(1, len(arr) - 1):
        ret.append(float(arr[i-1] + arr[i] + arr[i + 1])/3)
    if len(arr) != len(ret):
        ret.append(arr[len(arr) - 1])
    return ret

def calc_rr():
    """
    Uses most recent 10 seconds of data to calculate average RR
    """
    from numpy import array
    from peakdet import peakdet
    arr = array(moving_avg(array(WINDOW)))
    peaks = peakdet(arr, 1)
    peaks = peaks[0]
    print(len(peaks))
    try:
        beats_per_second = len(peaks) / (TIMES[len(TIMES) - 1] - TIMES[0])
        RR = str(beats_per_second * SECONDS_PER_MINUTE)
    except ZeroDivisionError:
        RR = str(-1)
    return RR

def main(i):
    # main loop
    global RR
    sample_data()
    message = ""
    if len(WINDOW) == WINDOW_SIZE:
        RR = calc_rr()
        message = check_alarm_conditions(RR)
    update_lcd()
    app.frame.update_labels(RR, message)
    # time.sleep(DELAY)

class AlarmThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        sound_alarm()

class GUI(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, "RR Monitor")

        container = tk.Frame(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        w = SCREEN_WIDTH;
        h = SCREEN_HEIGHT
        x = 0
        y = 0

        self.geometry('%dx%d+%d+%d' % (w, h, x, y))

        self.frames = {}

        self.frame = Graph(container, self)

        self.frames[Graph] = self.frame

        self.frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(Graph)

    def show_frame(self, cont):
        self.frame = self.frames[cont]
        self.frame.tkraise()


class Graph(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, width=SCREEN_WIDTH, height=SCREEN_WIDTH)
        label = tk.Label(self, text="Infant Respiration Monitor", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        self.rr = tk.StringVar()
        self.rr.set("Respiration Rate: ")

        self.rr_label = tk.Label(self, textvariable=self.rr, font=LARGE_FONT, bg = COLORS[0])
        self.rr_label.pack(pady=10, padx=10)

        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def update_labels(self, RR, message):
        if RR == "Not enough data yet.":
            self.rr.set("Respiration Rate: Not enough data yet.")
        elif message == "":
            self.rr.set("Respiration Rate: " + str(round(float(RR), 2)))
        else:
            self.rr.set(message + "(RR = " + str(round(float(RR), 2)) + ")")

        if RR != "Not enough data yet.":
            dist = abs(float(RR) - MEAN)
            self.rr_label.configure(bg = COLORS[min(len(COLORS) - 1, int(dist / DELTA))])



if __name__ == "__main__":
    LARGE_FONT = ("Verdana", 12)
    style.use("ggplot")

    f = Figure(figsize=(3, 1.5), dpi=100)
    a = f.add_subplot(111)

    # initialize ADC
    adc = Adafruit_ADS1x15.ADS1115()
    GAIN = 1
    ADC_IN = 0

    # initialize piezo
    PIN = 18  # Use GPIO pin 18 as output
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN, GPIO.OUT)

    # alarm conditions
    LL = 30  # lower limit: 10 breaths per minute
    UL = 60  # upper limit: 70 breaths per minute
    MEAN = (LL + UL) / 2
    DELTA = float(UL - MEAN) / 2

    RR = 'Not enough data yet.'
    START_TIME = time.time()

    SECONDS_PER_MINUTE = 60
    FS = 1000  # Sample at 100 Hz
    DELAY = float(1) / FS
    WINDOW_DURATION = 10  # Determine RR from a 10-second window
    #WINDOW_SIZE = int(WINDOW_DURATION / DELAY)
    WINDOW_SIZE = 120
    global ALARM_TRIGGER_COUNTER
    ALARM_TRIGGER_COUNTER = 0

    COLORS = ['lime green', 'dark green', 'red', 'red4']

    WINDOW = deque([], WINDOW_SIZE)
    TIMES = deque([], WINDOW_SIZE)

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(21, GPIO.IN)
    GPIO.add_event_detect(21, GPIO.RISING, callback=shutdown, bouncetime=100)

    app = GUI()
    power_on_sound()
    ani = animation.FuncAnimation(f, main, interval=1)
    app.mainloop()
