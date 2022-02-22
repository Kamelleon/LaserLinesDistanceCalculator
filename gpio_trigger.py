import RPi.GPIO as GPIO
import threading
class GPIOTrigger:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.button_pressed = False

    def check_button_press(self):
        if GPIO.input(17):
            print("[i] Trigger button: RELEASED (high)")
            self.button_pressed = False
        else:
            print("[i] Trigger button: PRESSED (low)")
            self.button_pressed = True

        return self.button_pressed