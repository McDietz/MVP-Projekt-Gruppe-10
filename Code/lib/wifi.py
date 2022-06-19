import network
import ntptime
from machine import reset
import time
import log


def connect():
    wifi_passwds = {}

    with open("../cert/wifi_passwds.txt") as f:
        for line in f.readlines():
            if len(line) > 0 and ":" in line:
                wifi_id, passwd = line.strip().split(":")
                wifi_passwds[wifi_id] = passwd

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        visible_wifis = [w[0].decode("utf-8") for w in wlan.scan()]
        known_wifis = list(filter(lambda w: w in wifi_passwds.keys(), visible_wifis))

        if len(known_wifis) > 0:
            wifi = known_wifis[0]
            print("connecting to network", wifi)
            wlan.connect(wifi, wifi_passwds[wifi])
            deadline = time.ticks_add(time.ticks_ms(), 30000)
            while not wlan.isconnected():
                if time.ticks_diff(deadline, time.ticks_ms()) < 0:
                    break
                pass
            if wlan.isconnected():
                print("connected:", wlan.ifconfig())
            else:
                print("Unable to connect")
                log.log("Unable to connect")
                time.sleep(5)
                reset()
        else:
            print("No known network available.")
            log.log("No known network available.")
            time.sleep(20)
            reset()


def synchronize_rtc():
    # set the rtc datetime from the remote server
    try:
        ntptime.settime()
    except:
        log.log("Error synchronize_rtc ")
        time.sleep(5)
        reset()


def start():
    connect()
    synchronize_rtc()
