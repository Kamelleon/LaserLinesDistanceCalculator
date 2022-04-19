import sys, os, traceback
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from gpio_trigger import GPIOTrigger


class Lasers:
    def __init__(self):
        self.gpio_trigger = GPIOTrigger()
        self.status_file = "../lasers_status.info"
        self.turned_on_text = "WŁĄCZONE"
        self.turned_off_text = "WYŁĄCZONE"

    def get_status(self):
        try:
            with open(self.status_file, "r") as f:
                lasers_status = f.readline()
            if lasers_status == "enabled":
                lasers_status = self.turned_on_text
            else:
                lasers_status = self.turned_off_text
            return lasers_status
        except FileNotFoundError:
            print(f"Nie znaleziono pliku: {self.status_file}\n{traceback.format_exc()}")
            os._exit(1)
        except:
            print(f"Wystąpił inny błąd: {traceback.format_exc()}")
            os._exit(1)

    def turn_off(self):
        with open(self.status_file, "w") as f:
            f.write("disabled")
        self.gpio_trigger.turn_off_lasers()

    def turn_on(self):
        with open(self.status_file, "w") as f:
            f.write("enabled")
        self.gpio_trigger.turn_on_lasers()