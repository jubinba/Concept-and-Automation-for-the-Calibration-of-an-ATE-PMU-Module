from time import sleep
from tqdm import tqdm
import numpy as np
from si_prefix import si_format
# import logging

from . import pmu_calc
from . import pmu_def

MEAS_COUNT = 5
MEAS_SLEEP = 0.1
MEAS_NPLC  = 1 # 0.1 ... 25

pmu_reg_channel_off = 0x1E060

def cal_FIN_U_C(
            pmu,
            keithley,
            channel,
            wait_before_measure = 0.5,
            measure_delay=MEAS_SLEEP,
            measure_count=MEAS_COUNT):
    
    # reset PMU-Regs
    pmu.write_all_PMU_REGS(pmu_reg_channel_off)
    pmu_reg_channel_on_sys = 0x21fc60
    
    # intro
    print("FIN_U_C CALIBRATION for channel %i" % channel)
    pmu_ch = pmu.channels[channel]
    
    LSB_SIZE_V = 4.5 * pmu_def.VREF / (2**16)
    OFFSET  = pmu_ch.read_dac("Offset")
    FIN_U_C = pmu_ch.read_dac("FIN_U", "C")
    
    # setup SMU
    keithley.display.screen = keithley.display.SMUA
    keithley.display.smua.measure.func = keithley.display.MEASURE_DCVOLTS
    
    keithley.smua.measure.autorangev = keithley.smua.AUTORANGE_ON
    keithley.smua.measure.nplc = MEAS_NPLC # 0.001 to 25

    keithley.smua.source.func = keithley.smua.OUTPUT_DCAMPS
    keithley.smua.source.leveli = 0
    keithley.smua.source.limiti = 1e-3
    keithley.smua.source.limitv = 20
    keithley.smua.source.output = keithley.smua.OUTPUT_ON
    
    

    pmu_ch.pmu_reg = pmu_reg_channel_on_sys
    
    # zero calibration
    dac_zero = pmu_calc.v_to_dac(0, OFFSET)
    v_zero = pmu_calc.dac_to_v(dac_zero, OFFSET)
    
    # set pos cal value
    pmu_ch.write_dac(dac_zero, dac_reg = "FIN_U")
    sleep(wait_before_measure)
    meas_zero = measure(keithley, measure_delay, measure_count)
    
    NEW_FIN_U_C = round(FIN_U_C - (meas_zero/LSB_SIZE_V))
    
    print("\tNEW_FIN_C = FIN_C - (Zero_offset / LSB)")
    print("\t%i = %i - (%sV / %sV)" %(
        NEW_FIN_U_C,
        FIN_U_C,
        si_format(meas_zero, precision=3),
        si_format(LSB_SIZE_V, precision=3)
    ))
    
    pmu_ch.write_dac(data = NEW_FIN_U_C, dac_reg = "FIN_U", reg = "C")
    pmu_ch.write_dac(dac_zero, dac_reg = "FIN_U")
    sleep(wait_before_measure)
    meas_zero_cal = measure(keithley, measure_delay, measure_count)
    print("\tOffset after Cal = %sV" % si_format(meas_zero_cal, precision=3))
    
    pmu_ch.pmu_reg = pmu_reg_channel_off
    keithley.smua.source.output = keithley.smua.OUTPUT_OFF
    
    return NEW_FIN_U_C

def cal_FIN_U_M(
            pmu,
            keithley,
            channel,
            wait_before_measure = 0.5,
            measure_delay=MEAS_SLEEP,
            measure_count=MEAS_COUNT):
    
    # reset PMU-Regs
    pmu.write_all_PMU_REGS(pmu_reg_channel_off)
    pmu_reg_channel_on_sys = 0x21fc60
    
    # intro
    print("FIN_U_M CALIBRATION for channel %i" % channel)
    pmu_ch = pmu.channels[channel]
    
    OFFSET  = pmu_ch.read_dac("Offset")
    FIN_U_M = pmu_ch.read_dac("FIN_U", "M")
    
    # setup SMU
    keithley.display.screen = keithley.display.SMUA
    keithley.display.smua.measure.func = keithley.display.MEASURE_DCVOLTS
    
    keithley.smua.measure.autorangev = keithley.smua.AUTORANGE_ON
    keithley.smua.measure.nplc = MEAS_NPLC # 0.001 to 25

    keithley.smua.source.func = keithley.smua.OUTPUT_DCAMPS
    keithley.smua.source.leveli = 0
    keithley.smua.source.limiti = 1e-3
    keithley.smua.source.limitv = 20
    keithley.smua.source.output = keithley.smua.OUTPUT_ON
    
    

    pmu_ch.pmu_reg = pmu_reg_channel_on_sys
    
    # zero calibration
    dac_max = 0xFFFF
    v_high = pmu_calc.dac_to_v(dac_max, OFFSET)
    
    # set pos cal value
    pmu_ch.write_dac(dac_max, dac_reg = "FIN_U")
    sleep(wait_before_measure)
    meas_max = measure(keithley, measure_delay, measure_count)
    
    NEW_FIN_U_M = round(FIN_U_M * (v_high/meas_max))

    print("\tNEW_FIN_M = FIN_U_M * (V_HIGH_SET / V_HIGH_MEAS)")
    print("\t%i = %i * (%sV / %sV)" %(
        NEW_FIN_U_M,
        FIN_U_M,
        si_format(v_high, precision=3),
        si_format(meas_max, precision=3)
    ))
    
    if NEW_FIN_U_M > 0xFFFF:
        NEW_FIN_U_M = 0xFFFF
    
    pmu_ch.write_dac(data = NEW_FIN_U_M, dac_reg = "FIN_U", reg = "M")
    pmu_ch.write_dac(dac_max, dac_reg = "FIN_U")
    sleep(wait_before_measure)
    meas_max_cal = measure(keithley, measure_delay, measure_count)
    print("\tV_MAX after Cal = %sV" % si_format(meas_max_cal, precision=3))
    
    pmu_ch.pmu_reg = pmu_reg_channel_off
    keithley.smua.source.output = keithley.smua.OUTPUT_OFF
    
    return NEW_FIN_U_M

