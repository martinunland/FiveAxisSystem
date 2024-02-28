# Five Axis System Control Library

This Python library is designed to facilitate the control and scheduling of a Five Axis System (FAS) through serial communication. The system allows for precise movements along five different axes: X, Y, Z, Rotation, and Tilt, making it suitable for a wide range of applications from robotics to manufacturing.

## Features

- Absolute and relative positioning commands
- Conversion between different units of measurement
- Scheduling of movement sequences
- Path optimization to reduce total movement time
- Logging of current position and movements
- Serial communication with hardware

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

You can create a schedule of movements and optimize the path to reduce total movement time:

```python
from scheduling import FASSchedule
schedule = FASSchedule()
# Append positions to the schedule
for i in range(1000):
    schedule.append_programmed_position(np.random.randint(0,100), np.random.randint(0,100), np.random.randint(0,100))

# Optimize the movement path
schedule.optimize_path()
# Execute scheduled movements
for position in schedule:
    FAS.move_absolute_position(**position.to_dict())
```

### Logging

The current position can be logged with:

```python
FAS.log_current_position()
```

## Contributing

Contributions to the library are welcome! Please submit pull requests with any new features or bug fixes.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
