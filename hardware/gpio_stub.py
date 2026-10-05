"""Minimal RPi.GPIO stand-in so the software runs on a PC (manual-input mode)."""


class _GPIOStub:
    BCM, OUT, HIGH, LOW = "BCM", "OUT", 1, 0

    def setmode(self, mode): pass
    def setup(self, pin, mode): pass
    def output(self, pin, value): pass
    def cleanup(self): pass


GPIO = _GPIOStub()
