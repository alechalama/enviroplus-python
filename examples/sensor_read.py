# Imports ---------------------------------------------------------- #
try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559

    ltr559 = LTR559()
except ImportError:
    import ltr559

from bme280 import BME280
from pms5003 import PMS5003, ReadTimeoutError as pmsReadTimeoutError
from enviroplus import gas
import logging
import sys
from subprocess import PIPE, Popen
# from enviroplus.noise import Noise
# ------------------------------------------------------------------ #

# Constructing Sensor Objects for Fetching
bme280 = BME280()  # BME280 temperature/pressure/humidity sensor
pms5003 = PMS5003()  # PMS5003 particulate sensor
# noise = Noise()


""" Method for fetching all sensor data 
    and populating the readings dictionary,
    which it returns """
def get_readings():
    readings = {'pressure': get_pressure(),
                'humidity': get_humidity(),
                'temperature': get_temperature(),
                'light': get_light()  # ,
                # 'noise': get_noise()
    }
    return readings


# Sensor Read Methods ---------------------------------------------- #
""" Method for fetching the humidity """
def get_humidity():
    return bme280.get_humidity()


""" Method for fetching the pressure """
def get_pressure():
    return bme280.get_pressure()


""" Method for fetching the light """
def get_light():
    return ltr559.get_lux()


""" Method for fetching the noise returns 
    the amplitude of the noise detected """
def get_noise():
    pass
    # low, mid, high, amp = noise.get_noise_profile()
    # amp *= 64
    # return amp


""" Method for fetching the ambient temperature
    Temperature compensates for cpu temperature """
def get_cpu_temperature():
    process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE, universal_newlines=True)
    output, _error = process.communicate()
    return float(output[output.index('=') + 1:output.rindex("'")])

cpu_temps = [get_cpu_temperature()] * 5  # Sliding window for averaging cpu temperature.
temp_tuning_factor = 2.25  # Temperature Compensation Factor, value from libraries.

def get_temperature():
    global cpu_temps
    cpu_temps = cpu_temps[1:] + [get_cpu_temperature()]
    avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))
    raw_temp = bme280.get_temperature()
    return raw_temp - ((avg_cpu_temp - raw_temp) / temp_tuning_factor)
# ------------------------------------------------------------------ #

# Test Loop -------------------------------------------------------- #
try:
    while True:
        print(get_readings())
# Exit cleanly
except KeyboardInterrupt:
    sys.exit(0)
# ------------------------------------------------------------------ #

