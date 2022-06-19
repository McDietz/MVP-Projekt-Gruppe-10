# Control over lcd and traffic light
# import display
import time
from machine import Pin, RTC, I2C
# Time to display data in seconds
display_time = 10
display_time_settings = 4
display_time_ticks = display_time * 1000
display_time_settings_ticks = display_time_settings * 1000

green = Pin(15, Pin.OUT)
yellow = Pin(2, Pin.OUT)
red = Pin(4, Pin.OUT)


def load_lcd():
    from lcd_api import LcdApi
    from i2c_lcd import I2cLcd
    I2C_ADDR = 0x27
    I2C_NUM_ROWS = 2
    I2C_NUM_COLS = 16

    i2c = I2C(sda=Pin(21), scl=Pin(22), freq=400000)
    lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)
    return lcd


def print_lcd(string):
    print(string)
    lcd.clear()
    lcd.putstr(string)


def lcd_backlight(state: bool):
    if state:
        lcd.backlight_on()
    else:
        lcd.backlight_off()


def display_info(button: str, end_time, data, settings: dict):
    if button == 1:
        print_lcd('aktueller CO2 Gehalt \n' + str(data[0]) + ' PPM')
        end_time = time.ticks_add(time.ticks_ms(), display_time_ticks)

    elif button == 4:
        print_lcd('Aktuelle Temperatur \n' + str(data[1]) + ' °C')
        end_time = time.ticks_add(time.ticks_ms(), display_time_ticks)

    elif button == 7:
        print_lcd('Aktuelle Luftfeutigkeit \n' + str(data[2]) + ' %')
        end_time = time.ticks_add(time.ticks_ms(), display_time_ticks)

    elif button == 8:
        print_lcd(str(data[3]))
        end_time = time.ticks_add(time.ticks_ms(), display_time_ticks)

    elif button == 2:
        settings['traffic_light'] = not settings['traffic_light']
        if settings['traffic_light']:
            print_lcd('Ampel eingeschaltet')
        else:
            print_lcd('Ampel ausgeschlatet')
        end_time = time.ticks_add(time.ticks_ms(), display_time_settings_ticks)

    delta = time.ticks_diff(end_time, time.ticks_ms()) / 1000
    if delta < 0:
        lcd_backlight(False)
        lcd.clear()
    else:
        lcd_backlight(True)
    return end_time, settings


def traffic_light(co2_value: int, state: bool):
    if state and 6 <= RTC().datetime()[4] < 20:
        if co2_value < 800:
            red.value(0)
            yellow.value(0)
            green.value(1)
        elif co2_value < 1200:
            green.value(0)
            red.value(0)
            yellow.value(1)
        elif co2_value >= 1200:
            green.value(0)
            yellow.value(0)
            red.value(1)
    else:
        green.value(0)
        yellow.value(0)
        red.value(0)


lcd = load_lcd()
