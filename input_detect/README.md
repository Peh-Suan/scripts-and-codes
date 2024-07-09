# input_detect
input_detect allows you to detect the input and whether it surpasses a certain threshold while executing other codes.

## Installation
For Windows:
```
pip install input_detect
```
For MacOS:
```
brew install portaudio
pip install input_detect
```

## Usage
This package is meant to be used in experiemnts, where the trials need to interact with given input. For example, with input_detect, a trial can be automatically stopped, or stimuli can be automatically changed, when the detected volume of the sbjects goes above a certain level.


```python
from input_detect import ThresholdDetect
```


```python
ipdt = ThresholdDetect()
```

### Initiate the input recording environment and start recording


```python
ipdt.init(channels=1)
ipdt.start_recording()
```

### Record the input and calculate the 30% threshold


```python
ipdt.calculate_threshold(30, data_len=400000, trial_num=2)
```




    116.634130859375



### Detect whether the input surpasses the calculated threshold


```python
while ipdt.detect_signal(447):
    pass
print('Signal detected.')
```

    Signal detected.


### Terminate recording


```python
ipdt.terminate_recording()
```
