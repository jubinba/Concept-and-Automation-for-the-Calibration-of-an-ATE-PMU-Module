from time import sleep
from tqdm import tqdm
import numpy as np
from si_prefix import si_format

from . import pmu_calc_jub
from . import pmu_def_jub
from.pmu_cal import measure
from decimal import Decimal, getcontext, ROUND_HALF_UP
from scipy import interpolate


MEAS_COUNT = 5
MEAS_SLEEP = 0.1
MEAS_NPLC = 1

pmu_reg_channel_off = 0x1E060

def cal_jub_FIN_U_C(
            p,
            keithley,
            channel,
            wait_before_measure = 0.5,
            measure_delay=MEAS_SLEEP,
            measure_count=MEAS_COUNT):
    
    # reset PMU-Regs
    p.write_all_PMU_REGS(pmu_reg_channel_off)
    pmu_reg_channel_on_sys = 0x21fc60
    
    # intro
    print("FIN_U_C CALIBRATION for channel %i" % channel)
    pmu_ch = p.channels[channel]
    
    LSB_SIZE_V = 4.5 * pmu_def_jub.VREF / (2**16)
    OFFSET  = pmu_ch.read_dac("Offset")
    
    FIN_U_C = pmu_ch.read_dac("FIN_U", "C")
    
    dac_one =  FIN_U_C
    
    
    # setup SMU
    keithley.display.screen = keithley.display.SMUA
    keithley.display.smua.measure.func = keithley.display.MEASURE_DCVOLTS
    
    #keithley.smua.sense = keithley.smua.SENSE_REMOTE
    keithley.smua.measure.autorangev = keithley.smua.AUTORANGE_ON
    keithley.smua.measure.nplc = MEAS_NPLC # 0.001 to 25

    keithley.smua.source.func = keithley.smua.OUTPUT_DCAMPS
    keithley.smua.source.leveli = 0
    keithley.smua.source.limiti = 1e-3
    keithley.smua.source.limitv = 20
    keithley.smua.source.output = keithley.smua.OUTPUT_ON
    
    

    pmu_ch.pmu_reg = pmu_reg_channel_on_sys
    
    # zero calibration
    # dac_zero = pmu_calc_jub.v_to_dac(0, OFFSET)
    
    x1_val = 32768
    v_req = pmu_calc_jub.dac_to_v(x1_val, OFFSET)

    
    # set pos cal value
    pmu_ch.write_dac(x1_val, dac_reg = "FIN_U")
    sleep(wait_before_measure)
    meas_one = measure(keithley, measure_delay, measure_count)
    #print("\nmeas_zero",meas_zero)
    #print("\nLSB_SIZE_V",LSB_SIZE_V)

    NEW_FIN_U_C = 0xFFFF
    
    #print("\nNEW_FIN_U_C",NEW_FIN_U_C)
    
    print("\tNEW_FIN_C , FIN_C ")
    print("\t%i = %i )" %(
        NEW_FIN_U_C,
        FIN_U_C
        
        ))
    
    pmu_ch.write_dac(data = NEW_FIN_U_C, dac_reg = "FIN_U", reg = "C")
    pmu_ch.write_dac(x1_val, dac_reg = "FIN_U")
    sleep(wait_before_measure)
    meas_zero = measure(keithley, measure_delay, measure_count)
    print("\tOffset after Cal = %sV" % si_format(meas_zero, precision=3))
    
    
    dac_zero = NEW_FIN_U_C
    dac_one = FIN_U_C
    volt_zero = meas_zero
    volt_one = meas_one
    
    print("\ndacc_zero",dac_zero)
    print("\ndac_one",dac_one)
    print("\nvolt_zero",volt_zero)
    print("\nvolt_one",volt_one)
    print("\nv_req",v_req)

    x_zero_c,y_zero_c,x_one_c,y_one_c,y_required_c = dac_zero,volt_zero,dac_one,volt_one,v_req
       
        
    #Calibration using linear interpolation for "C"
    # Calculate the numerator and denominator for interpolation
    numerator = (x_one_c - x_zero_c) * (y_required_c - y_zero_c)
    denominator = y_one_c - y_zero_c

    #Perform interpolation
    x_required_c = round(x_zero_c + numerator / denominator)

    print(f"The offset for output voltage {y_required_c} is approximately {x_required_c:.15f}.")

    NEW_FIN_U_C_FINAL = x_required_c


    pmu_ch.write_dac(data = NEW_FIN_U_C_FINAL, dac_reg = "FIN_U", reg = "C")
    pmu_ch.write_dac(x1_val, dac_reg = "FIN_U")
    sleep(wait_before_measure)
    meas_zero_cal_final = measure(keithley, measure_delay, measure_count)
    print("\tOffset after Cal = %sV" % si_format(meas_zero_cal_final, precision=3))

    new_FIN_C = NEW_FIN_U_C_FINAL




    pmu_ch.pmu_reg = pmu_reg_channel_off
    keithley.smua.source.output = keithley.smua.OUTPUT_OFF



    return new_FIN_C