def cal_FIN_I_C(
            pmu,
            keithley,
            channel,
            range,
            wait_before_measure = 0.5,
            measure_delay=MEAS_SLEEP,
            measure_count=MEAS_COUNT):
    
    # reset PMU-Regs
    pmu.write_all_PMU_REGS(pmu_reg_channel_off)
    
    # intro
    print("FIN_I_C CALIBRATION for channel %i @ %sA" % (channel, range))
    pmu_ch = pmu.channels[channel]
    
    LSB_SIZE_I = 4.5 * pmu_def.VREF \
              / ((2**16) * pmu_def.CURRENT_RANGES[range]["RSens"]*pmu_def.MI_GAIN)
    FIN_I_C = pmu_ch.read_dac("FIN_I_"+range, "C")
    keithley.display.screen = keithley.display.SMUA
    keithley.display.smua.measure.func = keithley.display.MEASURE_DCAMPS
    
    keithley.smua.measure.autorangei = keithley.smua.AUTORANGE_ON
    keithley.smua.measure.autorangev = keithley.smua.AUTORANGE_ON
    keithley.smua.measure.rangei = pmu_def.CURRENT_RANGES[range]["MaxVal"]
    keithley.smua.measure.nplc = MEAS_NPLC # 0.001 to 25

    keithley.smua.source.func = keithley.smua.OUTPUT_DCVOLTS
    keithley.smua.source.levelv = 0
    keithley.smua.source.limiti = pmu_def.CURRENT_RANGES[range]["MaxVal"]
    keithley.smua.source.limitv = 13
    keithley.smua.source.output = keithley.smua.OUTPUT_ON
    
    pmu.change_sys_ctrl({
        "DUTGND/CH" : 1,
        "INT10K"    : 1,
        "TMP ENABLE": 1,
        "TMP"       : 3 # Thermal shutdown at 100°C
    })

    pmu_ch.change_pmu_reg({
        "CH EN": 1,     #Channel enable
        "FORCE": 1,     #FI
        "SS0"  : 1,
        "SF0"  : 1,
        "C"    : pmu_def.CURRENT_RANGES[range]["C"],     #80mA Range
        "FIN"  : 1
    })
    pmu_reg_channel_on_sys = pmu_ch.pmu_reg
    # zero calibration
    dac_zero = 0x8000
    
    # set pos cal value
    pmu_ch.write_dac(dac_zero, dac_reg = "FIN_I_"+range)
    sleep(wait_before_measure)
    meas_zero = -measure(keithley, measure_delay, measure_count, "i")
    
    NEW_FIN_I_C = round(FIN_I_C - (meas_zero/LSB_SIZE_I))
    
    print("\tNEW_FIN_C = FIN_C - (Zero_offset / LSB)")
    print("\t%i = %i - (%sA / %sA)" %(
        NEW_FIN_I_C,
        FIN_I_C,
        si_format(meas_zero, precision=3),
        si_format(LSB_SIZE_I, precision=3)
    ))
    
    pmu_ch.write_dac(data = NEW_FIN_I_C, dac_reg = "FIN_I_"+range, reg = "C")
    pmu_ch.write_dac(dac_zero, dac_reg = "FIN_I_"+range)
    pmu_ch.pmu_reg = pmu_reg_channel_off
    pmu_ch.pmu_reg = pmu_reg_channel_on_sys
    
    sleep(wait_before_measure)
    meas_zero_cal = -measure(keithley, measure_delay, measure_count, "i")
    print("\tOffset after Cal = %sA" % si_format(meas_zero_cal, precision=3))
    
    pmu_ch.pmu_reg = pmu_reg_channel_off
    keithley.smua.source.output = keithley.smua.OUTPUT_OFF
    
    return NEW_FIN_I_C

def cal_FIN_I_M(
            pmu,
            keithley,
            channel,
            range,
            wait_before_measure = 0.5,
            measure_delay=MEAS_SLEEP,
            measure_count=MEAS_COUNT):
    
    # reset PMU-Regs
    pmu.write_all_PMU_REGS(pmu_reg_channel_off)
    
    # intro
    print("FIN_I_M CALIBRATION for channel %i @ %sA" % (channel, range))
    pmu_ch = pmu.channels[channel]
    
    FIN_I_M = pmu_ch.read_dac("FIN_I_"+range, "M")
    
    # setup SMU
    keithley.display.screen = keithley.display.SMUA
    keithley.display.smua.measure.func = keithley.display.MEASURE_DCAMPS
    keithley.smua.measure.autorangei = keithley.smua.AUTORANGE_ON
    keithley.smua.measure.autorangev = keithley.smua.AUTORANGE_ON
    keithley.smua.measure.nplc = MEAS_NPLC # 0.001 to 25

    keithley.smua.source.func = keithley.smua.OUTPUT_DCVOLTS
    keithley.smua.source.levelv = 0
    keithley.smua.source.limiti = pmu_def.CURRENT_RANGES[range]["MaxVal"] * 1.5
    keithley.smua.source.limitv = 13
    keithley.smua.source.output = keithley.smua.OUTPUT_ON
    
    
    pmu.change_sys_ctrl({
        "DUTGND/CH" : 1,
        "INT10K"    : 1,
        "TMP ENABLE": 1,
        "TMP"       : 3 # Thermal shutdown at 100°C
    })

    pmu_ch.change_pmu_reg({
        "CH EN": 1,     #Channel enable
        "FORCE": 1,     #FI
        "SS0"  : 1,
        "SF0"  : 1,
        "C"    : pmu_def.CURRENT_RANGES[range]["C"],     #80mA Range
        "FIN"  : 1
    })
    pmu_reg_channel_on_sys = pmu_ch.pmu_reg
    
    # zero calibration
    dac_max = 0xFFFF
    i_high = pmu_calc.dac_to_i(dac_max, range)
    
    # set pos cal value
    pmu_ch.write_dac(dac_max, dac_reg = "FIN_I_"+range)
    sleep(wait_before_measure)
    meas_max = -measure(keithley, measure_delay, measure_count, "i")
    
    # NEW_FIN_I_M = round(FIN_I_M * ((i_high/meas_max)+1) / 2)

    # print("\tNEW_FIN_I_M = FIN_I_M * ((I_HIGH_SET / I_HIGH_MEAS) + 1) / 2")
    # print("\t%i = %i * ((%sA / %sA)+ 1 ) / 2" %(
    
    NEW_FIN_I_M = round(FIN_I_M * (i_high/meas_max))

    print("\tNEW_FIN_I_M = FIN_I_M * (I_HIGH_SET / I_HIGH_MEAS)")
    print("\t%i = %i * (%sA / %sA)" %(
        NEW_FIN_I_M,
        FIN_I_M,
        si_format(i_high, precision=3),
        si_format(meas_max, precision=3)
    ))
    
    if NEW_FIN_I_M > 0xFFFF:
        NEW_FIN_I_M = 0xFFFF
    
    pmu_ch.write_dac(data = NEW_FIN_I_M, dac_reg = "FIN_I_"+range, reg = "M")
    pmu_ch.write_dac(dac_max, dac_reg = "FIN_I_"+range)
    pmu_ch.pmu_reg = pmu_reg_channel_off
    pmu_ch.pmu_reg = pmu_reg_channel_on_sys
    
    sleep(wait_before_measure)
    meas_max_cal = -measure(keithley, measure_delay, measure_count,"i")
    print("\tV_MAX after Cal = %sA" % si_format(meas_max_cal, precision=3))
    
    pmu_ch.pmu_reg = pmu_reg_channel_off
    keithley.smua.source.output = keithley.smua.OUTPUT_OFF
    
    return NEW_FIN_I_M

