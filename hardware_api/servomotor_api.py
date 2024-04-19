import RPi.GPIO as GPIO
import time


class Servomotor:
    """
    Class to work with servomotor by RPi.GPIO

    """

    def __init__(self):

        self.sleep_time_for_signal = 0.05
        self.pin_3_YEL = 3  # step
        self.pin_14_BLUE = 14  # (ENA)
        self.pin_4_GREY = 4  # direction (DIR)
        self.pin_17_MS1 = 17  # №6
        self.pin_18_MS2 = 18  # mode

    def initialize_pins(self,
                        direction: int,
                        mode: int):
        """

        Parameters
        ----------
        direction : int
            choose direction of rolling
            0 - left
            1 - right
        mode : int
            mode of rolling
            0 - full step
            1 - half step


        Returns
        -------

        """

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin_3_YEL, GPIO.OUT, initial=1)  # step
        GPIO.setup(self.pin_14_BLUE, GPIO.OUT, initial=1)  # (ENA)
        GPIO.setup(self.pin_4_GREY, GPIO.OUT, initial=1)  # (DIR)
        GPIO.setup(self.pin_17_MS1, GPIO.OUT, initial=0)
        GPIO.setup(self.pin_18_MS2, GPIO.OUT, initial=0)

        # Full step
        if mode == 0:
            GPIO.output(self.pin_17_MS1, 0)
            GPIO.output(self.pin_18_MS2, 0)
        # Half step
        elif mode == 1:
            GPIO.output(self.pin_17_MS1, 1)
            GPIO.output(self.pin_18_MS2, 0)
        elif mode == 2:
            GPIO.output(self.pin_17_MS1, 0)
            GPIO.output(self.pin_18_MS2, 1)
        elif mode == 4:
            GPIO.output(self.pin_17_MS1, 1)
            GPIO.output(self.pin_18_MS2, 1)
        else:
            raise 'Error with servomotor mode'

        GPIO.output(self.pin_4_GREY, direction)
        GPIO.output(self.pin_14_BLUE, 0)

    def next_step(self):

        GPIO.output(self.pin_3_YEL, 1)
        time.sleep(self.sleep_time_for_signal)
        GPIO.output(self.pin_3_YEL, 0)
        time.sleep(self.sleep_time_for_signal)

