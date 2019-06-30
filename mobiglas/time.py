import datetime
import time


def current_milli_time():
    return int(round(time.time() * 1000))


def to_date_time(epoch: int):
    return datetime.datetime.fromtimestamp(epoch / 1000.0).strftime('%Y-%m-%d@%H:%M')


def add_hours(epoch: int, hours: int):
    return (datetime.datetime.fromtimestamp(epoch / 1000.0) + datetime.timedelta(hours=hours)).timestamp() * 1000


def current_date_time():
    return to_date_time(current_date_time())
