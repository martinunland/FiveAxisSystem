
from .serialcontroller import SerialController
from .utils_constants import axis_to_system_units, system_default_units, axis_units, Axis, system_to_axis_units
from .utils_constants import parse_number_string
from dataclasses import dataclass, asdict
import logging

log = logging.getLogger(__name__)

@dataclass    
class Position:

    x: float = None
    y: float = None
    z: float = None
    rot: float = None
    tilt: float = None

    def update_to_system_units(self):
        # Iterate through each axis and update its value according to the unit conversion
        for axis, value in self.__dict__.items():
            if value is not None:
                setattr(self, axis, axis_to_system_units(value, axis))
        return self
    
    def __iter__(self):
        for axis, value in self.__dict__.items():
            yield (axis, value)

    def to_dict(self):
        return asdict(self)
class FiveAxisSystem:
    
    def __init__(self, controller : SerialController):
        self.controller = controller
        self.speed = 100
        self.acceleration = 100

    def _move_single_axis(self, axis: str, pos: int)->str:
        log.debug("Moving axis %s to position %d", axis, int(pos))
        axis_command = getattr(Axis, axis)
        return self.controller.send(f"{axis_command}-Achse:{int(pos)}", str(self.speed), str(self.acceleration))
    
    def get_current_position(self)->None:
        answer = self.controller.send(f"My-Achse:")
        print(self._parse_answer(answer))
        
    def move_absolute_position(self, x=None, y=None, z=None, rot=None, tilt=None) -> None:
        # Create a dictionary from the local variables (axis names and values),
        # filtering out None values to only attempt to move axes that are specified.
        moves = {axis: value for axis, value in locals().items() if axis != "self" and value is not None}
        log.debug("Moving to absolute position %s", moves)
        for axis, pos in moves.items():
            converted_pos = system_to_axis_units(pos, axis)
            answer = self._move_single_axis(axis, converted_pos)
        self.current_position = self._parse_answer(answer)

    def move_relative_distance(self, x=None, y=None, z=None, rot=None, tilt=None) -> None:
        if self.current_position is None:
                log.error("Current position is unknown; cannot move relatively.")
                return
        # Create a dictionary from the local variables (axis names and values),
        # filtering out None values to only attempt to move axes that are specified.
        relative_moves = {axis: value for axis, value in locals().items() if axis != "self" and value is not None}
        log.debug("Calculating position from relative input %s", relative_moves)
        absolute_moves = {}
        for axis, delta in relative_moves.items():
            current_value = getattr(self.current_position, axis)
            absolute_moves[axis] = current_value + delta
        self.move_absolute_position(**absolute_moves)

    def _parse_answer(self, answer) -> Position:
        log.debug("Parsing answer %s into Position instance", answer)
        answer_without_ending = answer.split(self.controller.answer_end)
        if len(answer_without_ending) > 1:
            split_axis = answer_without_ending[0].split("Achse:")
            axis_values = [parse_number_string(split_axis[i].split(" ")[0]) for i in range(1, 6)]
            return Position(*axis_values).update_to_system_units()
        else:
            return Position()
        
    def log_current_position(self) -> None:
        log.info("The current position is: %s", self.current_position)
        return self.current_position