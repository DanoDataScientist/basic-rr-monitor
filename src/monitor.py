import peakutils
import RPi.GPIO as GPIO
import time
import Adafruit_ADS1x15
from collections import deque

import matplotlib

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style

import Tkinter as tk
import numpy as np

global counter
counter = 0

def power_on_sound():
    """
    Sound the piezo buzzer for 1 second to indicate start up.
    :return:
    """
    GPIO.output(PIN, True)
    time.sleep(1)
    GPIO.output(PIN, False)


def update_lcd():
    """
    Update LCD with RR and error message if needed.
    """
    xList = np.multiply(DELAY, np.arange(0, len(WINDOW), 1))
    yList = WINDOW
    a.clear()
    a.plot(xList, yList)


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
    if int(RR) < LL:
        return "Respiration rate is too low!"
    elif int(RR) > UL:
        return "Respiration rate is too high!"
    return ""

def sample_data():
    """
    Samples from the ADC and appends the current value to the window of data.
    """
    val = adc.read_adc_difference(ADC_IN, gain=GAIN)
    WINDOW.append(val)
    

def calc_rr():
    """
    Uses most recent 10 seconds of data to calculate average RR
    """
    peaks = peakutils.peak.indexes(WINDOW)
    # for i in range(0, len(peaks) - 1):
    #     total += DELAY * (peaks[i + 1] - peaks[i])

    try:
        beats_per_second = len(peaks) / WINDOW_DURATION
        RR = str(beats_per_second / SECONDS_PER_MINUTE)
    except ZeroDivisionError:
        RR = str(-1)

def main(i):
    global counter
    # main loop
    print 'start'
    print time.time()
    sample_data()
    if len(WINDOW) == WINDOW_SIZE:
        calc_rr()
        check_alarm_conditions()
    update_lcd()
    app.frame.update_labels(RR)
    print time.time()
    # time.sleep(DELAY)
    

class GUI(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, "RR Monitor")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

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
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Graph Page!", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        self.rr = tk.StringVar()
        self.rr.set("Respiration Rate: ")
        
        rr_label = tk.Label(self, textvariable=self.rr, font=LARGE_FONT)
        rr_label.pack(pady=10, padx=10)

        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def update_labels(self, RR):
        self.rr.set(RR)
        
if __name__ == "__main__":
    LARGE_FONT = ("Verdana", 12)
    style.use("ggplot")

    f = Figure(figsize=(5, 5), dpi=100)
    a = f.add_subplot(111)
    a.axis('off')

    # initialize ADC
    adc = Adafruit_ADS1x15.ADS1115()
    GAIN = 1
    ADC_IN = 0

    # initialize piezo
    PIN = 18  # Use GPIO pin 18 as output
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN, GPIO.OUT)

    # alarm conditions
    LL = 10  # lower limit: 10 breaths per minute
    UL = 70  # upper limit: 70 breaths per minute

    RR = 'NOT ENOUGH DATA YET.'

    SECONDS_PER_MINUTE = 60
    FS = 1000  # Sample at 100 Hz
    DELAY = float(1) / FS
    WINDOW_DURATION = 10  # Determine RR from a 10-second window
    WINDOW_SIZE = int(WINDOW_DURATION / DELAY)
    WINDOW = deque([], WINDOW_SIZE)
    TIME = deque([], WINDOW_SIZE)

    app = GUI()
    power_on_sound()
    ani = animation.FuncAnimation(f, main, interval=1)
    app.mainloop()
