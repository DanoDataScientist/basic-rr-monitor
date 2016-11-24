# Continuous ADS1115 reading
# based off https://github.com/adafruit/Adafruit_Python_ADS1x15/blob/master/examples/continuous.py
import time

# Import the ADS1x15 module.
import Adafruit_ADS1x15


# Create an ADS1115 ADC (16-bit) instance.
adc = Adafruit_ADS1x15.ADS1115()

GAIN = 1
CHANNEL = 0

adc.start_adc(CHANNEL, gain=GAIN)

# Read channel 0 for 5 seconds and print out its values.
print('Reading ADS1x15 channel 0 for 5 seconds...')
start = time.time()
while (time.time() - start) <= 5.0:
    # Read the last ADC conversion value and print it out.
    value = adc.get_last_result()
    print('Channel 0: {0}'.format(value))
    # Sleep for half a second.
    time.sleep(0.5)

adc.stop_adc()
