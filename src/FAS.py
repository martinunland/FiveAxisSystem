
from serialcontroller import SerialController
from utils_constants import axis_to_system_units, system_default_units, axis_units, Axis, system_to_axis_units
from utils_constants import parse_number_string
from dataclasses import dataclass
import logging

log = logging.getLogger(__name__)

@dataclass    
class Position:

    X: float = None
    Y: float = None
    Z: float = None
    ROT: float = None
    TILT: float = None

    def update_to_system_units(self):
        # Iterate through each axis and update its value according to the unit conversion
        for axis, value in self.__dict__.items():
            if value is not None:
                setattr(self, axis, axis_to_system_units(value, axis))
        return self
    
class FiveAxisSystem:
    
    def __init__(self, controller : SerialController):
        self.controller = controller

    def _move_single_axis(self, axis: str, pos: int)->str:
        log.debug(f"Moving axis {axis} to position {pos}")
        axis_command = getattr(Axis, axis.upper())
        return self.controller.send(f"{axis_command}-Achse:{pos}", "100", "100")
        
    def move_absolute_position(self, x=None, y=None, z=None, rot=None, tilt=None) -> None:
        # Create a dictionary from the local variables (axis names and values),
        # filtering out None values to only attempt to move axes that are specified.
        moves = {axis: value for axis, value in locals().items() if axis != "self" and value is not None}
        
        for axis, pos in moves.items():
            converted_pos = system_to_axis_units(pos, axis.upper())
            answer = self._move_single_axis(axis, converted_pos)
        self.current_position = self._parse_answer(answer)

    def move_relative_distance(self, x=None, y=None, z=None, rot=None, tilt=None) -> None:
        if self.current_position is None:
                log.error("Current position is unknown; cannot move relatively.")
                return
        # Create a dictionary from the local variables (axis names and values),
        # filtering out None values to only attempt to move axes that are specified.
        relative_moves = {axis: value for axis, value in locals().items() if axis != "self" and value is not None}
        absolute_moves = {}
        for axis, delta in relative_moves.items():
            current_value = getattr(self.current_position, axis.upper())
            absolute_moves[axis] = current_value + delta
        self.move_absolute_position(**absolute_moves)

    def _parse_answer(self, answer) -> Position:
        answer_without_ending = answer.split(self.controller.answer_end)
        if len(answer_without_ending) > 1:
            split_axis = answer_without_ending[0].split("Achse:")
            axis_values = [parse_number_string(split_axis[i].split(" ")[0]) for i in range(1, 6)]
            return Position(*axis_values).update_to_system_units()
        else:
            return Position()
        
    def log_current_position(self) -> None:
        log.info("The current position is:")
        log.info(Position)