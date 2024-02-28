# Five Axis System Control Library

## Installation

To use this library, clone the repository to your local machine:

```bash
git clone [repository-link]
```

Ensure that Python 3.6+ is installed on your system. Then, navigate to the cloned repository's directory and install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Initializing the System

```python
from src.FAS import FiveAxisSystem
from src.serialcontroller import SerialController

controller = SerialController("COM5")  # Replace COM5 with your device's port
FAS = FiveAxisSystem(controller)
```

### Moving the Axes

To move an axis to an absolute position:

```python
FAS.move_absolute_position(x=100, rot=2)  # Moves X axis to 100cm, rotation axis to 2 degrees
```

To move an axis a relative distance from its current position:

```python
FAS.move_relative_distance(y=5)  # Moves Y axis 5cm from current position
```

### Using Different Units

The default units are centimeters and degrees. You can use other units like this:

```python
from src.utils_constants import Units
FAS.move_relative_distance(x=2/Units.MM, y=1/Units.M, tilt=2/Units.CENT_DEG)
```

### Scheduling Movements

You can create a schedule of movements:

```python
from scheduling import FASSchedule
schedule = FASSchedule()
# Append positions to the schedule
schedule.append_programmed_position(x=50, y=50, rot=30)
schedule.append_programmed_position(x=50, y=51, rot=30)
...
# Execute scheduled movements
for position in schedule:
    FAS.move_absolute_position(**position.to_dict())
```
For large measurement, you can optimize the total path. In this example all movements would have taken ~14 hrs, after optimization 3hrs
```python
for i in range(1000):
    schedule.append_programmed_position(np.random.randint(0,100), np.random.randint(0,100), np.random.randint(0,100))
# Optimize the movement path
schedule.optimize_path()
print(schedule.calculate_total_path_time())
```
You can save and load (optimized) schedules:
```python
schedule.write_schedule_to_file("optimized_position_schedule.pickle")
schedule.load_schedule_from_file("optimized_position_schedule.pickle")
```

### Logging

The current position can be logged with:

```python
FAS.log_current_position()
```
