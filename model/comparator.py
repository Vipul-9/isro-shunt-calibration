def compare(expected, actual, tolerance):
    error = abs(expected - actual)  # difference between measured and expected
    flag = "PASS" if error <= tolerance else "FAIL"  # flag the measurement against the tolerance
    return error, flag
