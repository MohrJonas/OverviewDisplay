import RPi.GPIO as GPIO
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
from typing import Callable
from PIL import ImageFont
from math import ceil


class ButtonConnectionParameters:
    def __init__(
        self,
        confirm_button_pin: int,
        back_button_pin: int,
        encoder_click_button_pin: int,
        encoder_a_button_pin: int,
        encoder_b_button_pin: int,
    ):
        self.confirm_button_pin = confirm_button_pin
        self.back_button_pin = back_button_pin
        self.encoder_click_button_pin = encoder_click_button_pin
        self.encoder_a_button_pin = encoder_a_button_pin
        self.encoder_b_button_pin = encoder_b_button_pin


class DisplayConnectionParameters:
    def __init__(self, i2c_port: int, i2c_address: int):
        self.i2c_port = i2c_port
        self.i2c_address = i2c_address


class Display:

    def __on_confirm_button_click(self, channel: int) -> None:
        self.on_confirm_press()

    def __on_back_button_click(self, channel: int) -> None:
        self.on_back_press()

    def __on_encoder_button_click(self, channel: int) -> None:
        self.on_encoder_press

    def __on_encoder_a_trigger(self, channel: int) -> None:
        if GPIO.input(self.__button_parameters.encoder_b_button_pin) == GPIO.HIGH:
            self.on_encoder_turn_ccw()
        else:
            self.on_encoder_turn_cw()

    def __init__(
        self,
        connection_parameters: DisplayConnectionParameters,
        button_parameters: ButtonConnectionParameters,
        on_confirm_press: Callable[[], None],
        on_back_press: Callable[[], None],
        on_encoder_press: Callable[[], None],
        on_encoder_turn_cw: Callable[[], None],
        on_encoder_turn_ccw: Callable[[], None],
    ) -> None:
        self.on_confirm_press = on_confirm_press
        self.on_back_press = on_back_press
        self.on_encoder_press = on_encoder_press
        self.on_encoder_turn_cw = on_encoder_turn_cw
        self.on_encoder_turn_ccw = on_encoder_turn_ccw

        self.__device = sh1106(
            i2c(
                port=connection_parameters.i2c_port,
                address=connection_parameters.i2c_address,
            )
        )
        self.__font = ImageFont.load_default(10)

        self.__connection_parameters = connection_parameters
        self.__button_parameters = button_parameters

        GPIO.setmode(GPIO.BCM)

        GPIO.setup(
            button_parameters.confirm_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN
        )
        GPIO.add_event_detect(
            button_parameters.confirm_button_pin,
            GPIO.RISING,
            callback=self.__on_confirm_button_click,
            bouncetime=300,
        )

        GPIO.setup(
            button_parameters.back_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN
        )
        GPIO.add_event_detect(
            button_parameters.back_button_pin,
            GPIO.RISING,
            callback=self.__on_back_button_click,
            bouncetime=300,
        )

        GPIO.setup(
            button_parameters.encoder_click_button_pin,
            GPIO.IN,
            pull_up_down=GPIO.PUD_DOWN,
        )
        GPIO.add_event_detect(
            button_parameters.encoder_click_button_pin,
            GPIO.RISING,
            callback=self.__on_encoder_button_click,
            bouncetime=300,
        )

        GPIO.setup(
            button_parameters.encoder_a_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN
        )
        GPIO.add_event_detect(
            button_parameters.encoder_a_button_pin,
            GPIO.RISING,
            callback=self.__on_encoder_a_trigger,
            bouncetime=300,
        )

        GPIO.setup(
            button_parameters.encoder_b_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN
        )

    def __get_text_size(self, text: str) -> tuple[int, int]:
        ascent, descent = self.__font.getmetrics()
        line_height = ascent + descent
        text_length = ceil(self.__font.getlength(text))
        return (text_length, line_height)

    def __trucate_str_to_size(self, text: str, max_size: int) -> str:
        (initial_text_width, _) = self.__get_text_size(text)
        if initial_text_width <= max_size:
            return text

        truncated_text = text[:-3:]
        while True:
            (text_width, _) = self.__get_text_size(f"{truncated_text}...")
            if text_width <= max_size:
                return f"{truncated_text}..."
            truncated_text = truncated_text[:-1:]

    def clear(self) -> None:
        self.__device.clear()

    def turn_off(self) -> None:
        self.__device.hide()

    def turn_on(self) -> None:
        self.__device.show()

    def render_chart(self, title: str, data: list[int]) -> None:
        display_width = self.__device.width
        display_height = self.__device.height

        multiplier = display_height / 100

        (text_length, text_height) = self.__get_text_size(title)
        text_x = (display_width - text_length) / 2

        data_to_render = data[-(min(len(data), display_width)) : :]

        with canvas(self.__device) as draw:
            self.clear()
            for x in range(len(data_to_render)):
                draw.line(
                    [
                        (x, display_height),
                        (x, display_height - (data_to_render[x] * multiplier)),
                    ],
                    fill="white",
                )
            draw.rectangle((text_x, 0, text_x + text_length, text_height), fill="black")
            draw.text((text_x, 0), title, fill="white")

    def render_table(self, data: list[tuple[str, str]]) -> None:
        # Text does not matter here, we only care about the height
        (_, text_height) = self.__get_text_size("Foo")

        with canvas(self.__device) as draw:
            self.clear()
            for i in range(len(data)):
                (key, value) = data[i]
                key_column_size = self.__get_text_size(key)[0]
                value_column_size = self.__device.width - key_column_size
                truncated_value = self.__trucate_str_to_size(value, value_column_size)
                draw.text((0, i * text_height), key, fill="white")
                (text_width, _) = self.__get_text_size(truncated_value)
                draw.text(
                    (self.__device.width - text_width - 2, i * text_height),
                    truncated_value,
                    fill="white",
                )
