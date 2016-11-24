import peakutils

RR = 0
WINDOW_SIZE = 10
FS = 5
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
