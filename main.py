#!/usr/bin/env python3

from time import sleep, time, gmtime, strftime

from display import ButtonConnectionParameters, DisplayConnectionParameters, Display
from display_timeout_thread import DisplayTimeoutThread
from data_update_thread import DataUpdateThread
from page import ChartPage, TablePage
from psutil import cpu_percent, virtual_memory, disk_usage, sensors_temperatures, net_if_addrs, boot_time
from page_collection import PageCollection
from rotating_int import RotatingInt

info_page = TablePage(lambda: [
    ("IP", net_if_addrs()["eth0"][0][1]),
    ("IP", net_if_addrs()["wlan0"][0][1]),
    ("Uptime", strftime("%H:%M:%S", gmtime(time() - boot_time())))

], 60)
cpu_page = ChartPage("CPU", lambda: round(cpu_percent()), 10)
ram_page = ChartPage("RAM", lambda: round(virtual_memory().percent), 10)
root_page = ChartPage("/", lambda: round(disk_usage("/").percent), 10)
temperature_page = ChartPage(
    "TEMP", lambda: round(sensors_temperatures()["cpu_thermal"][0][1]), 10
)

page_collection = PageCollection()
page_collection.add(info_page)
page_collection.add(cpu_page)
page_collection.add(ram_page)
page_collection.add(root_page)
page_collection.add(temperature_page)

page_index = RotatingInt(0, len(page_collection.pages) - 1)


def handle_timeout_interaction() -> bool:
    if timeout_thread.is_sleeping:
        print("Timeout thread is sleeping, waking up")
        timeout_thread.restart()
        return True
    else:
        print("Timeout thread is not sleeping, cancelling timeout")
        timeout_thread.cancel_timeout()
        return False


def update_display(force: bool=False) -> None:
    page = page_collection.pages[page_index.current]
    if isinstance(page, ChartPage) and (page.dirty or force):
        display.render_chart(page.title, page.data.as_list())
        page.dirty = False
    elif isinstance(page, TablePage) and (page.dirty or force):
        display.render_table(page.data)
        page.dirty = False


def on_confirm_press():
    print("Confirm pressed")
    if handle_timeout_interaction():
        return


def on_back_press():
    print("Back pressed")
    if handle_timeout_interaction():
        return


def on_encoder_press():
    print("Encoder pressed")
    if handle_timeout_interaction():
        return


def on_encoder_cw():
    print("Encoder CW")
    if handle_timeout_interaction():
        return
    page_index.increment()
    update_display(True)


def on_encoder_ccw():
    print("Encoder CCW")
    if handle_timeout_interaction():
        return
    page_index.decrement()
    update_display(True)


display = Display(
    DisplayConnectionParameters(1, 0x3C),
    ButtonConnectionParameters(4, 17, 27, 22, 10),
    on_confirm_press,
    on_back_press,
    on_encoder_press,
    on_encoder_cw,
    on_encoder_ccw,
)


def on_timeout() -> None:
    display.turn_off()


def on_wakeup() -> None:
    display.turn_on()


sleep_timeout = 300
timeout_thread = DisplayTimeoutThread(sleep_timeout, on_timeout, on_wakeup)
update_thread = DataUpdateThread(page_collection)

if __name__ == "__main__":
    timeout_thread.start()
    update_thread.start()
    while True:
        update_display()
        sleep(5)