def cal_CL_U_C(
            pmu,
            keithley,
            channel,
            range,
            clamp_side,
            current_factor=0.5,
            wait_before_measure = 0.5,
            measure_delay=MEAS_SLEEP,
            measure_count=MEAS_COUNT):
    
    # reset PMU-Regs
    pmu.write_all_PMU_REGS(pmu_reg_channel_off)
    pmu_ch = pmu.channels[channel]
    
    I_RANGE_DEFS = pmu_def.CURRENT_RANGES[range]
    
    LSB_SIZE_V = 4.5 * pmu_def.VREF / (2**16)
    OFFSET = pmu_ch.read_dac("Offset")
    CL_U_C = pmu_ch.read_dac("CL%s_U" % clamp_side, "C")
    
    # intro
    print("CL%s_U_C CALIBRATION for channel %i @ %sA" % (clamp_side, channel, range))

    
    # setup SMU
    keithley.display.screen = keithley.display.SMUA
    keithley.display.smua.measure.func = keithley.display.MEASURE_DCVOLTS
    keithley.smua.measure.autorangei = keithley.smua.AUTORANGE_ON
    keithley.smua.measure.autorangev = keithley.smua.AUTORANGE_ON
    keithley.smua.measure.nplc = MEAS_NPLC # 0.001 to 25

    keithley.smua.source.func = keithley.smua.OUTPUT_DCAMPS
    keithley.smua.source.leveli = 0
    keithley.smua.source.limiti = I_RANGE_DEFS["MaxVal"] * 1.5
    keithley.smua.source.limitv = 20
    keithley.smua.source.output = keithley.smua.OUTPUT_ON
    
    
    pmu.change_sys_ctrl({
        "DUTGND/CH" : 1,
        "INT10K"    : 1,
        "TMP ENABLE": 1,
        "TMP"       : 3 # Thermal shutdown at 100°C
    })
    
    sleep(0.1)

    pmu_ch.change_pmu_reg({
        "CH EN": 1,     #Channel enable
        "FORCE": 1,     #FI_CLV
        "SS0"  : 1,
        "SF0"  : 1,
        "CL"   : 1,
        "C"    : I_RANGE_DEFS["C"],     #80mA Range
        "FIN"  : 1
    })
    # sleep(0.5)
    # pmu_reg_channel_on_sys = pmu_ch.pmu_reg # hier springt camp raus ???
    
    if clamp_side == 'H':
        pmu_ch.write_dac(pmu_calc.i_to_dac(I_RANGE_DEFS["MaxVal"]*current_factor, range),"FIN_I_" + range)
        pmu_ch.write_dac(0,"CLL_U")
        dac_reg = "CLH_U"
    elif clamp_side == 'L':
        pmu_ch.write_dac(pmu_calc.i_to_dac((-1)*I_RANGE_DEFS["MaxVal"]*current_factor, range),"FIN_I_" + range)
        pmu_ch.write_dac(0xFFFF,"CLH_U")
        dac_reg = "CLL_U"
    else:
        raise ValueError("unknown clamp_side - should be 'H' or 'L'")
    
    # zero calibration
    dac_zero = pmu_calc.v_to_dac(0, OFFSET)
    pmu_ch.write_dac(dac_zero, dac_reg)
    sleep(wait_before_measure)
    meas_zero = measure(keithley, measure_delay, measure_count)
    
    NEW_CL_U_C = round(CL_U_C - (meas_zero/LSB_SIZE_V))

    print("\tNEW_CL%s_U_C = CL%s_U_C - (Zero_offset / LSB)" % (clamp_side, clamp_side))
    print("\t%i = %i - (%sV / %sV)" %(
        NEW_CL_U_C,
        CL_U_C,
        si_format(meas_zero, precision=3),
        si_format(LSB_SIZE_V, precision=3)
    ))
    
    pmu_ch.write_dac(data = NEW_CL_U_C, dac_reg = dac_reg, reg = "C")
    pmu_ch.write_dac(dac_zero, dac_reg)
    # pmu_ch.pmu_reg = pmu_reg_channel_off
    # pmu_ch.pmu_reg = pmu_reg_channel_on_sys
    
    sleep(wait_before_measure)
    meas_zero_cal = measure(keithley, measure_delay, measure_count)
    print("\tOffset after Cal = %sV" % si_format(meas_zero_cal, precision=3))
    
    pmu_ch.pmu_reg = pmu_reg_channel_off
    keithley.smua.source.output = keithley.smua.OUTPUT_OFF
    
    return NEW_CL_U_C