def cal_jub_FIN_U_M(
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
    FIN_U_M =  pmu_ch.read_dac("FIN_U","M")
    
    #FIN_U_M = 65206
    print("\nFIN_U_M",FIN_U_M)

    #print("\nFIN_U_M",FIN_U_M)
    
    # setup SMU
    keithley.display.screen = keithley.display.SMUA
    keithley.display.smua.measure.func = keithley.display.MEASURE_DCVOLTS
    
    keithley.smua.measure.autorangev = keithley.smua.AUTORANGE_ON
    keithley.smua.measure.nplc = MEAS_NPLC # 0.001 to 25


    #keithley.smua.sense = keithley.smua.SENSE_REMOTE
    keithley.smua.source.func = keithley.smua.OUTPUT_DCAMPS
    keithley.smua.source.leveli = 0
    keithley.smua.source.limiti = 1e-3
    keithley.smua.source.limitv = 20
    keithley.smua.source.output = keithley.smua.OUTPUT_ON
    
    

    pmu_ch.pmu_reg = pmu_reg_channel_on_sys
    
    # Finding the slope for M = 65535
    dac_max = 65535
    v_high = pmu_calc_jub.dac_to_v(dac_max, OFFSET)
    
    # set pos cal value
    pmu_ch.write_dac(data = FIN_U_M, dac_reg = "FIN_U", reg = "M")
    pmu_ch.write_dac(dac_max, dac_reg = "FIN_U")
    sleep(wait_before_measure)
    meas_max = measure(keithley, measure_delay, measure_count)
    #print("\nmeas_max",meas_max)

    dac_min = 32768
    v_low = pmu_calc_jub.dac_to_v(dac_min,OFFSET)
    pmu_ch.write_dac(data = FIN_U_M, dac_reg = "FIN_U", reg = "M")
    pmu_ch.write_dac(dac_min, dac_reg = "FIN_U")
    sleep(wait_before_measure)
    meas_min =  measure(keithley, measure_delay, measure_count)

    # SLOPE(65535)
    x1,y1 = dac_max, meas_max
    x2,y2 = dac_min,meas_min

    
    slope_Max = (y2 - y1)/(x2-x1)
    print("\nslope_Max",slope_Max)

    #SLOPE(Ideal)
    x1_ideal, y1_ideal = (dac_max,v_high)
    x2_ideal, y2_ideal = (dac_min,v_low)

    
    slope_Ideal = (y2_ideal-y1_ideal)/(x2_ideal-x1_ideal)
    print("\nslope_Ideal",slope_Ideal)

    # Finding the slope for M = 32768

    NEW_FIN_U_M = 0x8000

    
    # For dac_max
    pmu_ch.write_dac(data = NEW_FIN_U_M, dac_reg = "FIN_U", reg = "M")
    pmu_ch.write_dac(dac_max, dac_reg = "FIN_U")
    sleep(wait_before_measure)
    meas_max_new = measure(keithley, measure_delay, measure_count)

    # For dac_min
    
    pmu_ch.write_dac(data = NEW_FIN_U_M, dac_reg = "FIN_U", reg = "M")
    pmu_ch.write_dac(dac_min, dac_reg = "FIN_U")
    sleep(wait_before_measure)
    meas_min_new = measure(keithley, measure_delay, measure_count)

    x1_new, y1_new = (dac_max, meas_max_new)
    x2_new ,y2_new = ( dac_min,meas_min_new)

    slope_Min = (y2_new-y1_new)/(x2_new-x1_new)
    print("\nslope_Min",slope_Min)


    

   
   # Known x and y values
    x = np.array([ slope_Min, slope_Max])
    y = np.array([dac_min,dac_max])
 
    # Fit a linear line to the known data points
    model = np.polyfit(x, y, 1)
 
    # New x values for which to extrapolate the y values
    new_x = np.array([ slope_Ideal])
 
    # Extrapolate the y values for the new x values
    new_y = np.polyval(model, new_x)
 
    print(new_y)
    print("\nOffset after Interpolation",new_y)
    NEW_FIN_U_M_FINAL= new_y

    pmu_ch.write_dac(data = NEW_FIN_U_M_FINAL, dac_reg = "FIN_U", reg = "M")
    pmu_ch.write_dac(dac_max, dac_reg = "FIN_U")
    sleep(wait_before_measure)
    meas_max_cal_FINAL = measure(keithley, measure_delay, measure_count)
    print("\tV_MAX after Cal = %sV" % si_format(meas_max_cal_FINAL, precision=3))


    pmu_ch.pmu_reg = pmu_reg_channel_off
    keithley.smua.source.output = keithley.smua.OUTPUT_OFF

    return NEW_FIN_U_M_FINAL



def cal_jub_FIN_I_M(
        p,
        k,
        ch,
        range,
        wait_before_measure = 0.5,
        measure_delay = MEAS_SLEEP,
        measure_count = MEAS_COUNT):
    
    p.write_all_PMU_REGS(pmu_reg_channel_off)

    print("FIN_I_M CALIBRATION for channel %i @ %sA" % (ch, range))
    pmu_ch = p.channels[ch]

    FIN_I_M = pmu_ch.read_dac("FIN_I_"+range,"M")
    

    # setup SMU
    k.display.screen = k.display.SMUA
    k.display.smua.measure.func = k.display.MEASURE_DCAMPS
    k.smua.measure.autorangei = k.smua.AUTORANGE_ON
    k.smua.measure.autorangev = k.smua.AUTORANGE_ON
    k.smua.measure.nplc = MEAS_NPLC # 0.001 to 25

    k.smua.source.func = k.smua.OUTPUT_DCVOLTS
    k.smua.source.levelv = 0
    k.smua.source.limiti = pmu_def_jub.CURRENT_RANGES[range]["MaxVal"] * 1.5
    k.smua.source.limitv = 13
    k.smua.source.output = k.smua.OUTPUT_ON

    p.change_sys_ctrl({
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
        "C"    : pmu_def_jub.CURRENT_RANGES[range]["C"],     #80mA Range
        "FIN"  : 1
    })
    pmu_reg_channel_on_sys = pmu_ch.pmu_reg

                                                                                #Preparing for INTERPOLATION
                                                                                #For M = FIM_I_M read the measured voltage for X1 = 0x8000 and 0XFFFF
                                                                                # Also using eqaution, find the Ideal voltage For X1 = 0X0000 and 0XFFFF
                                                                                # For M = 0x0000 read the measure voltage for X1 = 0X0000 and 0XFFFF
                                                                                # Using results fro M=FIN_U_M amd M = 0X0000 , do interpolation to find M that can be used to get ideal measurement
    ######################################################################################################################################################################################################################   
    ##################-------For M = FIN_I_M(65535)(default)-----------############################################################################################################################################################
    ######################################################################################################################################################################################################################


    #Doing Measurement for X1 = 0XFFFF

    X1_val_max = 0xBFFF #0XFFFF
    volt_max_for_ideal = pmu_calc_jub.dac_to_i(X1_val_max,range)

    
    pmu_ch.write_dac(X1_val_max, dac_reg = "FIN_I_"+range)
    sleep(wait_before_measure)
    volt_max_for_M_0XFFFF = -measure(k,measure_delay,measure_count,"i")


    # Doing Measurement for X1 = 0X8000



    x1_val_min = 0x4000
    volt_min_for_ideal = pmu_calc_jub. dac_to_i(x1_val_min,range)


    pmu_ch.write_dac(x1_val_min,dac_reg = "FIN_I_"+range)
    sleep(wait_before_measure)
    volt_min_for_M_0XFFFF = -measure(k,measure_delay,measure_count,"i")

    #........................................................................................................................................................................................................................#

    # Arranging Variables for Interpolation

    #For Slope for M = 65535
    (x_one_for_M_65535,y_one_for_M_65535) = (x1_val_min,volt_min_for_M_0XFFFF)
    (x_two_for_M_65535,y_two_for_M_65535) = (X1_val_max,volt_max_for_M_0XFFFF)

    #For Slope For Ideal M using the equation
    (x_one_for_M_Ideal,y_one_for_M_Ideal) = (x1_val_min,volt_min_for_ideal)
    (x_two_for_M_Ideal,y_two_for_M_Ideal) = (X1_val_max,volt_max_for_ideal)

    # From the above equations, Find the slope for M = 65535 and For Ideal M.
    # Perform Interplolation using Slope Of M = 65535; Slope of M = 32768 and Slope for Ideal M

    ######################################################################################################################################################################################################################   
    ##################-------For M = FIN_I_M(32768)-----------############################################################################################################################################################
    ######################################################################################################################################################################################################################

    # Writing FIN_I_M as 32768
    pmu_ch.write_dac(data = 0X8000, dac_reg = "FIN_I_"+range, reg = "M")

    #Performing Measurement for X1 = 0XFFFF
    pmu_ch.write_dac(X1_val_max, dac_reg = "FIN_I_"+range)
    sleep(wait_before_measure)
    volt_max_for_M_0X8000 = -measure(k,measure_delay,measure_count,"i")

    #Performing Measurement for X1 = 0X8000

    pmu_ch.write_dac(x1_val_min,dac_reg = "FIN_I_"+range)
    sleep(wait_before_measure)
    volt_min_for_M_0X8000 = -measure(k,measure_delay,measure_count,"i")

    #.........................................................................................................................................................................................................................#

    #Arranging Variables for Interpolation

    # For Calculating Slope for M = 32768

    (x_one_for_M_32768,y_one_for_M_32768) = (x1_val_min,volt_min_for_M_0X8000)
    (x_two_for_M_32768,y_two_for_M_32768) = (X1_val_max,volt_max_for_M_0X8000)

    #...........................................................................................................................................................................................................................#
    # 3 Slopes required for interpolation

    slope_Max = (y_two_for_M_65535 - y_one_for_M_65535) / (x_two_for_M_65535-x_one_for_M_65535)
    print("\nslope_Max",slope_Max)

    slope_Min = (y_two_for_M_32768 - y_one_for_M_32768)/(x_two_for_M_32768 - x_one_for_M_32768)
    print("\nslope_Min",slope_Min)

    slope_Ideal = (y_two_for_M_Ideal-y_one_for_M_Ideal)/(x_two_for_M_Ideal - x_one_for_M_Ideal)
    print("\nslope_Ideal",slope_Ideal)

    #......................................................................................................................................................................................................................................
    # Performing Interpolation

    dac_min = 32768
    dac_max = 65535

    x = np.array([ slope_Min, slope_Max])       # Comparing For Interpolation
    y = np.array([dac_min,dac_max])
 
    
    model = np.polyfit(x, y, 1)                 # Fit a linear line to the known data points
 
    
    new_x = np.array([ slope_Ideal])             # New x values for which to extrapolate the y values
 
   
    new_y = np.polyval(model, new_x)             # Extrapolate the y values for the new x values
 
    print(new_y)
    print("\nGain after Interpolation",new_y)
    NEW_FIN_I_M_FINAL = new_y

    if NEW_FIN_I_M_FINAL > 0XFFFF:
        NEW_FIN_I_M_FINAL = 0XFFFF

    pmu_ch.write_dac(data = NEW_FIN_I_M_FINAL, dac_reg = "FIN_I_"+range, reg = "M")
    pmu_ch.write_dac(X1_val_max, dac_reg = "FIN_I_"+range)

    pmu_ch.pmu_reg = pmu_reg_channel_off
    pmu_ch.pmu_reg = pmu_reg_channel_on_sys

    sleep(wait_before_measure)
    meas_max_cal_FINAL = -measure(k, measure_delay, measure_count,"i")
    print("\tV_MAX after Cal = %sV" % si_format(meas_max_cal_FINAL, precision=3))


    pmu_ch.pmu_reg = pmu_reg_channel_off
    k.smua.source.output = k.smua.OUTPUT_OFF

    return NEW_FIN_I_M_FINAL

def cal_jub_FIN_I_C_without_slope_interpolation(
        p,
        k,
        ch,
        range,
        wait_before_measure = 0.5,
        measure_delay =MEAS_SLEEP,
        measure_count = MEAS_COUNT):
    
    p.write_all_PMU_REGS(pmu_reg_channel_off)

    print("FIN_I_C CALIBRATION for channel %i @ %sA" % (ch, range))
    pmu_ch = p.channels[ch]

    k.display.screen = k.display.SMUA
    k.display.smua.measure.func = k.display.MEASURE_DCAMPS
    
    k.smua.measure.autorangei = k.smua.AUTORANGE_ON
    k.smua.measure.autorangev = k.smua.AUTORANGE_ON
    k.smua.measure.rangei = pmu_def_jub.CURRENT_RANGES[range]["MaxVal"]
    k.smua.measure.nplc = MEAS_NPLC # 0.001 to 25

    k.smua.source.func = k.smua.OUTPUT_DCVOLTS
    k.smua.source.levelv = 0
    k.smua.source.limiti = pmu_def_jub.CURRENT_RANGES[range]["MaxVal"]
    k.smua.source.limitv = 13
    k.smua.source.output = k.smua.OUTPUT_ON

    p.change_sys_ctrl({
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
        "C"    : pmu_def_jub.CURRENT_RANGES[range]["C"],     #80mA Range
        "FIN"  : 1
    })

    pmu_reg_channel_on_sys = pmu_ch.pmu_reg


    ######################################################################################################################################################################################################################   
    ##################-------For M = FIN_I_C(32768)(default)-----------############################################################################################################################################################
    ######################################################################################################################################################################################################################

    #Performing Measurement for X1 = 0X8000
    FIN_I_C = pmu_ch.read_dac("FIN_I_"+range, "C")
    x1_val= 0x2000 #0xAAD8 #0x9C90#0x8E48#0xFFFF #0x8000 #0x2000 #  #0x8000 #0X4000

    volt_for_ideal = pmu_calc_jub.dac_to_i(x1_val,range)

    # M Register is by default 32768 

    pmu_ch.write_dac(x1_val,dac_reg = "FIN_I_"+range) # Writing x1 register
    sleep(wait_before_measure)
    volt_for_C_0x8000 = -measure(k, measure_delay, measure_count, "i")
    
    


    ######################################################################################################################################################################################################################   
    ##################-------For M = FIN_I_C(65535)-----------############################################################################################################################################################
    ######################################################################################################################################################################################################################

    # Writing FIN_I_C as 65535

    NEW_FIN_I_C = 0xFFFF
    pmu_ch.write_dac(data = NEW_FIN_I_C, dac_reg = "FIN_I_"+range, reg = "C") # Writing C Register

    #Performing Measurement for X1 = 0X8000
    pmu_ch.write_dac(x1_val, dac_reg = "FIN_I_"+range) # Writing x1 register
    pmu_ch.pmu_reg = pmu_reg_channel_off
    pmu_ch.pmu_reg = pmu_reg_channel_on_sys

    sleep(wait_before_measure)
    volt_for_C_0xFFFF = -measure(k, measure_delay, measure_count, "i")

   
    #......................................................................................................................................................................................................................
    
    # Arranging Variables for Interpolation

    dac_zero = NEW_FIN_I_C
    dac_one = FIN_I_C
    volt_zero = volt_for_C_0xFFFF
    volt_one = volt_for_C_0x8000
    v_req = volt_for_ideal

    print("\ndacc_zero",dac_zero)
    print("\ndac_one",dac_one)
    print("\nvolt_zero",volt_zero)
    print("\nvolt_one",volt_one)
    print("\nv_req",v_req)

    x_zero_c,y_zero_c,x_one_c,y_one_c,y_required_c = dac_zero,volt_zero,dac_one,volt_one,v_req

    #Calibration using linear interpolation for "C"
    # Calculate the numerator and denominator for interpolation
    numerator = (x_one_c - x_zero_c) * (y_required_c - y_zero_c)
    denominator = y_one_c - y_zero_c

    #Perform interpolation
    x_required_c = round(x_zero_c + numerator / denominator)

    print(f"The offset for output voltage {y_required_c} is approximately {x_required_c:.15f}.")

    NEW_FIN_I_C_FINAL = x_required_c

    pmu_ch.write_dac(data = NEW_FIN_I_C_FINAL, dac_reg = "FIN_I_"+range, reg = "C") 
    pmu_ch.write_dac(x1_val, dac_reg = "FIN_I_"+range)
    pmu_ch.pmu_reg = pmu_reg_channel_off
    pmu_ch.pmu_reg = pmu_reg_channel_on_sys

    sleep(wait_before_measure) 

    meas_max_cal_FINAL = -measure(k, measure_delay, measure_count, "i")
    print("\tV_MAX after Cal = %sV" % si_format(meas_max_cal_FINAL, precision=3))


    pmu_ch.pmu_reg = pmu_reg_channel_off
    k.smua.source.output = k.smua.OUTPUT_OFF


    return NEW_FIN_I_C_FINAL

def cal_jub_CL_I_M(
        p,
        k,
        ch,
        range,
        clamp_side,
        voltage = 5.,
        wait_before_measure = 0.5,
        measure_delay = MEAS_SLEEP,
        measure_count = MEAS_COUNT):
    
    # reset PMU-Regs
    p.write_all_PMU_REGS(pmu_reg_channel_off)
    pmu_ch = p.channels[ch]
    I_RANGE_DEFS = pmu_def_jub.CURRENT_RANGES[range]

    OFFSET = pmu_ch.read_dac("Offset")
    CL_I_M = pmu_ch.read_dac("CL%s_I" % clamp_side, "M")

    # intro
    print("CL%s_I_M CALIBRATION for channel %i @ %sA" % (clamp_side, ch, range))

    # setup SMU
    k.display.screen = k.display.SMUA
    k.display.smua.measure.func = k.display.MEASURE_DCAMPS
    k.smua.measure.autorangei = k.smua.AUTORANGE_ON
    k.smua.measure.autorangev = k.smua.AUTORANGE_ON
    k.smua.measure.nplc = MEAS_NPLC # 0.001 to 25

    k.smua.source.func = k.smua.OUTPUT_DCVOLTS
    k.smua.source.levelv = 0
    k.smua.source.limiti = I_RANGE_DEFS["MaxVal"] * 1.5
    k.smua.source.limitv = 15
    k.smua.source.output = k.smua.OUTPUT_ON

    p.change_sys_ctrl({
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

    if clamp_side == 'H':
        pmu_ch.write_dac(pmu_calc_jub.v_to_dac(voltage, OFFSET),"FIN_U")
        pmu_ch.write_dac(0,"CLL_I")
        dac_reg = "CLH_I"
        x1_val_max = 0xFFFF
        x1_val_min = 0X8000
    elif clamp_side == 'L':
        pmu_ch.write_dac(pmu_calc_jub.v_to_dac((-1)*voltage, OFFSET),"FIN_U")
        pmu_ch.write_dac(0xFFFF,"CLH_I")
        dac_reg = "CLL_I"
        x1_val_max =  0X8000
        x1_val_min = 0x0
    else:
        raise ValueError("unknown clamp_side - should be 'H' or 'L'")
    
    ######################################################################################################################################################################################################################   
    ##################-------For M = CL_I_M(65535)-----------#############################################################################################################################################################
    ######################################################################################################################################################################################################################

    #Ideal_maximum_and_minimum_current

    current_max_for_M_ideal = pmu_calc_jub.dac_to_i(x1_val_max,range)
    current_min_for_M_ideal = pmu_calc_jub.dac_to_i(x1_val_min,range)

    # Doing Measurement when X1 is x1_val_max(0XFFFF)

    pmu_ch.write_dac(x1_val_max,dac_reg)
    sleep(wait_before_measure)
    current_max_for_M_0XFFFF = -measure(k, measure_delay, measure_count, "i")

    # Doing Measurement when  X1 is x1_val_min

    pmu_ch.write_dac(x1_val_min,dac_reg)
    sleep(wait_before_measure)
    current_min_for_M_0XFFFF = -measure(k,measure_delay,measure_count, "i")

    #.....................................................................................................................................................................................................................
    # Arranging for Interpolation

    (x_one_for_M_65535,y_one_for_M_65535) = (x1_val_min,current_min_for_M_0XFFFF)
    (x_two_for_M_65535,y_two_for_M_65535) = (x1_val_max,current_max_for_M_0XFFFF)


    (x_one_for_M_Ideal,y_one_for_M_Ideal) = (x1_val_min,current_min_for_M_ideal)
    (x_two_for_M_Ideal,y_two_for_M_Ideal) = (x1_val_max,current_max_for_M_ideal)

    ######################################################################################################################################################################################################################   
    ##################-------For M = NEW_CL_I_M(32768)-----------#############################################################################################################################################################
    ######################################################################################################################################################################################################################

    NEW_CL_I_M = 0x8000
    pmu_ch.write_dac(data = NEW_CL_I_M,dac_reg = dac_reg,reg = "M")


    # Doing Measurement when X1 is x1_val_max(0XFFFF)

    pmu_ch.write_dac(x1_val_max,dac_reg)
    sleep(wait_before_measure)
    current_max_for_M_0X8000 = -measure(k, measure_delay, measure_count, "i")

    # Doing Measurement when  X1 is x1_val_min
    pmu_ch.write_dac(x1_val_min,dac_reg)
    sleep(wait_before_measure)
    current_min_for_M_0X8000 = -measure(k,measure_delay,measure_count, "i")


    #.....................................................................................................................................................................................................................
    # Arranging for Interpolation

    (x_one_for_M_32768 , y_one_for_M_32768) = (x1_val_min,current_min_for_M_0X8000)
    (x_two_for_M_32768 , y_two_for_M_32768) = (x1_val_max,current_max_for_M_0X8000)


    #....................................................................................................................................................................................................................................
    # 3 Slopes required for interpolation

    slope_Max = (y_two_for_M_65535 - y_one_for_M_65535) / (x_two_for_M_65535-x_one_for_M_65535)
    print("\nslope_Max",slope_Max)

    slope_Min = (y_two_for_M_32768-y_one_for_M_32768)/(x_two_for_M_32768-x_one_for_M_32768)
    print("\nslope_Min",slope_Min)

    slope_Ideal = (y_two_for_M_Ideal-y_one_for_M_Ideal)/(x_two_for_M_Ideal-x_one_for_M_Ideal)
    print("\nslope_Ideal",slope_Ideal)
    #.....................................................................................................................................................................................................................

    

    # Performing Interpolation

    dac_min = NEW_CL_I_M
    dac_max = CL_I_M

    x = np.array([ slope_Min, slope_Max])    # Comparing for Interpolation
    y = np.array([dac_min,dac_max])

    
    model = np.polyfit(x, y, 1)              # Fit a linear line to the known data points
 
    
    new_x = np.array([ slope_Ideal])         # New x values for which to extrapolate the y values
 
    
    new_y = np.polyval(model, new_x)         # Extrapolate the y values for the new x values
 
    print(new_y)
    print("\nOffset after Interpolation",new_y)
    NEW_CL_I_M_FINAL= new_y

    pmu_ch.write_dac(data = NEW_CL_I_M_FINAL, dac_reg = dac_reg, reg = "M")
    pmu_ch.write_dac(dac_max, dac_reg )


    sleep(wait_before_measure)
    meas_max_cal_FINAL = measure(k, measure_delay, measure_count)
    print("\tV_MAX after Cal = %sV" % si_format(meas_max_cal_FINAL, precision=3))


    pmu_ch.pmu_reg = pmu_reg_channel_off
    k.smua.source.output = k.smua.OUTPUT_OFF

    return NEW_CL_I_M_FINAL

def cal_jub_CL_I_C(
        p,
        k,
        ch,
        range,
        clamp_side,
        voltage=5.,
        wait_before_measure = 0.5,
        measure_delay=MEAS_SLEEP,
        measure_count=MEAS_COUNT):
    
    # reset PMU-Regs
    p.write_all_PMU_REGS(pmu_reg_channel_off)
    pmu_ch = p.channels[ch]

    I_RANGE_DEFS = pmu_def_jub.CURRENT_RANGES[range]

    OFFSET = pmu_ch.read_dac("Offset")
    CL_I_C = pmu_ch.read_dac("CL%s_I" % clamp_side, "C")

    # intro
    print("CL%s_I_C CALIBRATION for channel %i @ %sA" % (clamp_side, ch, range))


    # SMU SETUP
    k.display.screen = k.display.SMUA
    k.display.smua.measure.func = k.display.MEASURE_DCAMPS
    k.smua.measure.autorangei = k.smua.AUTORANGE_ON
    k.smua.measure.autorangev = k.smua.AUTORANGE_ON
    k.smua.measure.nplc = MEAS_NPLC # 0.001 to 25

    k.smua.source.func = k.smua.OUTPUT_DCVOLTS
    k.smua.source.levelv = 0
    k.smua.source.limiti = I_RANGE_DEFS["MaxVal"] * 1.5
    k.smua.source.limitv = 20
    k.smua.source.output = k.smua.OUTPUT_ON

    p.change_sys_ctrl({
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

    if clamp_side == 'H':
        pmu_ch.write_dac(pmu_calc_jub.v_to_dac(voltage, OFFSET),"FIN_U")
        pmu_ch.write_dac(0,"CLL_I")
        dac_reg = "CLH_I"
    elif clamp_side == 'L':
        pmu_ch.write_dac(pmu_calc_jub.v_to_dac((-1)*voltage, OFFSET),"FIN_U")
        pmu_ch.write_dac(0xFFFF,"CLH_I")
        dac_reg = "CLL_I"
    else:
        raise ValueError("unknown clamp_side - should be 'H' or 'L'")
    
    x1_val = 0x8000


    # Ideal Value Requied
    current_for_ideal = pmu_calc_jub.dac_to_i(x1_val,range)

    ######################################################################################################################################################################################################################   
    ##################-------For C = CL_I_C(32768)(default)-----------############################################################################################################################################################
    ######################################################################################################################################################################################################################

    # Doing Measurement for x1_val

    pmu_ch.write_dac(x1_val,dac_reg)
    sleep(wait_before_measure)
    current_for_C_0x8000 = -measure(k, measure_delay, measure_count, "i")

    ######################################################################################################################################################################################################################   
    ##################-------For C = NEW_CL_I_C(0xFFFF)-----------#############################################################################################################################################################
    ######################################################################################################################################################################################################################

    NEW_CL_I_C = 0xFFFF
    pmu_ch.write_dac(data = NEW_CL_I_C,dac_reg = dac_reg,reg = "C")


    # Doing Measurement for x1_val

    pmu_ch.write_dac(x1_val,dac_reg)
    sleep(wait_before_measure)
    current_for_C_0xFFFF = -measure(k, measure_delay, measure_count, "i")

    #......................................................................................................................................................................................................................
    
    # Arranging Variables for Interpolation
    dac_zero = NEW_CL_I_C
    dac_one = CL_I_C
    volt_zero = current_for_C_0xFFFF
    volt_one = current_for_C_0x8000
    v_req = current_for_ideal

    print("\ndacc_zero",dac_zero)
    print("\ndac_one",dac_one)
    print("\nvolt_zero",volt_zero)
    print("\nvolt_one",volt_one)
    print("\nv_req",v_req)

    x_zero_c,y_zero_c,x_one_c,y_one_c,y_required_c = dac_zero,volt_zero,dac_one,volt_one,v_req

    #Calibration using linear interpolation for "C"
    # Calculate the numerator and denominator for interpolation
    numerator = (x_one_c - x_zero_c) * (y_required_c - y_zero_c)
    denominator = y_one_c - y_zero_c

    #Perform interpolation
    x_required_c = round(x_zero_c + numerator / denominator)

    print(f"The offset for output voltage {y_required_c} is approximately {x_required_c:.15f}.")

    NEW_CL_I_C_FINAL = x_required_c

    pmu_ch.write_dac(data = NEW_CL_I_C_FINAL, dac_reg = dac_reg, reg = "C")
    pmu_ch.write_dac(dac_zero, dac_reg)

    #pmu_ch.pmu_reg = pmu_reg_channel_off
    #pmu_ch.pmu_reg = pmu_reg_channel_on_sys

    sleep(wait_before_measure) 

    meas_max_cal_FINAL = -measure(k, measure_delay, measure_count, "i")
    print("\tV_MAX after Cal = %sV" % si_format(meas_max_cal_FINAL, precision=3))


    pmu_ch.pmu_reg = pmu_reg_channel_off
    k.smua.source.output = k.smua.OUTPUT_OFF


    return NEW_CL_I_C_FINAL





def cal_jub_CL_U_C(
        p,
        k,
        ch,
        range,
        clamp_side,
        current_factor=0.5,
        wait_before_measure = 0.5,
        measure_delay=MEAS_SLEEP,
        measure_count=MEAS_COUNT):
    
    p.write_all_PMU_REGS(pmu_reg_channel_off)
    pmu_ch = p.channels[ch]

    I_RANGE_DEFS = pmu_def_jub.CURRENT_RANGES[range]
    
    OFFSET = pmu_ch.read_dac("Offset")
    CL_U_C = pmu_ch.read_dac("CL%s_U" % clamp_side, "C")

    # intro
    print("CL%s_U_C CALIBRATION for channel %i @ %sA" % (clamp_side, ch, range))

    #setup SMU
    k.display.screen = k.display.SMUA
    k.display.smua.measure.func = k.display.MEASURE_DCVOLTS
    k.smua.measure.autorangei = k.smua.AUTORANGE_ON
    k.smua.measure.autorangev = k.smua.AUTORANGE_ON
    k.smua.measure.nplc = MEAS_NPLC # 0.001 to 25

    k.smua.source.func = k.smua.OUTPUT_DCAMPS
    k.smua.source.leveli = 0
    k.smua.source.limiti = I_RANGE_DEFS["MaxVal"] * 1.5
    k.smua.source.limitv = 20
    k.smua.source.output = k.smua.OUTPUT_ON

    p.change_sys_ctrl({
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

    if clamp_side == 'H':
        pmu_ch.write_dac(pmu_calc_jub.i_to_dac(I_RANGE_DEFS["MaxVal"]*current_factor, range),"FIN_I_" + range)
        pmu_ch.write_dac(0,"CLL_U")
        dac_reg = "CLH_U"
    elif clamp_side == 'L':
        pmu_ch.write_dac(pmu_calc_jub.i_to_dac((-1)*I_RANGE_DEFS["MaxVal"]*current_factor, range),"FIN_I_" + range)
        pmu_ch.write_dac(0xFFFF,"CLH_U")
        dac_reg = "CLL_U"
    else:
        raise ValueError("unknown clamp_side - should be 'H' or 'L'")
    
    ######################################################################################################################################################################################################################   
    ##################-------For C = CL_U_C(32768)(default)-----------############################################################################################################################################################
    ######################################################################################################################################################################################################################

    x1_val = 0X8000

    # Performing Measurement for Ideal Offset
    volt_for_C_ideal = pmu_calc_jub.dac_to_v(x1_val,OFFSET)

    # Performing Measurement for x1_val = 0X8000
    pmu_ch.write_dac(x1_val,dac_reg)
    sleep(wait_before_measure)
    volt_for_C_0X8000 = measure(k,measure_delay,measure_count)

    ######################################################################################################################################################################################################################   
    ##################-------For C = NEW_CL_U_C(65535)-----------############################################################################################################################################################
    ######################################################################################################################################################################################################################

    NEW_CL_U_C = 0XFFFF

    pmu_ch.write_dac(data = NEW_CL_U_C,dac_reg = dac_reg, reg = "C")

    # Performing Measurement for x1_val = 0X8000
    pmu_ch.write_dac(x1_val,dac_reg)

    sleep(wait_before_measure)
    volt_for_C_0XFFFF = measure(k,measure_delay,measure_count)

    #.........................................................................................................................................................................................................................
    
    # Arranging Variables for Interpolation

    dac_zero = NEW_CL_U_C
    dac_one = CL_U_C
    volt_zero = volt_for_C_0XFFFF
    volt_one = volt_for_C_0X8000
    v_req = volt_for_C_ideal

    print("\ndacc_zero",dac_zero)
    print("\ndac_one",dac_one)
    print("\nvolt_zero",volt_zero)
    print("\nvolt_one",volt_one)
    print("\nv_req",v_req)

    x_zero_c,y_zero_c,x_one_c,y_one_c,y_required_c = dac_zero,volt_zero,dac_one,volt_one,v_req

    #Calibration using linear interpolation for "C"
    # Calculate the numerator and denominator for interpolation
    numerator = (x_one_c - x_zero_c) * (y_required_c - y_zero_c)
    denominator = y_one_c - y_zero_c

    #Perform interpolation
    x_required_c = round(x_zero_c + numerator / denominator)

    print(f"The offset for output voltage {y_required_c} is approximately {x_required_c:.15f}.")

    NEW_CL_U_C = x_required_c

    pmu_ch.write_dac(data = NEW_CL_U_C, dac_reg = dac_reg, reg = "C")
    pmu_ch.write_dac(x1_val, dac_reg)
    
    sleep(wait_before_measure) 

    meas_max_cal_FINAL = measure(k, measure_delay, measure_count)
    print("\tV_MAX after Cal = %sV" % si_format(meas_max_cal_FINAL, precision=3))


    pmu_ch.pmu_reg = pmu_reg_channel_off
    k.smua.source.output = k.smua.OUTPUT_OFF


    return NEW_CL_U_C


def cal_jub_CL_U_M(
        p,
        k,
        ch,
        range,
        clamp_side,
        current_factor=  0.5,
        wait_before_measure = 0.5,
        measure_delay=MEAS_SLEEP,
        measure_count=MEAS_COUNT):
    
    p.write_all_PMU_REGS(pmu_reg_channel_off)
    pmu_ch = p.channels[ch]

    I_RANGE_DEFS = pmu_def_jub.CURRENT_RANGES[range]

    OFFSET = pmu_ch.read_dac("Offset")
    CL_U_M = pmu_ch.read_dac("CL%s_U" % clamp_side, "M")

    # intro
    print("CL%s_U_M CALIBRATION for channel %i @ %sA" % (clamp_side, ch, range))

    # SETUP SMU
    k.display.screen = k.display.SMUA
    k.display.smua.measure.func = k.display.MEASURE_DCVOLTS
    k.smua.measure.autorangei = k.smua.AUTORANGE_ON
    k.smua.measure.autorangev = k.smua.AUTORANGE_ON
    k.smua.measure.nplc = MEAS_NPLC # 0.001 to 25

    k.smua.source.func = k.smua.OUTPUT_DCAMPS
    k.smua.source.leveli = 0
    k.smua.source.limiti = I_RANGE_DEFS["MaxVal"] * 1.5
    k.smua.source.limitv = 20
    k.smua.source.output = k.smua.OUTPUT_ON

    p.change_sys_ctrl({
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

    if clamp_side == 'H':
        pmu_ch.write_dac(pmu_calc_jub.i_to_dac(I_RANGE_DEFS["MaxVal"]*current_factor, range),"FIN_I_" + range)
        pmu_ch.write_dac(0,"CLL_U")
        dac_reg = "CLH_U"
        x1_val_max = 0xFFFF
        x1_val_min = 0X8000
    elif clamp_side == 'L':
        pmu_ch.write_dac(pmu_calc_jub.i_to_dac((-1)*I_RANGE_DEFS["MaxVal"]*current_factor, range),"FIN_I_" + range)
        pmu_ch.write_dac(0xFFFF,"CLH_U")
        dac_reg = "CLL_U"
        x1_val_max = 0x0
        x1_val_min = 0X8000
    else:
        raise ValueError("unknown clamp_side - should be 'H' or 'L'")
    

    ######################################################################################################################################################################################################################   
    ##################-------For M = CL_U_M(65535)-----------#############################################################################################################################################################
    ######################################################################################################################################################################################################################

    #Ideal_maximum_and_minimum_volt
       
    volt_max_for_M_ideal = pmu_calc_jub.dac_to_v(x1_val_max, OFFSET)
    volt_min_for_M_ideal = pmu_calc_jub.dac_to_v(x1_val_min, OFFSET)

    # X1 = 0XFFFF

    pmu_ch.write_dac(x1_val_max, dac_reg)
    sleep(wait_before_measure)
    volt_max_for_M_0XFFFF = measure(k, measure_delay, measure_count)

    # X1 = 0X8000

    pmu_ch.write_dac(x1_val_min, dac_reg)
    sleep(wait_before_measure)
    volt_min_for_M_0XFFFF = measure(k, measure_delay, measure_count)

    #..........................................................................................................................................................................................................................
    #Arranging Variables for Interpolation

    (x_one_for_M_65535,y_one_for_M_65535) = (x1_val_min,volt_min_for_M_0XFFFF)
    (x_two_for_M_65535,y_two_for_M_65535) = (x1_val_max,volt_max_for_M_0XFFFF)

    (x_one_for_M_Ideal,y_one_for_M_Ideal) = (x1_val_min,volt_min_for_M_ideal)
    (x_two_for_M_Ideal,y_two_for_M_Ideal) = (x1_val_max,volt_max_for_M_ideal)

    ######################################################################################################################################################################################################################   
    ##################-------For M = NEW_CL_U_M(32768)-----------############################################################################################################################################################
    ######################################################################################################################################################################################################################


    NEW_CL_U_M = 0X8000

    
    pmu_ch.write_dac(data = NEW_CL_U_M, dac_reg = dac_reg, reg = "M")

    #X1 = 0XFFFF
    pmu_ch.write_dac(x1_val_max,dac_reg)
    sleep(wait_before_measure)
    volt_max_for_M_0X8000 =  measure(k, measure_delay, measure_count)

    #X1 = 0X8000
    pmu_ch.write_dac(x1_val_min,dac_reg)
    sleep(wait_before_measure)
    volt_min_for_M_0X8000 = measure(k, measure_delay, measure_count)

    #................................................................................................................................................................................................................................
    #Arranging Variables for Interpolation
    
    (x_one_for_M_32768,y_one_for_M_32768) = (x1_val_min,volt_min_for_M_0X8000)
    (x_two_for_M_32768,y_two_for_M_32768) = (x1_val_max,volt_max_for_M_0X8000)

    #....................................................................................................................................................................................................................................
    # 3 Slopes required for interpolation

    slope_Min = (y_two_for_M_65535 - y_one_for_M_65535) / (x_two_for_M_65535-x_one_for_M_65535)
    print("\nslope_Min",slope_Min)

    slope_Max = (y_two_for_M_32768-y_one_for_M_32768)/(x_two_for_M_32768-x_one_for_M_32768)
    print("\nslope_Max",slope_Max)

    slope_Ideal = (y_two_for_M_Ideal-y_one_for_M_Ideal)/(x_two_for_M_Ideal-x_one_for_M_Ideal)
    print("\nslope_Ideal",slope_Ideal)

    #.......................................................................................................................................................................................................................................
    # Performing Interpolation

    dac_min = CL_U_M
    dac_max = NEW_CL_U_M

    x = np.array([ slope_Min, slope_Max])    # Comparing for Interpolation
    y = np.array([dac_min,dac_max])

    
    model = np.polyfit(x, y, 1)              # Fit a linear line to the known data points
 
    
    new_x = np.array([ slope_Ideal])         # New x values for which to extrapolate the y values
 
    
    new_y = np.polyval(model, new_x)         # Extrapolate the y values for the new x values
 
    print(new_y)
    print("\nGain after Interpolation",new_y)
    NEW_CL_U_M_FINAL= new_y

    pmu_ch.write_dac(data = NEW_CL_U_M_FINAL, dac_reg = dac_reg, reg = "M")
    pmu_ch.write_dac(dac_max, dac_reg )


    sleep(wait_before_measure)
    meas_max_cal_FINAL = measure(k, measure_delay, measure_count)
    print("\tV_MAX after Cal = %sV" % si_format(meas_max_cal_FINAL, precision=3))


    pmu_ch.pmu_reg = pmu_reg_channel_off
    k.smua.source.output = k.smua.OUTPUT_OFF

    return NEW_CL_U_M_FINAL



def calibrate_jub(
        p,
        k,
        reset_pmu = True,
        max_iterations = 1,
        wait_before_measure =0.5,
        accuracy = 10,
        measure_delay = MEAS_SLEEP,
        measure_count = MEAS_COUNT):
    
    if reset_pmu == True:
        p.reset()
    cal_data = dict()
    CAL_M_DEFAULT = 0xFFFF
    CAL_C_DEFAULT =0x8000
    new_FIN_M = 0
   #new_FIN_C = 0 

    # FIN_U
    for ch in range(4):
        for _ in range(max_iterations):
            new_FIN_M = cal_jub_FIN_U_M(p, k, ch, wait_before_measure, measure_delay, measure_count)
            new_FIN_C = cal_jub_FIN_U_C(p, k, ch, wait_before_measure, measure_delay, measure_count)
       

        
       
        #     if abs(cal_data[str(ch)+"FIN_U_M"] - new_FIN_M) <= accuracy and\
        #        abs(cal_data[str(ch)+"FIN_U_C"] - new_FIN_C) <= accuracy :
        #         print("Calibration OK")
        #         break
        #     else:
        #         cal_data[str(ch)+"FIN_U_C"] = new_FIN_C
        #         cal_data[str(ch)+"FIN_U_M"] = new_FIN_M
        # else:
        #     print("No ideal Calibration found")
        #     new_FIN_M = CAL_M_DEFAULT
        #     new_FIN_C = CAL_C_DEFAULT

def test_calibrate_jub_FIN_I_M(
        p,
        k,
        reset_pmu = True,
        max_iterations = 1,
        wait_before_measure =0.5,
        accuracy = 10,
        measure_delay = MEAS_SLEEP,
        measure_count = MEAS_COUNT):
    
    if reset_pmu == True:
        p.reset()
    cal_data_jub = dict()
    CAL_M_DEFAULT = 0xFFFF
    CAL_C_DEFAULT =0x8000
    new_FIN_M = 0


    # FIN_U
    for ch in range(4):
        if not reset_pmu:
            cal_data_jub[str(ch)+"FIN_U_M"] = p.channels[ch].read_dac(dac_reg = "FIN_U", reg = "M")
            cal_data_jub[str(ch)+"FIN_U_C"] = p.channels[ch].read_dac(dac_reg = "FIN_U", reg = "C")
        elif ch == 0:
            cal_data_jub[str(ch)+"FIN_U_M"] = CAL_M_DEFAULT
            cal_data_jub[str(ch)+"FIN_U_C"] = CAL_C_DEFAULT
       
        for _ in range(max_iterations):
            new_FIN_M = cal_jub_FIN_U_M(p, k, ch, wait_before_measure, measure_delay, measure_count)
            new_FIN_C = cal_jub_FIN_U_C(p, k, ch, wait_before_measure, measure_delay, measure_count)
            cal_data_jub[str(ch)+"FIN_U_C"] = new_FIN_C
            cal_data_jub[str(ch)+"FIN_U_M"] = new_FIN_M
            print("\n debug print FIN_U_C ",cal_data_jub[str(ch)+"FIN_U_C"])
            print("\n debug print FIN_U_M ",cal_data_jub[str(ch)+"FIN_U_M"])

    # FIN_I        
    for r in pmu_def_jub.I_RANGES:
        for ch in range(4):
            if not reset_pmu:
                cal_data_jub[str(ch)+"FIN_I_M_"+r] = p.channels[ch].read_dac(dac_reg = "FIN_I_"+r, reg = "M")
                cal_data_jub[str(ch)+"FIN_I_C_"+r] = p.channels[ch].read_dac(dac_reg = "FIN_I_"+r, reg = "C")
            
            for _ in range(max_iterations):
                new_FIN_M = cal_jub_FIN_I_M(p, k, ch, r, wait_before_measure, measure_delay, measure_count)
                new_FIN_C = cal_jub_FIN_I_C_without_slope_interpolation(p,k,ch,r,wait_before_measure,measure_delay,measure_count)
                cal_data_jub[str(ch)+"FIN_I_M_"+r] = new_FIN_M
                cal_data_jub[str(ch)+"FIN_I_C_"+r] = new_FIN_C

    
    #CLL_U
    
    for r in pmu_def_jub.I_RANGES:
        for ch in range(4):
            if not reset_pmu:
                cal_data_jub[str(ch)+"CLL_U_M"] = p.channels[ch].read_dac(dac_reg = "CLL_U", reg = "M")
                cal_data_jub[str(ch)+"CLL_U_C"] = p.channels[ch].read_dac(dac_reg = "CLL_U", reg = "C")
            for _ in range(max_iterations):
                new_CL_M = cal_jub_CL_U_M(p, k, ch, r, "L", 0.5, wait_before_measure, measure_delay, measure_count)
                new_CL_C = cal_jub_CL_U_C(p, k, ch, r, "L", 0.5, wait_before_measure, measure_delay, measure_count)
                cal_data_jub[str(ch)+"CLL_U_M"+r] = new_CL_M
                cal_data_jub[str(ch)+"CLL_U_C"+r] = new_CL_C

    # avg_M = {}
    # avg_C = {}
    # for ch in range(4):
    #     M_L_values = [cal_data_jub[key] for key in cal_data_jub if key.startswith(str(ch) + "CLL_U_M")]
    #     C_L_values = [cal_data_jub[key] for key in cal_data_jub if key.startswith(str(ch) + "CLL_U_C")]
    #     print(f"M_values for channel{ch} :{M_L_values}")
    #     print(f"C_values for channel{ch} :{C_L_values}")
    
    #     avg_M[ch] = sum(M_L_values) / len(M_L_values) if M_L_values else 0
    #     avg_C[ch] = sum(C_L_values) / len(C_L_values) if C_L_values else 0

    #     print(f"Average M value for channel {ch}: {avg_M[ch]}")
    #     print(f"Average C value for channel {ch}: {avg_C[ch]}")
    #     # Store the average M and C values back into cal_data_jub
    #     cal_data_jub[str(ch) + "CLL_U_M"] = avg_M[ch]
    #     cal_data_jub[str(ch) + "CLL_U_C"] = avg_C[ch]

    #     dac_max = 0X8000
    #     pmu_ch = p.channels[ch]
    #     pmu_ch.write_dac(data = avg_M[ch], dac_reg = "CLL_U", reg = "M")
    #     pmu_ch.write_dac(dac_max, dac_reg = "CLL_U" )
    #     pmu_ch.write_dac(data = avg_C[ch], dac_reg = "CLL_U", reg = "C")
    #     pmu_ch.write_dac(dac_max, dac_reg = "CLL_U" )



    
    #CLH_U
    for r in pmu_def_jub.I_RANGES:
        for ch in range(4):
            if not reset_pmu:
                cal_data_jub[str(ch)+"CLH_U_M"] = p.channels[ch].read_dac(dac_reg = "CLH_U", reg = "M")
                cal_data_jub[str(ch)+"CLH_U_C"] = p.channels[ch].read_dac(dac_reg = "CLH_U", reg = "C")
            for _ in range(max_iterations):
                new_CL_M = cal_jub_CL_U_M(p, k, ch, r, "H", 0.5, wait_before_measure, measure_delay, measure_count)
                new_CL_C = cal_jub_CL_U_C(p, k, ch, r, "H", 0.5, wait_before_measure, measure_delay, measure_count)
                cal_data_jub[str(ch)+"CLH_U_M"+r] = new_CL_M
                cal_data_jub[str(ch)+"CLH_U_C"+r] = new_CL_C
    
    # avg_M_H = {}
    # avg_C_H = {}
    # for ch in range(4):
    #     M_H_values = [cal_data_jub[key] for key in cal_data_jub if key.startswith(str(ch) + "CLH_U_M")]
    #     C_H_values = [cal_data_jub[key] for key in cal_data_jub if key.startswith(str(ch) + "CLH_U_C")]
    #     print("\nM_H_values ",M_H_values)
    #     print("\nC_H_values",C_H_values)

    #     avg_M_H[ch] = sum(M_H_values) / len(M_H_values) if M_H_values else 0
    #     avg_C_H[ch] = sum(C_H_values) / len(C_H_values) if C_H_values else 0

    #     print(f"Average M value for channel {ch}: {avg_M_H[ch]}")
    #     print(f"Average C value for channel {ch}: {avg_C_H[ch]}")

    #     # Store the average M and C values back into cal_data_jub
    #     cal_data_jub[str(ch) + "CLH_U_M"] = avg_M_H[ch]
    #     cal_data_jub[str(ch) + "CLH_U_C"] = avg_C_H[ch]
    #     dac_max = 0X8000
    #     pmu_ch = p.channels[ch]
    #     pmu_ch.write_dac(data = avg_M_H[ch], dac_reg = "CLH_U", reg = "M")
    #     pmu_ch.write_dac(dac_max, dac_reg = "CLH_U" )
    #     pmu_ch.write_dac(data = avg_C_H[ch], dac_reg = "CLH_U", reg = "C")
    #     pmu_ch.write_dac(dac_max, dac_reg = "CLH_U" )





           

           

    #CLL_I
    for ch in range(4):
        if not reset_pmu:
            cal_data_jub[str(ch)+"CLL_I_M"] = p.channels[ch].read_dac(dac_reg = "CLL_I", reg = "M")
            cal_data_jub[str(ch)+"CLL_I_C"] = p.channels[ch].read_dac(dac_reg = "CLL_I", reg = "C")
        # elif ch == 0:
        #     cal_data_jub[str(ch)+"CLL_I_M"] = CAL_M_DEFAULT
        #     cal_data_jub[str(ch)+"CLL_I_C"] = CAL_C_DEFAULT
        # else:
        #     cal_data_jub[str(ch)+"CLL_I_M"] = new_CL_M
        #     p.channels[ch].write_dac(data = new_CL_M, dac_reg = "CLL_I", reg = "M")
        #     cal_data_jub[str(ch)+"CLL_I_C"] = new_CL_C
        #     p.channels[ch].write_dac(data = new_CL_C, dac_reg = "CLL_I", reg = "C")
        for _ in range(max_iterations):
            new_CL_M = cal_jub_CL_I_M(p, k, ch, "2m", "L", 5, wait_before_measure, measure_delay, measure_count)
            new_CL_C = cal_jub_CL_I_C(p, k, ch, "2m", "L", 5, wait_before_measure, measure_delay, measure_count)
            cal_data_jub[str(ch)+"CLL_I_M"] = new_CL_M
            cal_data_jub[str(ch)+"CLL_I_C"] = new_CL_C

    

    #CLH_I
    for ch in range(4):
        if not reset_pmu:
            cal_data_jub[str(ch)+"CLH_I_M"] = p.channels[ch].read_dac(dac_reg = "CLH_I", reg = "M")
            cal_data_jub[str(ch)+"CLH_I_C"] = p.channels[ch].read_dac(dac_reg = "CLH_I", reg = "C")
        # else:
        #     cal_data_jub[str(ch)+"CLH_I_M"] = new_CL_M
        #     p.channels[ch].write_dac(data = new_CL_M, dac_reg = "CLH_I", reg = "M")
        #     cal_data_jub[str(ch)+"CLH_I_C"] = new_CL_C
        #     p.channels[ch].write_dac(data = new_CL_C, dac_reg = "CLH_I", reg = "C")
            
        for _ in range(max_iterations):
            new_CL_M = cal_jub_CL_I_M(p, k, ch, "2m", "H", 5, wait_before_measure, measure_delay, measure_count)
            new_CL_C = cal_jub_CL_I_C(p, k, ch, "2m", "H", 5, wait_before_measure, measure_delay, measure_count)
            cal_data_jub[str(ch)+"CLH_I_M"] = new_CL_M
            cal_data_jub[str(ch)+"CLH_I_C"] = new_CL_C

    #print(cal_data_jub)
    return cal_data_jub

def measure(
        k,
        meas_delay=MEAS_SLEEP,
        meas_count=MEAS_COUNT,
        meas_func="v"):
    
    values = list()
    if meas_func == "v":
        meas_func = k.smua.measure.v
    elif meas_func == "i":
        meas_func = k.smua.measure.i
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
    
    #keithley.smua.sense = keithley.smua.SENSE_REMOTE
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
        output_voltage.append(pmu_calc_jub.dac_to_v(d, pmu_ch.read_dac("Offset")))
        sleep(measure_delay)
        measure_data.append(keithley.smua.measure.v())
        
    pmu_ch.pmu_reg = pmu_reg_channel_off
    keithley.smua.source.output = keithley.smua.OUTPUT_OFF
    
    
    return np.array(output_voltage), np.array(measure_data)  

def measureFI(pmu, keithley, ch, range, num=100, measure_delay = 0.1):
    I_RANGE_DEFS = pmu_def_jub.CURRENT_RANGES[range]
    
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
        output_current.append(pmu_calc_jub.dac_to_i(d, range))
        sleep(measure_delay)
        measure_data.append(keithley.smua.measure.i())
        
    pmu_ch.pmu_reg = pmu_reg_channel_off
    keithley.smua.source.output = keithley.smua.OUTPUT_OFF
    
    return np.array(output_current), np.array(measure_data)

def measureCL_U(pmu, keithley, ch, range, current_range_factor=0.5 , clamp_side='H', overlap=0.5, num=100, measure_delay = 0.1):
    I_RANGE_DEFS = pmu_def_jub.CURRENT_RANGES[range]
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
        pmu_ch.write_dac(pmu_calc_jub.i_to_dac(I_RANGE_DEFS["MaxVal"]*current_range_factor, range),"FIN_I_" + range)
        pmu_ch.write_dac(0,"CLL_U")
        dac_reg = "CLH_U"
    elif clamp_side == 'L':
        measure_points = np.linspace(round(0x7FFF+(0x8000*overlap)), 0, num)
        pmu_ch.write_dac(pmu_calc_jub.i_to_dac((-1)*I_RANGE_DEFS["MaxVal"]*current_range_factor, range),"FIN_I_" + range)
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
        output_voltage.append(pmu_calc_jub.dac_to_v(d, ch_offset))
        sleep(measure_delay)
        measure_data.append(keithley.smua.measure.v())
        
    pmu_ch.pmu_reg = pmu_reg_channel_off
    keithley.smua.source.output = keithley.smua.OUTPUT_OFF
    
    return np.array(output_voltage), np.array(measure_data)

def measureCL_I(pmu, keithley, ch, range, voltage=5, clamp_side='H', overlap=0.5, num=100, measure_delay = 0.1):
    I_RANGE_DEFS = pmu_def_jub.CURRENT_RANGES[range]
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
        pmu_ch.write_dac(pmu_calc_jub.v_to_dac(voltage, ch_offset),"FIN_U")
        pmu_ch.write_dac(0,"CLL_I")
        dac_reg = "CLH_I"
    elif clamp_side == 'L':
        measure_points = np.linspace(round(0x7FFF+(0x8000*overlap)), 0, num)
        pmu_ch.write_dac(pmu_calc_jub.v_to_dac(-voltage, ch_offset),"FIN_U")
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
        output_current.append(pmu_calc_jub.dac_to_i(d, range))
        sleep(measure_delay)
        measure_data.append(keithley.smua.measure.i())
        
    pmu_ch.pmu_reg = pmu_reg_channel_off
    keithley.smua.source.output = keithley.smua.OUTPUT_OFF
    
    return np.array(output_current), np.array(measure_data)

    


    
       

        
        

# def measure_jub(
#         k,
#         meas_delay=MEAS_SLEEP,
#         meas_count=MEAS_COUNT,
#         meas_func="v"):
    
#     values = list()
#     if meas_func == "v":
#         meas_func = k.smua.measure.v
#     elif meas_func == "i":
#         meas_func = k.smua.measure.i
#     else:
#         raise ValueError("unsopported measurement function")

#     for _ in range(meas_count):
#         values.append(meas_func())
#         sleep(meas_delay)
    
#     values = np.array(values)
#     if values.max() - values.min() > 0.1:
#         print("Values have high deviation (%f)" % values.std()) # warning only for voltage yet
#     return values.mean()   

        



       



# # def measure_jub(
# #         k,
# #         meas_delay = MEAS_SLEEP,
# #         meas_count = MEAS_COUNT,
# #         meas_func = "v"):


# #     values = list()
# #     if meas_func =="v":
# #         meas_func = k.smua.measure.v
# #     elif meas_func == "i":
# #         meas_func = k.smua.measure.i
# #     else:
# #         raise ValueError("unsupported measurement function")
    
# #     for _ in range (meas_count):
# #         values.append(meas_func())
# #         sleep(meas_delay)

# #     values = np.array(values)
# #     if values.max() - values.min() > 0.1 :
# #         print("Measured values have a very high deviation for a single input (%f)" % values.std()) #Warning for high deviation
# #     return values.mean()

# # def measure_avg_jub(
# #         k,
# #         meas_delay = MEAS_SLEEP,
# #         meas_count = MEAS_COUNT,
# #         meas_func = "v"):
    
    





def cal_jub_FIN_I_C_using_slope_interpolation(
        p,
        k,
        ch,
        range,
        wait_before_measure = 0.5,
        measure_delay =MEAS_SLEEP,
        measure_count = MEAS_COUNT):
    
    p.write_all_PMU_REGS(pmu_reg_channel_off)

    print("FIN_I_C CALIBRATION for channel %i @ %sA" % (ch, range))
    pmu_ch = p.channels[ch]

    k.display.screen = k.display.SMUA
    k.display.smua.measure.func = k.display.MEASURE_DCAMPS
    
    k.smua.measure.autorangei = k.smua.AUTORANGE_ON
    k.smua.measure.autorangev = k.smua.AUTORANGE_ON
    k.smua.measure.rangei = pmu_def_jub.CURRENT_RANGES[range]["MaxVal"]
    k.smua.measure.nplc = MEAS_NPLC # 0.001 to 25

    k.smua.source.func = k.smua.OUTPUT_DCVOLTS
    k.smua.source.levelv = 0
    k.smua.source.limiti = pmu_def_jub.CURRENT_RANGES[range]["MaxVal"]
    k.smua.source.limitv = 13
    k.smua.source.output = k.smua.OUTPUT_ON

    p.change_sys_ctrl({
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
        "C"    : pmu_def_jub.CURRENT_RANGES[range]["C"],     #80mA Range
        "FIN"  : 1
    })

    pmu_reg_channel_on_sys = pmu_ch.pmu_reg


    ######################################################################################################################################################################################################################   
    ##################-------For C = FIN_I_C(32768)(default)-----------############################################################################################################################################################
    ######################################################################################################################################################################################################################

    #Performing Measurement for X1 = 0X8000

    x1_val_max = 0X0000

    volt_max_for_ideal = pmu_calc_jub.dac_to_i(x1_val_max,range)

    # M Register is by default 32768 

    pmu_ch.write_dac(x1_val_max,dac_reg = "FIN_I_"+range) # Writing x1 register
    sleep(wait_before_measure)
    volt_max_for_C_0x8000 = -measure(k, measure_delay, measure_count, "i")
    
    #Performing Measurement for X1 = 0X0000

    x1_val_min = 0x8000
    volt_min_for_ideal = pmu_calc_jub.dac_to_i(x1_val_min,range)

    pmu_ch.write_dac(x1_val_min,dac_reg = "FIN_I_"+range) # Writing x1 register
    sleep(wait_before_measure)
    volt_min_for_C_0x8000 = -measure(k, measure_delay, measure_count, "i")

    #.................................................................................................................................................................................................................................
    # Arranging Variables for Interpolation

    # For Slope for C = 32768

    (x_one_for_C_32768,y_one_for_C_32768) = (x1_val_min,volt_min_for_C_0x8000)
    (x_two_for_C_32768,y_two_for_C_32768) = (x1_val_max,volt_max_for_C_0x8000)


    
    # For Slope for Ideal M Using the Equation

    (x_one_for_C_Ideal,y_one_for_C_Ideal) = (x1_val_min,volt_min_for_ideal)
    (x_two_for_C_Ideal,y_two_for_C_Ideal) = (x1_val_max,volt_max_for_ideal)

    # Refer the Code in PC to find the slopes and then do the Interpolation also

    ######################################################################################################################################################################################################################   
    ##################-------For M = FIN_I_C(65535)-----------############################################################################################################################################################
    ######################################################################################################################################################################################################################

    # Writing FIN_I_C as 65535
    pmu_ch.write_dac(data = 40000, dac_reg = "FIN_I_"+range, reg = "C") # Writing C Register

    #Performing Measurement for X1 = 0X8000
    pmu_ch.write_dac(x1_val_max, dac_reg = "FIN_I_"+range) # Writing x1 register
    pmu_ch.pmu_reg = pmu_reg_channel_off
    pmu_ch.pmu_reg = pmu_reg_channel_on_sys

    sleep(wait_before_measure)
    volt_max_for_C_0xFFFF = -measure(k, measure_delay, measure_count, "i")

    # Performing Measurement for X1 = 0x0000
    pmu_ch.write_dac(x1_val_min,dac_reg = "FIN_I_"+range) # Writing x1 register
    pmu_ch.pmu_reg = pmu_reg_channel_off
    pmu_ch.pmu_reg = pmu_reg_channel_on_sys

    sleep(wait_before_measure)
    volt_min_for_C_0xFFFF = -measure(k, measure_delay, measure_count, "i")

    #......................................................................................................................................................................................................................
    
    # Arranging Variables for Interpolation

    # For Slope for C = 65535

    (x_one_for_C_65535,y_one_for_C_65535) = (x1_val_min,volt_min_for_C_0xFFFF)
    (x_two_for_C_65535,y_two_for_C_65535) = (x1_val_max,volt_max_for_C_0xFFFF)

    

    # 3 Slopes required for interpolation

    slope_Max = (y_two_for_C_65535 - y_one_for_C_65535) / (x_two_for_C_65535-x_one_for_C_65535)
    print("\nslope_Max",slope_Max)

    slope_Min = (y_two_for_C_32768-y_one_for_C_32768)/(x_two_for_C_32768-x_one_for_C_32768)
    print("\nslope_Min",slope_Min)

    slope_Ideal = (y_two_for_C_Ideal-y_one_for_C_Ideal)/(x_two_for_C_Ideal-x_one_for_C_Ideal)
    print("\nslope_Ideal",slope_Ideal)

    #..................................................................................................................................................................................................................................
    # Performing Interpolation

    dac_min = 0X8000
    dac_max = 0XFFFF

    x = np.array([ slope_Min, slope_Max])           #  Comparing For Interpolation
    y = np.array([dac_min,dac_max])
 
    
    model = np.polyfit(x, y, 1)                     # Fit a linear line to the known data points
 
   
    new_x = np.array([ slope_Ideal])                # New x values for which to extrapolate the y values
 
    
    new_y = np.polyval(model, new_x)                # Extrapolate the y values for the new x values
 
    print(new_y)
    print("\nOffset after Interpolation",new_y)
    NEW_FIN_I_C_FINAL= new_y

    pmu_ch.write_dac(data = NEW_FIN_I_C_FINAL, dac_reg = "FIN_I_"+range, reg = "C") # Writing the new C found using interpolation
    pmu_ch.write_dac(x1_val_max, dac_reg = "FIN_I_"+range) # Writing 0XFFFF to X1
    pmu_ch.pmu_reg = pmu_reg_channel_off
    pmu_ch.pmu_reg = pmu_reg_channel_on_sys

    sleep(wait_before_measure)

    meas_max_cal_FINAL = -measure(k, measure_delay, measure_count, "i")
    print("\tV_MAX after Cal = %sV" % si_format(meas_max_cal_FINAL, precision=3))


    pmu_ch.pmu_reg = pmu_reg_channel_off
    k.smua.source.output = k.smua.OUTPUT_OFF

    return NEW_FIN_I_C_FINAL

def cal_perc_FIN_U_M(     
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
    v_high = pmu_calc_jub.dac_to_v(dac_max, OFFSET)
    
    # set pos cal value
    pmu_ch.write_dac(dac_max, dac_reg = "FIN_U")
    sleep(wait_before_measure)
    meas_max = measure(keithley, measure_delay, measure_count)
    difference = abs(v_high - meas_max)

    percentage_difference = ((meas_max-v_high)/meas_max) *100
    print("\npercentage_difference",percentage_difference)
    
    Offset_decrease = FIN_U_M*(percentage_difference/100)

    NEW_FIN_U_M = (FIN_U_M-Offset_decrease)
   
    
    pmu_ch.write_dac(data = NEW_FIN_U_M, dac_reg = "FIN_U", reg = "M")
    pmu_ch.write_dac(dac_max, dac_reg = "FIN_U")
    sleep(wait_before_measure)
    meas_max_cal = measure(keithley, measure_delay, measure_count)
    print("\tV_MAX after Cal = %sV" % si_format(meas_max_cal, precision=3))
    
    pmu_ch.pmu_reg = pmu_reg_channel_off
    keithley.smua.source.output = keithley.smua.OUTPUT_OFF
    
    return NEW_FIN_U_M








    
    

     