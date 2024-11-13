# Calibration for PMU-SOM

**Calculation for FV :**

$$ VOUT = \left( 4.5 * VREF * {DAC\_CODE \over 2^{16}} \right) - \left( 3.5 * VREF * {OFFSET\_DAC\_CODE \over 2^{16}} \right) + DUTGND $$

**Calculation for FI :**

$$ FI = 4.5 * VREF * \left( {DAC\_CODE - 2^{15} \over 2^{16} } \over R_{SENSE} * MI\_AMPLIFIER\_GAIN \right) $$

**Values:** 

| Name                  | Value            |
|:----------------------|------------------|
| VREF                  | $$ 5 V $$        |
| DUTGND                | $$ 0 V $$        |
| $$R_{SENS \pm 5uA}$$  | $$ 200k \Omega$$ |
| $$R_{SENS \pm 20uA}$$ | $$ 50k \Omega$$  |
| $$R_{SENS \pm 200uA}$$| $$ 5k \Omega$$   |
| $$R_{SENS \pm 2mA}$$  | $$ 500 \Omega$$  |
| $$R_{SENS \pm 80mA}$$ | $$ 15 \Omega$$   |



## Zero Scale Gain Calibration
Set to Zero
Measure Output Voltage

## Calculate DAC-OFFSET Code

$$ V_{DAC\_OFFSET} = - \left( 3.5 * VREF * {OFFSET\_DAC\_CODE \over 2^{16}} \right)$$

$$ V_{DAC\_OFFSET\_MAX} = 3.5 * 5V * 0 = 0V $$
$$ V_{DAC\_OFFSET\_MIN} = 3.5 * 5V * 1 = -17,5V $$


Lets aim for -6,25V DAC-Offset Voltage

$$ OFFSET\_DAC\_CODE = -{{V_{DAC\_OFFSET} * 2^{16}} \over 3.5 * VREF} = -{{(-6,25V) * 2^{16}} \over 3.5 * 5V} = 23406 $$

Real Offset voltage error is +76 uV.

DAC - Zero Voltage value will be:
$$ \left( 4.5 * VREF * {DAC\_CODE \over 2^{16}} \right) - 6.25V = 0 $$
$$ DAC\_ZERO\_CODE = {{6,25V * 2^{16}} \over 4.5 * 5V} = 18204$$

This allows for DAC-Range from -6,25 V to 16,25 V