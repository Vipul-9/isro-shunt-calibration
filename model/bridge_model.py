# Expected quarter-bridge output with shunt Rs across one Rg arm:
#   Vout = Vexc * Rg / (4*Rs + 2*Rg) = (Vexc / 2) * Rg / (2*Rs + Rg)
def compute_expected_voltage(Vexc, Rg, Rs):
    return (Vexc / 2) * (Rg / (2 * Rs + Rg))
