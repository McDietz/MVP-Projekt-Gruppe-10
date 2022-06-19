import json
import time

import network
from machine import RTC, reset

from lib import wifi, log, mqtt, measurement, interface
interface.lcd_backlight(False)
from lib.keypad import keypad_button

MQTT_TOPIC = "MQTT_TOPIC"
MQTT_TOPIC_Device = "MQTT_TOPIC_Device"


def convert_to_iso(datetime):
    y, m, d, _, h, mi, s, _ = datetime
    return "{}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(y, m, d, h, mi, s)


def publish_environment_data(mqtt_client):
    measured_data = measurement.measure_environment_data()
    iso_timestamp = convert_to_iso(RTC().datetime())
    measured_data.append(convert_to_iso(RTC().datetime()))

    message = {"co2": measured_data[0], "temperature": measured_data[1], "humidity": measured_data[2], "timestamp": iso_timestamp}
    mqtt_client.publish(MQTT_TOPIC, json.dumps(message))
    return measured_data


def publish_device_data(mqtt_client):
    iso_timestamp = convert_to_iso(RTC().datetime())
    error = log.get_log()
    message = {"timestamp_sent": iso_timestamp, "timestamp_error": error[0], "error_message": error[1]}
    mqtt_client.publish(MQTT_TOPIC_Device, json.dumps(message))


def keypad_thread(stop_time: '_TicksMs', data: list, settings: dict):
    button = keypad_button()
    stop_time, settings = interface.display_info(button, stop_time, data, settings)
    return stop_time, settings


def connect_and_publish():
    interface.print_lcd("connect wifi and synchronize RTC")
    time.sleep(1)
    wifi.start()
    time.sleep(1)

    interface.print_lcd("connect mqtt")
    mqtt_client = mqtt.connect_mqtt()

    interface.print_lcd("publish start signal")
    try:
        publish_device_data(mqtt_client)
    except Exception as f:
        print(str(f))
    time.sleep(5)

    interface.print_lcd("Start Sensor")
    #measurement.measurement_start()

    interface.print_lcd("publish data")
    starttime_measurement = time.ticks_ms()
    stoptime_interface = time.ticks_ms()
    settings = {'traffic_light': True}
    measured_data = [0, 0, 0]
    while True:
        if not network.WLAN(network.STA_IF).isconnected():
            log.log("no network connection while publishing")
            time.sleep(20)
            reset()
        else:
            try:
                delta = time.ticks_diff(time.ticks_ms(), starttime_measurement) / 1000
                # if delta is higher than 5 seconds measure data
                if delta > 5:
                    # measure data and send it to AWS
                    measured_data = publish_environment_data(mqtt_client)
                    # set new start time
                    starttime_measurement = time.ticks_ms()
                interface.traffic_light(measured_data[0], settings['traffic_light'])
                stoptime_interface, settings = keypad_thread(stoptime_interface, measured_data, settings)
            except Exception as e:
                print(str(e))
                log.log(str(e))
                reset()


if __name__ == "__main__":
    connect_and_publish()
print('loaded main')