def cal_CL_U_M(
            pmu,
            keithley,
            channel,
            range,
            clamp_side,
            current_factor=0.5,
            wait_before_measure = 0.5,
            measure_delay=MEAS_SLEEP,
            measure_count=MEAS_COUNT):
    
    # reset PMU-Regs
    pmu.write_all_PMU_REGS(pmu_reg_channel_off)
    pmu_ch = pmu.channels[channel]
    
    I_RANGE_DEFS = pmu_def.CURRENT_RANGES[range]

    OFFSET = pmu_ch.read_dac("Offset")
    CL_U_M = pmu_ch.read_dac("CL%s_U" % clamp_side, "M")
    
    # intro
    print("CL%s_U_M CALIBRATION for channel %i @ %sA" % (clamp_side, channel, range))

    
    # setup SMU
    keithley.display.screen = keithley.display.SMUA
    keithley.display.smua.measure.func = keithley.display.MEASURE_DCVOLTS
    keithley.smua.measure.autorangei = keithley.smua.AUTORANGE_ON
    keithley.smua.measure.autorangev = keithley.smua.AUTORANGE_ON
    keithley.smua.measure.nplc = MEAS_NPLC # 0.001 to 25

    keithley.smua.source.func = keithley.smua.OUTPUT_DCAMPS
    keithley.smua.source.leveli = 0
    keithley.smua.source.limiti = I_RANGE_DEFS["MaxVal"] * 1.5
    keithley.smua.source.limitv = 20
    keithley.smua.source.output = keithley.smua.OUTPUT_ON
    
    
    pmu.change_sys_ctrl({
        "DUTGND/CH" : 1,
        "INT10K"    : 1,
        "TMP ENABLE": 1,
        "TMP"       : 3 # Thermal shutdown at 100°C
    })
    
    sleep(0.1)

    pmu_ch.change_pmu_reg({
        "CH EN": 1,     #Channel enable
        "FORCE": 1,     #FI_CLV
        "SS0"  : 1,
        "SF0"  : 1,
        "CL"   : 1,
        "C"    : I_RANGE_DEFS["C"],     #80mA Range
        "FIN"  : 1
    })
    # sleep(0.5)
    # pmu_reg_channel_on_sys = pmu_ch.pmu_reg # hier springt camp raus ???
    
    if clamp_side == 'H':
        pmu_ch.write_dac(pmu_calc.i_to_dac(I_RANGE_DEFS["MaxVal"]*current_factor, range),"FIN_I_" + range)
        pmu_ch.write_dac(0,"CLL_U")
        dac_reg = "CLH_U"
        dac_max = 0xFFFF
    elif clamp_side == 'L':
        pmu_ch.write_dac(pmu_calc.i_to_dac((-1)*I_RANGE_DEFS["MaxVal"]*current_factor, range),"FIN_I_" + range)
        pmu_ch.write_dac(0xFFFF,"CLH_U")
        dac_reg = "CLL_U"
        dac_max = 0x0
    else:
        raise ValueError("unknown clamp_side - should be 'H' or 'L'")
    
    # zero calibration
    v_high = pmu_calc.dac_to_v(dac_max, OFFSET)
    
    pmu_ch.write_dac(dac_max, dac_reg)
    sleep(wait_before_measure)
    meas_max = measure(keithley, measure_delay, measure_count)
    
    rel_error = (v_high/meas_max)
    
    NEW_CL_U_M = round(CL_U_M * (rel_error+1) / 2)

    print("\tNEW_CL%s_M = CL%s_U_M * ((V_HIGH_SET / V_HIGH_MEAS) + 1) / 2" % (clamp_side, clamp_side))
    print("\t%i = %i * ((%sV / %sV) + 1) / 2" %(
        NEW_CL_U_M,
        CL_U_M,
        si_format(v_high, precision=3),
        si_format(meas_max, precision=3)
    ))
    
    pmu_ch.write_dac(data = NEW_CL_U_M, dac_reg = dac_reg, reg = "M")
    pmu_ch.write_dac(dac_max, dac_reg)
    # pmu_ch.pmu_reg = pmu_reg_channel_off
    # pmu_ch.pmu_reg = pmu_reg_channel_on_sys
    
    sleep(wait_before_measure)
    meas_max_cal = measure(keithley, measure_delay, measure_count)
    print("\tV_MAX after Cal = %sV" % si_format(meas_max_cal, precision=3))
    
    pmu_ch.pmu_reg = pmu_reg_channel_off
    keithley.smua.source.output = keithley.smua.OUTPUT_OFF
    
    return NEW_CL_U_M

def cal_CL_I_C(
            pmu,
            keithley,
            channel,
            range,
            clamp_side,
            voltage=5.,
            wait_before_measure = 0.5,
            measure_delay=MEAS_SLEEP,
            measure_count=MEAS_COUNT):
    
    # reset PMU-Regs
    pmu.write_all_PMU_REGS(pmu_reg_channel_off)
    pmu_ch = pmu.channels[channel]
    
    I_RANGE_DEFS = pmu_def.CURRENT_RANGES[range]
    
    LSB_SIZE_I = 4.5 * pmu_def.VREF \
              / ((2**16) * pmu_def.CURRENT_RANGES[range]["RSens"]*pmu_def.MI_GAIN)
    OFFSET = pmu_ch.read_dac("Offset")
    CL_I_C = pmu_ch.read_dac("CL%s_I" % clamp_side, "C")
    
    # intro
    print("CL%s_I_C CALIBRATION for channel %i @ %sA" % (clamp_side, channel, range))

    
    # setup SMU
    keithley.display.screen = keithley.display.SMUA
    keithley.display.smua.measure.func = keithley.display.MEASURE_DCAMPS
    keithley.smua.measure.autorangei = keithley.smua.AUTORANGE_ON
    keithley.smua.measure.autorangev = keithley.smua.AUTORANGE_ON
    keithley.smua.measure.nplc = MEAS_NPLC # 0.001 to 25

    keithley.smua.source.func = keithley.smua.OUTPUT_DCVOLTS
    keithley.smua.source.levelv = 0
    keithley.smua.source.limiti = I_RANGE_DEFS["MaxVal"] * 1.5
    keithley.smua.source.limitv = 20
    keithley.smua.source.output = keithley.smua.OUTPUT_ON
    
    
    pmu.change_sys_ctrl({
        "DUTGND/CH" : 1,
        "INT10K"    : 1,
        "TMP ENABLE": 1,
        "TMP"       : 3 # Thermal shutdown at 100°C
    })
    
    sleep(0.1)

    pmu_ch.change_pmu_reg({
        "CH EN": 1,     #Channel enable
        "FORCE": 0,     #FV_CLI
        "SS0"  : 1,
        "SF0"  : 1,
        "CL"   : 1,
        "C"    : I_RANGE_DEFS["C"],     #80mA Range
        "FIN"  : 1
    })
    # sleep(0.5)
    # pmu_reg_channel_on_sys = pmu_ch.pmu_reg # hier springt camp raus ???
    
    if clamp_side == 'H':
        pmu_ch.write_dac(pmu_calc.v_to_dac(voltage, OFFSET),"FIN_U")
        pmu_ch.write_dac(0,"CLL_I")
        dac_reg = "CLH_I"
    elif clamp_side == 'L':
        pmu_ch.write_dac(pmu_calc.v_to_dac((-1)*voltage, OFFSET),"FIN_U")
        pmu_ch.write_dac(0xFFFF,"CLH_I")
        dac_reg = "CLL_I"
    else:
        raise ValueError("unknown clamp_side - should be 'H' or 'L'")
    
    # zero calibration
    dac_zero = pmu_calc.i_to_dac(0, range)
    pmu_ch.write_dac(dac_zero, dac_reg)
    sleep(wait_before_measure)
    meas_zero = -measure(keithley, measure_delay, measure_count, 'i')
    
    NEW_CL_I_C = round(CL_I_C - (meas_zero/LSB_SIZE_I))

    print("\tNEW_CL%s_I_C = CL%s_I_C - (Zero_offset / LSB)" % (clamp_side, clamp_side))
    print("\t%i = %i - (%sA / %sA)" %(
        NEW_CL_I_C,
        CL_I_C,
        si_format(meas_zero, precision=3),
        si_format(LSB_SIZE_I, precision=3)
    ))
    
    pmu_ch.write_dac(data = NEW_CL_I_C, dac_reg = dac_reg, reg = "C")
    pmu_ch.write_dac(dac_zero, dac_reg)
    # pmu_ch.pmu_reg = pmu_reg_channel_off
    # pmu_ch.pmu_reg = pmu_reg_channel_on_sys
    
    sleep(wait_before_measure)
    meas_zero_cal = -measure(keithley, measure_delay, measure_count, 'i')
    print("\tOffset after Cal = %sA" % si_format(meas_zero_cal, precision=3))
    
    pmu_ch.pmu_reg = pmu_reg_channel_off
    keithley.smua.source.output = keithley.smua.OUTPUT_OFF
    
    return NEW_CL_I_C

