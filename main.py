from src.scheduling import FASSchedule
from src.FAS import FiveAxisSystem
#from src.serialcontroller import SerialController
from src.utils_constants import Units
import logging
import numpy as np

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

'''
controller = SerialController("COM5")
FAS = FiveAxisSystem(controller)

FAS.move_absolute_position(x=100, rot=2)  # moves x axis 100cm, rotation axis 2 deg

FAS.move_relative_distance(y=5)  # moves y axis 5cm from current position

# Default units centimeter and degree (check utils_constants-> system_default_units), but you can use other units,
# e.g. if you want to move x 2 mm, y 1 meter and tilt 2/100 deg:

FAS.move_relative_distance(x=2 / Units.MM, y=1 / Units.M, tilt=2 / Units.CENT_DEG)

FAS.log_current_position()

'''

# Scheduling example
schedule = FASSchedule()
for i in range(1000):
    schedule.append_programmed_position(
        np.random.randint(0, 100), np.random.randint(0, 100), np.random.randint(0, 100)
    )
print(schedule.calculate_total_path_time())  # In this example I got 864 min

# Optimize path so next move is always shortest distance
schedule.optimize_path()

print(schedule.calculate_total_path_time())  # In this example I got 176 min

'''
# You can save optimized schedule
schedule.write_schedule_to_file("optimized_position_schedule.pickle")

# And load it in future measurements directly
schedule.load_schedule_from_file("optimized_position_schedule.pickle")

# Going through schedule
for position in schedule:
    FAS.move_absolute_position(**position.to_dict())
'''