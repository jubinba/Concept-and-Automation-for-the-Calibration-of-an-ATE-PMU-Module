
from time import sleep
from tqdm import tqdm
import pandas as pd
import numpy as np
from si_prefix import si_format

from pmu_som import pmu_calc_jub
from pmu_som import pmu_def_jub

MEAS_COUNT = 5
MEAS_SLEEP = 0.1
MEAS_NPLC = 1



pmu_reg_channel_off = 0x1E060




        
    
def cal_jub_FIN_U_C(
        p,
        k,
        channel,
        wait_before_measure = 0.5,
        measure_delay=MEAS_SLEEP,
        measure_count=MEAS_COUNT ):
    
    # pmu initialisation- all channels turned off and reset , initial default
    p.write_all_PMU_REGS(pmu_reg_channel_off)
    pmu_reg_channel_on_sys = 0x21fc60

    # INTRO
    print("FIN_U_C CALIBRATION for channel %i" % channel)
    pmu_ch = p.channels[channel]

    LSB_SIZE_V = 4.5 * pmu_def_jub.VREF / (2**16)
    OFFSET = pmu_ch.read_dac("Offset")
    FIN_U_C = pmu_ch.read_dac("FIN_U","C")

    # SMU SETUP
    k.display.screen            = k.display.SMUA
    k.display.smua.measure.func = k.display.MEASURE_DCVOLTS
    k.smua.measure.autorangev   = k.smua.AUTORANGE_ON
    k.smua.measure.nplc = MEAS_NPLC

    k.smua.source.func          = k.smua.OUTPUT_DCAMPS
    k.smua.source.leveli        = 0
    k.smua.source.limiti        = 1e-3
    k.smua.source.limitv        = 20
    k.smua.source.output        = k.smua.OUTPUT_ON


    pmu_ch.pmu_reg = pmu_reg_channel_on_sys

    # zero calibration

    dac_zero = pmu_calc_jub.v_to_dac(0,OFFSET)
    #v_zero = pmu_calc_jub.dac_to_v(dac_zero ,OFFSET)

    # Writing zero calibration value to X1

    pmu_ch.write_dac(dac_zero, dac_reg = "FIN_U")  # The value is by default assisgned to reg = "X1"
    sleep(wait_before_measure)
    meas_zero = measure_jub(k,measure_count,measure_delay)

    NEW_FIN_U_C = round(FIN_U_C-(meas_zero/LSB_SIZE_V))

    print("\tNEW_FIN_U_C = FIN_U_C -(Zero_offset_output for 0 volts/LSB) ")
    print("\t%i = %i -(%sv/%sv)"%(
        NEW_FIN_U_C,
        FIN_U_C,
        si_format(meas_zero,precision=3),
        si_format(LSB_SIZE_V,precision=3)
        ))
    
    pmu_ch.write_dac(data = NEW_FIN_U_C, dac_reg = "FIN_U" ,reg = "C")
    pmu_ch.write_dac(data = dac_zero, dac_reg = "FIN_U")
    sleep(wait_before_measure)
    meas_zero_cal = measure_jub(k,measure_count,measure_delay)
    print("\tOutput Voltage after Calicration = %sv" % si_format(meas_zero_cal,precision = 3))

    pmu_ch.pmu_reg = pmu_reg_channel_off
    k.smua.source.output = k.smua.OUTPUT_OFF

    return NEW_FIN_U_C

def cal_jub_FIN_U_M(
        p,
        k,
        channel,
        wait_before_measure =0.5,
        measure_delay = MEAS_SLEEP,
        measure_count =MEAS_COUNT):
    
    # pmu initialisation- all channels turned off and reset , initial default
    p.write_all_PMU_REGS(pmu_reg_channel_off)
    pmu_reg_channel_on_sys = 0x21fc60

    print("FIN_U_C CALIBRATION for channel %i" % channel)
    pmu_ch = p.channels[channel]

    OFFSET = pmu_ch.read_dac("Offset")
    FIN_U_M = pmu_ch.read_dac("FIN_U","M")

    #SMU SETUP
    k.display.screen            = k.display.SMUA
    k.display.smua.measure.func = k.display.MEASURE_DCVOLTS
    k.smua.measure.autorangev   = k.smua.AUTORANGE_ON
    k.smua.measure.nplc = MEAS_NPLC

    k.smua.source.func          = k.smua.OUTPUT_DCAMPS
    k.smua.source.leveli        = 0
    k.smua.source.limiti        = 1e-3
    k.smua.source.limitv        = 20
    k.smua.source.output        = k.smua.OUTPUT_ON

    pmu_ch.pmu_reg = pmu_reg_channel_on_sys

    # zero calibration
    dac_max = 0xFFFF
    v_high = pmu_calc_jub.dac_to_v(dac_max,OFFSET)  # Expected voltage corresponding to 0xFFFF without any calibration ---> From the equation

    #  Writing zero calibration to the value to x1

    pmu_ch.write_dac(dac_max, dac_reg ="FIN_U")  # The value is by default assisgned to reg = "X1"
    sleep(wait_before_measure)
    meas_max = measure_jub(k,measure_delay,measure_count)   # Measured voltage corresponding to 0xFFFF without any calibration ---> From Keithley measurement

    NEW_FIN_U_M = round(FIN_U_M * (v_high/meas_max))

    print("\tNEW_FIN_U_M = FIN_U_M * (Zero_offset_output for 0xFFFF.....Expected Value Value/Zero_Offset_output for 0xFFFF......Measured Value)")
    print("\t%i = %i * (%sV/%sV)"  %(
        NEW_FIN_U_M,
        FIN_U_M,
        si_format(v_high,precision = 3),
        si_format(meas_max,precision = 3)
        ))
    
    if NEW_FIN_U_M > 0xFFFF:
        NEW_FIN_U_M = 0xFFFF

    pmu_ch.write_dac(NEW_FIN_U_M,dac_reg = "FIN_U",reg = "M")
    pmu_ch.write_dac(dac_max,dac_reg = "FIN_U")
    sleep(wait_before_measure)

    meas_max_cal = measure_jub(k,measure_delay,measure_count)
    print("V_MAX after Calibration = %sV" % si_format(meas_max_cal,precision=3))

    pmu_ch.pmu_reg = pmu_reg_channel_off
    k.smua.source.output = k.smua.OUTPUT_OFF
    
    return NEW_FIN_U_M

