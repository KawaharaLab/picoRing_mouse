## VNA

```
[VNA] # frequency sweep parameter of VNA. Note that the parameter matches with the parameter in the calibration file
start_freq = 27
freq_step = 0.06
step_num = 51
input_power = -3
bandwidth = 10000
calibration_file = calibration_file/27_30_51_10kHz_ncal.cal 

```


## Sensor

### template
```
[sensor_name]
state_name1 = peak_freq1 (MHz)
state_name2 = peak_freq2 (MHz)

state_nameN = peak_freqN (MHz)
none = 0
range = freq (MHz)
```