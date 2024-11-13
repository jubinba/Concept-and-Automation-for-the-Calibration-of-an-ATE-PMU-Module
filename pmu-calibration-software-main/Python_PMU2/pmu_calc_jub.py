from pmu_def_jub import VREF, MI_GAIN , CURRENT_RANGES

def dac_to_v(val, offset_dac=0xA492):
    return ((4.5 * val) - (3.5 * offset_dac)) * (VREF / (2**16))

def v_to_dac(val, offset_dac=0xA492):
    return round(((val * (2**16) / VREF) + (3.5*offset_dac)) / 4.5)

def  dac_to_i(val, range):
    rsens = CURRENT_RANGES[range]["RSens"]
    return (4.5 * VREF * (val-(2**15))) / ((2**16)*rsens*MI_GAIN)

def i_to_dac(val, range):
    rsens = CURRENT_RANGES[range]["RSens"]
    return round(((val * (2**16) * rsens * MI_GAIN)/(4.5 * VREF)) + (2**15))