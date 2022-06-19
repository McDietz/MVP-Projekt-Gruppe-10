# write and read error messages in log.txt
from machine import RTC


def convert_to_iso(datetime):
    y, m, d, _, h, mi, s, _ = datetime
    return "{}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(y, m, d, h, mi, s)


def log(error):
    with open('../log.txt', 'r') as f:
        content = f.readlines()

    iso_timestamp = convert_to_iso(RTC().datetime())

    with open('../log.txt', 'w') as f:
        error_message = iso_timestamp + ";" + str(error)
        content.append(str(error_message) + '\n')

        for i in content:
            f.write(i)


def get_log():
    logs_correct = []
    with open("../log.txt") as f:
        for line in f.readlines():
            if len(line) > 0 and ";" in line:
                timestamp, error = line.strip().split(";")
                log_text = [str(timestamp), str(error)]
                logs_correct.append(log_text)
    if len(logs_correct) == 0:
        logs_correct = [['-', '-']]
    return logs_correct[-1]
