from keithley2600 import Keithley2600

from time import sleep
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from percentage_calculator import calculate_percentage
from tqdm import tqdm
import matplotlib.pyplot as plt
from pmu_som import pmu_ctrl, pmu_cal, pmu_calc, pmu_def


def j_measurement_FV(p,k,offset_val=0x8000):

   

    k.smua.reset()
    k.smub.reset()
    measure_delay = 0.1
    sleep(measure_delay)

    # p = communicator.communicator(False)

    ### all channels of PMU turnoff

    for channel in p.channels:
        channel.change_pmu_reg({"CH EN": 0})
   

    ## SMU and PMU Setup

    p.write_all_PMU_REGS(0x1E060)
    sleep(0.5)

    k.display.screen = k.display.SMUA
    k.display.smua.measure.func = k.display.MEASURE_DCVOLTS

    k.smua.measure.rangev = 20
    k.smua.measure.autorangei = k.smua.AUTORANGE_ON
    # k.smua.measure.autorangev   = k.smua.AUTORANGE_ON
    k.smua.measure.nplc = 1
    k.smua.source.func = k.smua.OUTPUT_DCAMPS
    k.smua.source.leveli = 0
    k.smua.source.limiti = 1e-3
    k.smua.source.limitv = 20
    k.smua.source.output = k.smua.OUTPUT_ON

    p.change_sys_ctrl({
        "DUTGND/CH": 1,
        "INT10K": 1,
        "GAIN": 2,
        "TMP ENABLE": 1,
        "TMP": 3  # Thermal shutdown at 100°C
    })

    #p.decode_pmu_reg()

    for ch in range(4):
        p.channels[ch].change_pmu_reg({
            "SS0": 0,
            "SF0": 0  # 1,1
        })

        d = 0x4000
        
        p.channels[ch].write_dac(
            data = offset_val,
            dac_reg="FIN_U",
            reg="C"
        )
       
        sleep(0.5)

    import matplotlib.pyplot as plt

    # Initialize an empty list to store individual DataFrames
    all_dataframes = []

    # Add for loop for ch
    for ch in range(1):
        print(ch)

        #  p.write_all_PMU_REGS(0x21fc60)

        # p.channels[ch].change_pmu_reg = 0x21fc60

        # Change PMU register settings for the current channel
        p_ch = p.channels[ch]
        p_ch.pmu_reg = 0x21fc60

        # Enable beeper and play chord
        k.beeper.enable = k.beeper.ON
        k.beeper.beep(0.5,500)
        k.beeper.enable = k.beeper.OFF
        k.smua.source.output = k.smua.OUTPUT_ON

        data_list = []
        measure_points = np.linspace(0x0000, 0x8000, 10)

        # Calculate the step size to generate 20 equidistant data points
        # step_size = 0xFFFF // 19
       
        

        # Loop to generate and write equidistant data points
        for d in measure_points:
            # Calculate the data value for the current index
            # data = i * step_size

            # Print the data being written to the DAC register
            #print(f"Writing data {d }: {(d)}")
            x = d
            data_perc = calculate_percentage(x)
            print(data_perc)
            sleep(measure_delay)

            # Write the data to the DAC register
            p.channels[ch].write_dac(
                data=round(d),
                dac_reg="FIN_U",
                reg="X1"
            )

            # Perform measurement after writing to the DAC register
            sleep(0.5)

            iv_data = k.smua.measure.v()
            V_REF = 5

            # Print the measurement outputs
            #print(f"Measurement outputs : {iv_data}")

            # Calculate expected output and error
            VOUT = ((4.5 * d) - (3.5 * 42130)) * (V_REF / (2 ** 16))
            error = VOUT - iv_data
            #print(f"Expected Output : {VOUT}")

            # Append data to the list
            data_list.append({"CODE": (d), "VOUT - EXPECTED": VOUT, "VOUT-RESULT": iv_data, "Error": error})

        # Create a DataFrame for the current channel
        data_df = pd.DataFrame(data_list)

        # Append the DataFrame to the list of all DataFrames
        all_dataframes.append(data_df)

        # Display the DataFrame
        #print("\nData stored in DataFrame:")
        #print(data_df)

        # Plot the data for the current channel
        #plt.plot(data_df.index, data_df["Error"], label=f"Channel {ch} Data", linestyle='-')

        # Add legend and labels
        #plt.xlabel("CODE")
        #plt.ylabel("Error")
        #plt.title(f"Error vs CODE Plot for Channel {ch}")
        #plt.legend()

        # Show the plot
        #plt.show()
        k.smua.source.output = k.smua.OUTPUT_OFF
        p.channels[ch].change_pmu_reg({
            "CH EN": 0
        })

        # Change PMU register settings for the current channel
        p.channels[ch].change_pmu_reg({
            "SS0": 0,
            "SF0": 0,
        })

        sleep(measure_delay)
        #p.c.s.close()

    # Concatenate all individual DataFrames into a single DataFrame
    all_data_df = pd.concat(all_dataframes)
    print( all_data_df)
    
    
   
   
    #print(offset_val)

    # Display the new DataFrame
    #print("\nNew DataFrame containing values of all four previous DataFrames:")
    #print(all_data_df)

    # Plot comparing all the other four plots
    #for df in all_dataframes:
        #plt.plot(df.index, df["Error"], linestyle='-')

    # Add legend and labels
   # plt.xlabel("CODE")
    #plt.ylabel("Error")
    #plt.title("Comparison of Error vs CODE Plots for All Channels")
    #plt.legend([f"Channel {i}" for i in range(4)])

    # Extracting the error values to a separate dataframe called error1
    error_res = all_data_df[["Error"]]
    k.beeper.enable = k.beeper.ON
    k.beeper.beep(0.5,1000)
    k.beeper.enable = k.beeper.OFF
    return error_res, offset_val

if __name__ == "__main__":
    error_res, offset_val = j_measurement_FV(p,k)
   # print(error_res)
