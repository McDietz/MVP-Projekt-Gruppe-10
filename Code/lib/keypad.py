from machine import Pin


def keypad_button():
    wire_3 = 26
    wire_4 = 27
    wire_6 = 14
    wire_7 = 25
    wire_8 = 13

    button = "None"
    Pin(wire_3, Pin.OUT)
    Pin(wire_4, Pin.OUT)

    value_row_1 = not(Pin(wire_8, Pin.IN, Pin.PULL_UP).value())
    value_row_2 = not(Pin(wire_7, Pin.IN, Pin.PULL_UP).value())
    value_row_3 = not(Pin(wire_6, Pin.IN, Pin.PULL_UP).value())

    Pin(wire_8, Pin.OUT)
    Pin(wire_7, Pin.OUT)
    Pin(wire_6, Pin.OUT)

    value_column_1 = not(Pin(wire_4, Pin.IN, Pin.PULL_UP).value())
    value_column_2 = not(Pin(wire_3, Pin.IN, Pin.PULL_UP).value())

    if value_column_1:
        if value_row_1:
            button = 1
        elif value_row_2:
            button = 4
        elif value_row_3:
            button = 7
    elif value_column_2:
        if value_row_1:
            button = 2
        elif value_row_2:
            button = 5
        elif value_row_3:
            button = 8
    return button
