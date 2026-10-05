import time

try:
    import smbus
except ImportError:
    try:
        import smbus2 as smbus
    except ImportError:
        smbus = None

ADS1015_ADDR = 0x48

# Relay -> ADS1015 input. Channel 0 = differential AIN0 (V+) - AIN1 (V-),
# i.e. the bridge output. All shunts are read on the same channel.
channel_map = {"R1": 0, "R2": 0, "R3": 0, "R4": 0, "R5": 0}

# PGA full-scale range (V) -> config bits. Smaller range = finer LSB.
PGA = {6.144: 0b000, 4.096: 0b001, 2.048: 0b010, 1.024: 0b011, 0.512: 0b100, 0.256: 0b101}


def read_ads1015(channel, fsr=2.048):
    if smbus is None:
        raise RuntimeError("smbus not available - run on the Raspberry Pi or set use_adc=false")
    bus = smbus.SMBus(1)

    # OS=1 (start), MUX=channel, PGA=fsr, single-shot, 1600 SPS, comparator off
    config = 0x8000 | (channel << 12) | (PGA[fsr] << 9) | 0x0100 | 0x0083
    bus.write_i2c_block_data(ADS1015_ADDR, 1, [(config >> 8) & 0xFF, config & 0xFF])

    time.sleep(0.1)
    data = bus.read_i2c_block_data(ADS1015_ADDR, 0, 2)
    value = ((data[0] << 8) | data[1]) >> 4   # 12-bit result
    if value > 0x7FF:                           # two's complement
        value -= 1 << 12
    lsb = fsr / 2048                            # volts per bit for this PGA setting
    return value * lsb


def get_voltage(shunt, fsr=2.048):
    return read_ads1015(channel_map[shunt], fsr)