def cal_CL_I_M(
            pmu,
            keithley,
            channel,
            range,
            clamp_side,
            voltage=5.,
            wait_before_measure = 0.5,
            measure_delay=MEAS_SLEEP,
            measure_count=MEAS_COUNT):
    
    # reset PMU-Regs
    pmu.write_all_PMU_REGS(pmu_reg_channel_off)
    pmu_ch = pmu.channels[channel]
    I_RANGE_DEFS = pmu_def.CURRENT_RANGES[range]

    OFFSET = pmu_ch.read_dac("Offset")
    CL_I_M = pmu_ch.read_dac("CL%s_I" % clamp_side, "M")
    
    # intro
    print("CL%s_I_M CALIBRATION for channel %i @ %sA" % (clamp_side, channel, range))

    
    # setup SMU
    keithley.display.screen = keithley.display.SMUA
    keithley.display.smua.measure.func = keithley.display.MEASURE_DCAMPS
    keithley.smua.measure.autorangei = keithley.smua.AUTORANGE_ON
    keithley.smua.measure.autorangev = keithley.smua.AUTORANGE_ON
    keithley.smua.measure.nplc = MEAS_NPLC # 0.001 to 25

    keithley.smua.source.func = keithley.smua.OUTPUT_DCVOLTS
    keithley.smua.source.levelv = 0
    keithley.smua.source.limiti = I_RANGE_DEFS["MaxVal"] * 1.5
    keithley.smua.source.limitv = 15
    keithley.smua.source.output = keithley.smua.OUTPUT_ON
    
    
    pmu.change_sys_ctrl({
        "DUTGND/CH" : 1,
        "INT10K"    : 1,
        "TMP ENABLE": 1,
        "TMP"       : 3 # Thermal shutdown at 100°C
    })
    
    sleep(0.1)

    pmu_ch.change_pmu_reg({
        "CH EN": 1,     #Channel enable
        "FORCE": 0,     #FV_CLI
        "SS0"  : 1,
        "SF0"  : 1,
        "CL"   : 1,
        "C"    : I_RANGE_DEFS["C"],     #80mA Range
        "FIN"  : 1
    })
    # sleep(0.5)
    # pmu_reg_channel_on_sys = pmu_ch.pmu_reg # hier springt camp raus ???
    
    if clamp_side == 'H':
        pmu_ch.write_dac(pmu_calc.v_to_dac(voltage, OFFSET),"FIN_U")
        pmu_ch.write_dac(0,"CLL_I")
        dac_reg = "CLH_I"
        dac_max = 0xFFFF
    elif clamp_side == 'L':
        pmu_ch.write_dac(pmu_calc.v_to_dac((-1)*voltage, OFFSET),"FIN_U")
        pmu_ch.write_dac(0xFFFF,"CLH_I")
        dac_reg = "CLL_I"
        dac_max = 0x0
    else:
        raise ValueError("unknown clamp_side - should be 'H' or 'L'")
    
    # zero calibration
    i_high = pmu_calc.dac_to_i(dac_max, range)
    
    pmu_ch.write_dac(dac_max, dac_reg)
    sleep(wait_before_measure)
    meas_max = -measure(keithley, measure_delay, measure_count, 'i')
    
    rel_error = (i_high/meas_max)
    
    NEW_CL_I_M = round(CL_I_M * (rel_error+1) / 2)

    print("\tNEW_CL%s_I_M = CL%s_I_M * ((I_HIGH_SET / I_HIGH_MEAS) + 1) / 2" % (clamp_side, clamp_side))
    print("\t%i = %i * ((%sA / %sA) + 1) / 2" %(
        NEW_CL_I_M,
        CL_I_M,
        si_format(i_high, precision=3),
        si_format(meas_max, precision=3)
    ))
    
    pmu_ch.write_dac(data = NEW_CL_I_M, dac_reg = dac_reg, reg = "M")
    pmu_ch.write_dac(dac_max, dac_reg)
    # pmu_ch.pmu_reg = pmu_reg_channel_off
    # pmu_ch.pmu_reg = pmu_reg_channel_on_sys
    
    sleep(wait_before_measure)
    meas_max_cal = -measure(keithley, measure_delay, measure_count, 'i')
    print("\tI_MAX after Cal = %sA" % si_format(meas_max_cal, precision=3))
    
    pmu_ch.pmu_reg = pmu_reg_channel_off
    keithley.smua.source.output = keithley.smua.OUTPUT_OFF
    
    return NEW_CL_I_M