def cal_jub_FIN_I_C(
        p,
        k,
        channel,
        range,
        wait_before_measure = 0.5,
        measure_delay = MEAS_SLEEP,
        measure_count = MEAS_COUNT):
    
    # pmu initialisation- all channels turned off and reset , initial default
    p.write_all_PMU_REGS(pmu_reg_channel_off)
    pmu_ch = p.channels[channel]

    # Equation for calculation of LSB SIZE
    LSB_SIZE_I = 4.5*pmu_def_jub.VREF / ((2**16)*pmu_def_jub.CURRENT_RANGES[range]["RSens"]*pmu_def_jub.MI_GAIN)

    FIN_I_C = pmu_ch.read_dac("FIN_I"+range,"C") # Reading the value in C of the PMU from FIN_I+range(eg. "FIN_I_2m")

    # SMU SETUP

    k.display.screen = k.display.SMUA
    k.display.smua.measure.func = k.display.MEASURE_DCAMPS

    k.smua.measure.autorangei = k.smua.AUTORANGE_ON
    k.smua.measure.autorangev = k.smua.AUTORANGE_ON
    k.smua.measure.rangei = pmu_def_jub.CURRENT_RANGES[range]["MaxVal"]
    k.smua.measure.nplc = MEAS_NPLC 

    k.smua.source.func = k.smua.OUTPUT_DCVOLTS
    k.smua.source.levelv = 0     # by default k.smua.source.levelv and k.smua.source.leveli = 0
    k.smua.source.limiti = pmu_def_jub.CURRENT_RANGES[range]["MaxVal"]
    k.smua.source.limitv = 13
    k.smua.source.output = k.smua.OUTPUT_ON

    p.change_sys_ctrl({
        "DUTGND/CH" : 1,
        "INT10K" : 1,
        "TMP ENABLE" : 1,
        "TMP" : 3 # Thermal shutdown at 100°C
        })
    
    pmu_ch.change_pmu_reg({
        "CH EN" : 1,
        "FORCE" : 1,
        "SS0" : 1,
        "SF0" : 1,
        "C" : pmu_def_jub.CURRENT_RANGES[range]["C"],  
        "FIN" : 1
    })

    pmu_reg_channel_on_sys = pmu_ch.pmu_reg

    dac_zero = 0x8000 # DAC code corresponding to 0 volts

    # Writing dac code corresponding to 0 volts to "X1"
    pmu_ch.write_dac(dac_zero,dac_reg = "FIN_I_"+range)
    sleep(wait_before_measure)
    meas_zero = -measure_jub(k,measure_delay,measure_count,"i") # Output current for 0x8000 to "X1"

    NEW_FIN_I_C = round(FIN_I_C -(meas_zero/LSB_SIZE_I))
    

print("\tNEW_FIN_C = FIN_C - (Zero_offset / LSB)")
print("\t%i = %i - (%sA / %sA)" %(
    NEW_FIN_I_C,
    FIN_I_C,
    si_format(meas_zero, precision=3),
    si_format(LSB_SIZE_I, precision=3)
))

pmu


















    


def measure_jub(
        k,
        meas_delay = MEAS_SLEEP,
        meas_count = MEAS_COUNT,
        meas_func = "v"
        ):


    values = list()
    if meas_func =="v":
        meas_func = k.smua.measure.v
    elif meas_func == "i":
        meas_func = k.smua.measure.i
    else:
        raise ValueError("unsupported measurement function")
    
    for _ in range(meas_count):
        values.append(meas_func())
        sleep(meas_delay)

    values = np.array(values)
    if values.max() - values.min() > 0.1 :
        print("Measured values have a very high deviation for a single input (%f)" % values.std()) #Warning for high deviation
    return values.mean()


















    
    

     