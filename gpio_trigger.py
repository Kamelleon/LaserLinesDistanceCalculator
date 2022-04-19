import RPi.GPIO as GPIO
import threading
GPIO.setwarnings(False)

class GPIOTrigger:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Cut sensor
        GPIO.setup(5, GPIO.OUT)  # Lasers
        self.lasers_status_file = "lasers_status.info"
        self.button_pressed = False

    def check_cut_sensor(self):
        if GPIO.input(17):
            print("[+] Cut sensor: DETECTED CUT")
            self.button_pressed = True
        else:
            print("[~] Cut sensor: WAITING FOR CUT")
            self.button_pressed = False

        return self.button_pressed

    def get_lasers_status(self):
        try:
            with open(self.lasers_status_file, "r") as f:
                lasers_status = f.readline()
        except FileNotFoundError:
            print(f"Nie znaleziono pliku: {self.lasers_status_file}\n{traceback.format_exc()}")
            os._exit(1)
        except:
            print(f"Wystąpił inny błąd: {traceback.format_exc()}")
            os._exit(1)
        print(f"[i] Lasers: {lasers_status}")
        return lasers_status

    def turn_off_lasers(self):
        print("[~] Turning off lasers...")
        GPIO.output(5, GPIO.LOW)

    def turn_on_lasers(self):
        print("[~] Turning on lasers...")
        GPIO.output(5, GPIO.HIGH)