def calibrate(
            pmu,
            keithley,
            max_iterations = 20,
            accuracy = 1,
            reset_pmu=True,
            wait_before_measure=0.5,
            measure_delay=MEAS_SLEEP,
            measure_count=MEAS_COUNT):
    
    if reset_pmu:
        pmu.reset()
    cal_data = dict()
    CAL_M_DEFAULT = 0xFFFF
    CAL_C_DEFAULT = 0x8000
    new_FIN_M = 0
    # FIN_U
    for ch in range(4):
        if not reset_pmu:
            cal_data[str(ch)+"FIN_U_M"] = pmu.channels[ch].read_dac(dac_reg = "FIN_U", reg = "M")
            cal_data[str(ch)+"FIN_U_C"] = pmu.channels[ch].read_dac(dac_reg = "FIN_U", reg = "C")
        elif ch == 0:
            cal_data[str(ch)+"FIN_U_M"] = CAL_M_DEFAULT
            cal_data[str(ch)+"FIN_U_C"] = CAL_C_DEFAULT
        else:
            cal_data[str(ch)+"FIN_U_M"] = new_FIN_M
            pmu.channels[ch].write_dac(data = new_FIN_M, dac_reg = "FIN_U", reg = "M")
            cal_data[str(ch)+"FIN_U_C"] = new_FIN_C
            pmu.channels[ch].write_dac(data = new_FIN_C, dac_reg = "FIN_U", reg = "C")
            
        for _ in range(max_iterations):
            new_FIN_M = cal_FIN_U_M(pmu, keithley, ch, wait_before_measure, measure_delay, measure_count)
            new_FIN_C = cal_FIN_U_C(pmu, keithley, ch, wait_before_measure, measure_delay, measure_count)
            
            if abs(cal_data[str(ch)+"FIN_U_M"] - new_FIN_M) <= accuracy and\
               abs(cal_data[str(ch)+"FIN_U_C"] - new_FIN_C) <= accuracy :
                print("Calibration OK")
                break
            else:
                cal_data[str(ch)+"FIN_U_C"] = new_FIN_C
                cal_data[str(ch)+"FIN_U_M"] = new_FIN_M
        else:
            print("No ideal Calibration found")
            new_FIN_M = CAL_M_DEFAULT
            new_FIN_C = CAL_C_DEFAULT
    # FIN_I
    for r in pmu_def.I_RANGES:
        for ch in range(4):
            if not reset_pmu:
                cal_data[str(ch)+"FIN_I_M_"+r] = pmu.channels[ch].read_dac(dac_reg = "FIN_I_"+r, reg = "M")
                cal_data[str(ch)+"FIN_I_C_"+r] = pmu.channels[ch].read_dac(dac_reg = "FIN_I_"+r, reg = "C")
            else:
                cal_data[str(ch)+"FIN_I_M_"+r] = new_FIN_M
                pmu.channels[ch].write_dac(data = new_FIN_M, dac_reg = "FIN_I_"+r, reg = "M")
                cal_data[str(ch)+"FIN_I_C_"+r] = new_FIN_C
                pmu.channels[ch].write_dac(data = new_FIN_C, dac_reg = "FIN_I_"+r, reg = "C")
            
            for _ in range(max_iterations):
                new_FIN_M = cal_FIN_I_M(pmu, keithley, ch, r, wait_before_measure, measure_delay, measure_count)
                new_FIN_C = cal_FIN_I_C(pmu, keithley, ch, r, wait_before_measure, measure_delay, measure_count)
                if abs(cal_data[str(ch)+"FIN_I_M_"+r] - new_FIN_M) <= accuracy and\
                   abs(cal_data[str(ch)+"FIN_I_C_"+r] - new_FIN_C) <= accuracy:
                    print("Calibration OK")
                    break
                else:
                    cal_data[str(ch)+"FIN_I_M_"+r] = new_FIN_M
                    cal_data[str(ch)+"FIN_I_C_"+r] = new_FIN_C
            else:
                print("No ideal Calibration found")
                new_FIN_M = CAL_M_DEFAULT
                new_FIN_C = CAL_C_DEFAULT
                
    # CLL_U
    for ch in range(4):
        if not reset_pmu:
            cal_data[str(ch)+"CLL_U_M"] = pmu.channels[ch].read_dac(dac_reg = "CLL_U", reg = "M")
            cal_data[str(ch)+"CLL_U_C"] = pmu.channels[ch].read_dac(dac_reg = "CLL_U", reg = "C")
        elif ch == 0:
            cal_data[str(ch)+"CLL_U_M"] = CAL_M_DEFAULT
            cal_data[str(ch)+"CLL_U_C"] = CAL_C_DEFAULT
        else:
            cal_data[str(ch)+"CLL_U_M"] = new_CL_M
            pmu.channels[ch].write_dac(data = new_CL_M, dac_reg = "CLL_U", reg = "M")
            cal_data[str(ch)+"CLL_U_C"] = new_CL_C
            pmu.channels[ch].write_dac(data = new_CL_C, dac_reg = "CLL_U", reg = "C")
            
        for _ in range(max_iterations):
            new_CL_M = cal_CL_U_M(pmu, keithley, ch, "2m", "L", 0.5, wait_before_measure, measure_delay, measure_count)
            new_CL_C = cal_CL_U_C(pmu, keithley, ch, "2m", "L", 0.5, wait_before_measure, measure_delay, measure_count)
            
            if abs(cal_data[str(ch)+"CLL_U_M"] - new_CL_M) <= accuracy and\
               abs(cal_data[str(ch)+"CLL_U_C"] - new_CL_C) <= accuracy :
                print("Calibration OK")
                break
            else:
                cal_data[str(ch)+"CLL_U_M"] = new_CL_M
                cal_data[str(ch)+"CLL_U_C"] = new_CL_C
        else:
            print("No ideal Calibration found")
            new_CL_M = CAL_M_DEFAULT
            new_CL_C = CAL_C_DEFAULT

    # CLH_U
    for ch in range(4):
        if not reset_pmu:
            cal_data[str(ch)+"CLH_U_M"] = pmu.channels[ch].read_dac(dac_reg = "CLH_U", reg = "M")
            cal_data[str(ch)+"CLH_U_C"] = pmu.channels[ch].read_dac(dac_reg = "CLH_U", reg = "C")
        else:
            cal_data[str(ch)+"CLH_U_M"] = new_CL_M
            pmu.channels[ch].write_dac(data = new_CL_M, dac_reg = "CLH_U", reg = "M")
            cal_data[str(ch)+"CLH_U_C"] = new_CL_C
            pmu.channels[ch].write_dac(data = new_CL_C, dac_reg = "CLH_U", reg = "C")
            
        for _ in range(max_iterations):
            new_CL_M = cal_CL_U_M(pmu, keithley, ch, "2m", "H", 0.5, wait_before_measure, measure_delay, measure_count)
            new_CL_C = cal_CL_U_C(pmu, keithley, ch, "2m", "H", 0.5, wait_before_measure, measure_delay, measure_count)
            if abs(cal_data[str(ch)+"CLH_U_M"] - new_CL_M) <= accuracy and\
               abs(cal_data[str(ch)+"CLH_U_C"] - new_CL_C) <= accuracy :
                print("Calibration OK")
                break
            else:
                cal_data[str(ch)+"CLH_U_M"] = new_CL_M
                cal_data[str(ch)+"CLH_U_C"] = new_CL_C
        else:
            print("No ideal Calibration found")
            new_CL_M = CAL_M_DEFAULT
            new_CL_C = CAL_C_DEFAULT
            
    # CLL_I
    for ch in range(4):
        if not reset_pmu:
            cal_data[str(ch)+"CLL_I_M"] = pmu.channels[ch].read_dac(dac_reg = "CLL_I", reg = "M")
            cal_data[str(ch)+"CLL_I_C"] = pmu.channels[ch].read_dac(dac_reg = "CLL_I", reg = "C")
        elif ch == 0:
            cal_data[str(ch)+"CLL_I_M"] = CAL_M_DEFAULT
            cal_data[str(ch)+"CLL_I_C"] = CAL_C_DEFAULT
        else:
            cal_data[str(ch)+"CLL_I_M"] = new_CL_M
            pmu.channels[ch].write_dac(data = new_CL_M, dac_reg = "CLL_I", reg = "M")
            cal_data[str(ch)+"CLL_I_C"] = new_CL_C
            pmu.channels[ch].write_dac(data = new_CL_C, dac_reg = "CLL_I", reg = "C")
            
        for _ in range(max_iterations):
            new_CL_M = cal_CL_I_M(pmu, keithley, ch, "2m", "L", 5, wait_before_measure, measure_delay, measure_count)
            new_CL_C = cal_CL_I_C(pmu, keithley, ch, "2m", "L", 5, wait_before_measure, measure_delay, measure_count)
            
            if abs(cal_data[str(ch)+"CLL_I_M"] - new_CL_M) <= accuracy and\
               abs(cal_data[str(ch)+"CLL_I_C"] - new_CL_C) <= accuracy :
                print("Calibration OK")
                break
            else:
                cal_data[str(ch)+"CLL_I_M"] = new_CL_M
                cal_data[str(ch)+"CLL_I_C"] = new_CL_C
        else:
            print("No ideal Calibration found")
            new_CL_M = CAL_M_DEFAULT
            new_CL_C = CAL_C_DEFAULT

    # CLH_U
    for ch in range(4):
        if not reset_pmu:
            cal_data[str(ch)+"CLH_I_M"] = pmu.channels[ch].read_dac(dac_reg = "CLH_I", reg = "M")
            cal_data[str(ch)+"CLH_I_C"] = pmu.channels[ch].read_dac(dac_reg = "CLH_I", reg = "C")
        else:
            cal_data[str(ch)+"CLH_I_M"] = new_CL_M
            pmu.channels[ch].write_dac(data = new_CL_M, dac_reg = "CLH_I", reg = "M")
            cal_data[str(ch)+"CLH_I_C"] = new_CL_C
            pmu.channels[ch].write_dac(data = new_CL_C, dac_reg = "CLH_I", reg = "C")
            
        for _ in range(max_iterations):
            new_CL_M = cal_CL_I_M(pmu, keithley, ch, "2m", "H", 5, wait_before_measure, measure_delay, measure_count)
            new_CL_C = cal_CL_I_C(pmu, keithley, ch, "2m", "H", 5, wait_before_measure, measure_delay, measure_count)
            
            if abs(cal_data[str(ch)+"CLH_I_M"] - new_CL_M) <= accuracy and\
               abs(cal_data[str(ch)+"CLH_I_C"] - new_CL_C) <= accuracy :
                print("Calibration OK")
                break
            else:
                cal_data[str(ch)+"CLH_I_M"] = new_CL_M
                cal_data[str(ch)+"CLH_I_C"] = new_CL_C
        else:
            print("No ideal Calibration found")
            new_CL_M = CAL_M_DEFAULT
            new_CL_C = CAL_C_DEFAULT
            
    return cal_data

