VREF = 5
MI_GAIN     = 10

CURRENT_RANGES = {
    "5u"    : {
        "C":        0,          # PMU C Value
        "MaxVal":   5e-6,       # Max Current
        "RSens":    200e3       # Sens Resistor
    },
    "20u"   : {
        "C":        1,          # PMU C Value
        "MaxVal":   20e-6,      # Max Current
        "RSens":    50e3        # Sens Resistor
    },
    "200u"  : {
        "C":        2,          # PMU C Value
        "MaxVal":   200e-6,     # Max Current
        "RSens":    5e3         # Sens Resistor
    },
    "2m"    : {
        "C":        3,          # PMU C Value
        "MaxVal":   2e-3,       # Max Current
        "RSens":    500         # Sens Resistor
    },
    "ext"   : {
        "C":        4,          # PMU C Value
        "MaxVal":   50e-3,      # Max Current
        "RSens":    15          # Sens Resistor
    },
    "HIGH_Z": {
        "C":        5,          # PMU C Value
        "MaxVal":   0           # Max Current
    }
}

