from src.FAS import FiveAxisSystem
from src.serialcontroller import SerialController
from utils_constants import Units

controller = SerialController("COM5")
FAS = FiveAxisSystem(controller)
FAS.move_absolute_position(x=100)
FAS.move_absolute_position(x=200, tilt = 20)
FAS.move_relative_distance(y=5)

#Default units centimeter and degree (check utils_constants-> system_default_units), but you can use other units,
# e.g. if you want to move 1 meter:

FAS.move_relative_distance(y=1/Units.M)