def measure(
        keithley,
        meas_delay=MEAS_SLEEP,
        meas_count=MEAS_COUNT,
        meas_func="v"):
    
    values = list()
    if meas_func == "v":
        meas_func = keithley.smua.measure.v
    elif meas_func == "i":
        meas_func = keithley.smua.measure.i
    else:
        raise ValueError("unsopported measurement function")

    for _ in range(meas_count):
        values.append(meas_func())
        sleep(meas_delay)
    
    values = np.array(values)
    if values.max() - values.min() > 0.1:
        print("Values have high deviation (%f)" % values.std()) # warning only for voltage yet
    return values.mean()
        
def measureFV(pmu, keithley, ch, num=100, measure_delay = 0.1):
    pmu.write_all_PMU_REGS(0x1E060)
    # keithley.smua.measure.autorangev    = keithley.smua.AUTORANGE_ON
    keithley.display.screen = keithley.display.SMUA
    keithley.display.smua.measure.func = keithley.display.MEASURE_DCVOLTS
    
    keithley.smua.measure.rangev        = 20
    keithley.smua.measure.autorangei    = keithley.smua.AUTORANGE_ON
    keithley.smua.measure.nplc          = MEAS_NPLC
    
    keithley.smua.source.func           = keithley.smua.OUTPUT_DCAMPS
    keithley.smua.source.leveli         = 0
    keithley.smua.source.limiti         = 1e-3
    keithley.smua.source.limitv         = 20
    keithley.smua.source.output         = keithley.smua.OUTPUT_ON
    
    pmu_ch = pmu.channels[ch]
    pmu_ch.pmu_reg = 0x21fc60
    
    measure_data = list()
    measure_points = np.linspace(0, 0xFFFF, num)
    output_voltage = list()

    # for d in tqdm(measure_points):
    for d in measure_points:
        pmu_ch.write_dac(
            data= round(d),
            dac_reg="FIN_U",
            reg="X1"
        )
        output_voltage.append(pmu_calc.dac_to_v(d, pmu_ch.read_dac("Offset")))
        sleep(measure_delay)
        measure_data.append(keithley.smua.measure.v())
        
    pmu_ch.pmu_reg = pmu_reg_channel_off
    keithley.smua.source.output = keithley.smua.OUTPUT_OFF
    
    
    return np.array(output_voltage), np.array(measure_data)

def measureFI(pmu, keithley, ch, range, num=100, measure_delay = 0.1):
    I_RANGE_DEFS = pmu_def.CURRENT_RANGES[range]
    
    pmu.write_all_PMU_REGS(0x1E060)
    
    # keithley.smua.measure.autorangev    = keithley.smua.AUTORANGE_ON
    keithley.display.screen = keithley.display.SMUA
    keithley.display.smua.measure.func = keithley.display.MEASURE_DCAMPS
    
    keithley.smua.measure.rangev        = 20
    keithley.smua.measure.rangei        = I_RANGE_DEFS["MaxVal"] * 1.5
    keithley.smua.source.func           = keithley.smua.OUTPUT_DCVOLTS
    keithley.smua.source.leveli         = 0
    keithley.smua.source.limiti         = I_RANGE_DEFS["MaxVal"] * 1.5
    keithley.smua.source.limitv         = 15
    keithley.smua.source.output         = keithley.smua.OUTPUT_ON
    
    pmu_ch = pmu.channels[ch]
    
    pmu.change_sys_ctrl({
        "DUTGND/CH" : 1,
        "INT10K"    : 1,
        "TMP ENABLE": 1,
        "TMP"       : 3 # Thermal shutdown at 100°C
    })
    
    pmu_ch.change_pmu_reg({
        "CH EN": 1,     #Channel enable
        "FORCE": 1,     #FI
        "SS0"  : 1,
        "SF0"  : 1,
        "C"    : I_RANGE_DEFS["C"],
        "FIN"  : 1
    })
    
    
    measure_data = list()
    measure_points = np.linspace(0, 0xFFFF, num)
    output_current = list()

    # for d in tqdm(measure_points):
    for d in measure_points:
        pmu_ch.write_dac(
            data= round(d),
            dac_reg="FIN_I_"+range,
            reg="X1"
        )
        output_current.append(pmu_calc.dac_to_i(d, range))
        sleep(measure_delay)
        measure_data.append(keithley.smua.measure.i())
        
    pmu_ch.pmu_reg = pmu_reg_channel_off
    keithley.smua.source.output = keithley.smua.OUTPUT_OFF
    
    return np.array(output_current), np.array(measure_data)

