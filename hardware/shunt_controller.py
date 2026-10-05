try:
    import RPi.GPIO as GPIO
except ImportError:  # running off the Pi: use a no-op stand-in so the GUI still works
    from hardware.gpio_stub import GPIO


class ShuntController:
    def __init__(self, pin_map):
        # Store pin mapping for each shunt
        self.pin_map = pin_map
        GPIO.setmode(GPIO.BCM)

        # Set each pin as output and ensure they start LOW (off)
        for pin in self.pin_map.values():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)

    def deactivate_all(self):
        # Turn off all shunts
        for pin in self.pin_map.values():
            GPIO.output(pin, GPIO.LOW)

    def activate(self, shunt):
        # First turn off all shunts, then activate the requested one
        self.deactivate_all()
        GPIO.output(self.pin_map[shunt], GPIO.HIGH)

    def cleanup(self):
        # Reset all GPIO pins when done
        GPIO.cleanup()
