from dht import DHT11
from machine import Pin, UART
import time


class MHZ19BSensor:

    # initializes a new instance
    def __init__(self, rx_pin=3, tx_pin=1):
        self.uart = UART(2, baudrate=9600, bits=8, parity=None, stop=1, tx=17, rx=16)

    # measure CO2
    def measure(self):
        while True:
            # send a read command to the sensor
            'try to connect: write'
            self.uart.write(b'\xff\x01\x86\x00\x00\x00\x00\x00\x79')

            # a little delay letting the sensor measure CO2 and send the data back
            time.sleep(1)  # in seconds
            # read and validate the data
            buf = self.uart.read(9)
            try:
                if self.is_valid(buf):
                    'valid'
                    break
            except Exception as e:
                print(e)
            time.sleep(1)
        co2 = buf[2] * 256 + buf[3]
        return co2

    def calibration(self):
        self.uart.write(b'\xff\x01\x79\x00\x00\x00\x00\x00\x80')

    # check data returned by the sensor
    def is_valid(self, buf):
        if buf is None or buf[0] != 0xFF or buf[1] != 0x86:
            return False
        i = 1
        checksum = 0x00
        while i < 8:
            checksum += buf[i] % 256
            i += 1
        checksum = ~checksum & 0xFF
        checksum += 1
        return checksum == buf[8]


def temp_hum_measurement():
    # measure temperature and humidity
    sensor = DHT11(Pin(23))
    sensor.measure()
    temp_measure = sensor.temperature()
    hum_measure = sensor.humidity()
    return temp_measure, hum_measure


def carbon_dioxide_measurement():
    # measure co2 in ppm
    sensor = MHZ19BSensor()
    co2_measure = sensor.measure()
    return co2_measure


def measurement_start():
    print("Program starts")
    sensor = MHZ19BSensor()
    print('Start der Stopuhr')
    start = time.ticks_ms()
    print('Initialisierung des Stoppdeltas')
    delta = 0
    print('Aufheizen von 1 Minute zum Messstart')
    while delta < 60:
        co2_measure = sensor.measure()
        time.sleep(1)
        temp_measure, hum_measure = temp_hum_measurement()
        time.sleep(1)
        # calculate delta since start
        delta = time.ticks_diff(time.ticks_ms(), start) / 1000
        print("\nPreheat time: ", round(delta, 2), "seconds")
        print("CO2: ", co2_measure, "ppm",
              "\nTemperature: ", temp_measure, "°C",
              "\nHumidity: ", hum_measure, "%")


def measure_environment_data():
    # combine measurement of co2, temperature and humidity in one function
    co2 = carbon_dioxide_measurement()
    temp, humid = temp_hum_measurement()
    return [co2, temp, humid]