def measureCL_U(pmu, keithley, ch, range, current_range_factor=0.5, clamp_side='H', overlap=0.5, num=100, measure_delay = 0.1):
    I_RANGE_DEFS = pmu_def.CURRENT_RANGES[range]
    pmu_ch = pmu.channels[ch]
    ch_offset = pmu_ch.read_dac("Offset")
    
    pmu.write_all_PMU_REGS(0x1E060)
    
    keithley.display.screen                = keithley.display.SMUA
    keithley.display.smua.measure.func     = keithley.display.MEASURE_DCVOLTS
    
    keithley.smua.measure.nplc             = MEAS_NPLC
    keithley.smua.measure.autorangei       = keithley.smua.AUTORANGE_ON
    keithley.smua.measure.autorangev       = keithley.smua.AUTORANGE_ON

    keithley.smua.source.limiti            = I_RANGE_DEFS["MaxVal"]*2
    keithley.smua.source.limitv            = 20
    keithley.smua.source.func              = keithley.smua.OUTPUT_DCAMPS
    keithley.smua.source.leveli            = 0
    keithley.smua.source.output            = keithley.smua.OUTPUT_ON
    
    pmu.change_sys_ctrl({
        "DUTGND/CH" : 1,
        "INT10K"    : 1,
        "TMP ENABLE": 1,
        "TMP"       : 3 # Thermal shutdown at 100°C
    })
    
    pmu_ch.change_pmu_reg({
        "CH EN": 1,     #Channel enable
        "FORCE": 1,     #FI
        "SS0"  : 1,
        "SF0"  : 1,
        "FIN"  : 1,
        "C"    : I_RANGE_DEFS["C"],
        "CL"   : 1
    })
    
    measure_data = list()
    if clamp_side == 'H':
        measure_points = np.linspace(round(0x8000-(0x8000*overlap)), 0xFFFF, num)
        pmu_ch.write_dac(pmu_calc.i_to_dac(I_RANGE_DEFS["MaxVal"]*current_range_factor, range),"FIN_I_" + range)
        pmu_ch.write_dac(0,"CLL_U")
        dac_reg = "CLH_U"
    elif clamp_side == 'L':
        measure_points = np.linspace(round(0x7FFF+(0x8000*overlap)), 0, num)
        pmu_ch.write_dac(pmu_calc.i_to_dac((-1)*I_RANGE_DEFS["MaxVal"]*current_range_factor, range),"FIN_I_" + range)
        pmu_ch.write_dac(0xFFFF,"CLH_U")
        dac_reg = "CLL_U"
    else:
        measure_points = list()
        raise ValueError("unknown clamp_side - should be 'H' or 'L'")

    output_voltage = list()
    #set limit
    
    for d in measure_points:
        pmu_ch.write_dac(
            data= round(d),
            dac_reg=dac_reg,
            reg="X1"
        )
        output_voltage.append(pmu_calc.dac_to_v(d, ch_offset))
        sleep(measure_delay)
        measure_data.append(keithley.smua.measure.v())
        
    pmu_ch.pmu_reg = pmu_reg_channel_off
    keithley.smua.source.output = keithley.smua.OUTPUT_OFF
    
    return np.array(output_voltage), np.array(measure_data)

def measureCL_I(pmu, keithley, ch, range, voltage=5, clamp_side='H', overlap=0.5, num=100, measure_delay = 0.1):
    I_RANGE_DEFS = pmu_def.CURRENT_RANGES[range]
    pmu_ch = pmu.channels[ch]
    ch_offset = pmu_ch.read_dac("Offset")
    
    pmu.write_all_PMU_REGS(0x1E060)
    
    keithley.display.screen                = keithley.display.SMUA
    keithley.display.smua.measure.func     = keithley.display.MEASURE_DCAMPS
    
    keithley.smua.measure.nplc             = MEAS_NPLC
    keithley.smua.measure.autorangei       = keithley.smua.AUTORANGE_ON
    keithley.smua.measure.autorangev       = keithley.smua.AUTORANGE_ON

    keithley.smua.source.limiti            = I_RANGE_DEFS["MaxVal"]*2
    keithley.smua.source.limitv            = 20
    keithley.smua.source.func              = keithley.smua.OUTPUT_DCVOLTS
    keithley.smua.source.levelv            = 0
    keithley.smua.source.output            = keithley.smua.OUTPUT_ON
    
    pmu.change_sys_ctrl({
        "DUTGND/CH" : 1,
        "INT10K"    : 1,
        "TMP ENABLE": 1,
        "TMP"       : 3 # Thermal shutdown at 100°C
    })
    
    pmu_ch.change_pmu_reg({
        "CH EN": 1,     #Channel enable
        "FORCE": 0,     #FV
        "SS0"  : 1,
        "SF0"  : 1,
        "FIN"  : 1,
        "C"    : I_RANGE_DEFS["C"],
        "CL"   : 1
    })
    
    measure_data = list()
    if clamp_side == 'H':
        measure_points = np.linspace(round(0x8000-(0x8000*overlap)), 0xFFFF, num)
        pmu_ch.write_dac(pmu_calc.v_to_dac(voltage, ch_offset),"FIN_U")
        pmu_ch.write_dac(0,"CLL_I")
        dac_reg = "CLH_I"
    elif clamp_side == 'L':
        measure_points = np.linspace(round(0x7FFF+(0x8000*overlap)), 0, num)
        pmu_ch.write_dac(pmu_calc.v_to_dac(-voltage, ch_offset),"FIN_U")
        pmu_ch.write_dac(0xFFFF,"CLH_I")
        dac_reg = "CLL_I"
    else:
        raise ValueError("unknown clamp_side - should be 'H' or 'L'")

    output_current = list()
    #set limit
    
    
    for d in measure_points:
        pmu_ch.write_dac(
            data= round(d),
            dac_reg=dac_reg,
            reg="X1"
        )
        output_current.append(pmu_calc.dac_to_i(d, range))
        sleep(measure_delay)
        measure_data.append(keithley.smua.measure.i())
        
    pmu_ch.pmu_reg = pmu_reg_channel_off
    keithley.smua.source.output = keithley.smua.OUTPUT_OFF
    
    return np.array(output_current), np.array(measure_data)