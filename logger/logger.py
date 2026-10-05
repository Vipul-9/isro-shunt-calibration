import csv


def log_header(filename):
    # Create (or overwrite) the CSV file and add a header row
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Shunt", "Expected", "Measured", "Error", "Flag"])


def log_result(filename, row):
    # Append a calibration record to the CSV file
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(row)
