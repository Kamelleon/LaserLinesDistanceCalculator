import RPi.GPIO as GPIO
import threading
GPIO.setwarnings(False)

class GPIOTrigger:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(5, GPIO.OUT)
        self.button_pressed = False

    def check_button_press(self):
        if GPIO.input(17):
            print("[i] Trigger button: RELEASED (high)")
            self.button_pressed = False
        else:
            print("[i] Trigger button: PRESSED (low)")
            self.button_pressed = True

        return self.button_pressed

    def turn_off_lasers(self):
        GPIO.output(5, GPIO.LOW)

    def turn_on_lasers(self):
        GPIO.output(5, GPIO.HIGH)
