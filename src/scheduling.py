from tqdm import tqdm
import numpy as np
import functools
from .FAS import Position


def linear(x, slope, const):
    return x * slope + const


def linear_step(x, slope, const):
    x = int(x/10)*10
    return linear(x,slope,const)

class PathTime:
    axis_calibration = {
        "x": {
            "a_slope": 0.2904409779122619,
            "a_const": 1.2077330604928136,
            "s_slope": 0.21638106368842852,
            "s_const": 0.0018993869426034257,
            "t0": 0.8908983496211884,
        },
        "y": {
            "a_slope": 0.23827953982528538,
            "a_const": 2.0345359162324947,
            "s_slope": 0.21659195037066725,
            "s_const": 0.0007889468963793958,
            "t0": 0.8251032150944726,
        },
        "z": {
            "a_slope": 0.23342700810816303,
            "a_const": 2.127238368785634,
            "s_slope": 0.21652565324121187,
            "s_const": 0.000773052604182803,
            "t0": 0.8161839563958946,
        },
        "tilt": {
            "a_slope": 17.752623230479188,
            "a_const": -28.161817079227312,
            "s_slope": 0.06027239386618709,
            "s_const": -0.001236066727795777,
            "t0": 0.8217697818261861,
        },
        "rot": {
            "a_slope": 6.081587120398348,
            "a_const": -17.82680508910915,
            "s_slope": 0.020025354843183265,
            "s_const": -0.00014466021729686357,
            "t0": 0.8218914594786518,
        },
    }

    @functools.lru_cache(maxsize=1000000)
    def ramp_motion_time(self, distance, max_speed, acceleration):
        # Distance covered during rampind up down
        d_ramp = max_speed * max_speed / acceleration
        distance_left = distance - d_ramp

        # Check if max speed is reached
        if distance_left < 0:
            # Triangular motion (max speed not reached)
            time = np.sqrt(4 * distance / (acceleration))
        else:
            # Trapezoidal motion (max speed reached)
            # Distance covered during rampind up down
            t_const = distance_left / max_speed
            t_ramp = 2 * max_speed / acceleration
            time = t_ramp + t_const
        return time

    @functools.lru_cache(maxsize=1000000)
    def model(
        self,
        distance,
        speed_adc,
        acceleration_adc,
        a_slope,
        a_const,
        s_slope,
        s_const,
        t0
    ):
        acceleration = linear_step(acceleration_adc, a_slope, a_const)
        max_speed = linear(speed_adc, s_slope, s_const)
        return self.ramp_motion_time(distance, max_speed, acceleration) + t0

    def time_to_position(self, initial_position: Position, target_position: Position):
        total_time = 0
        for (axis_initial, val_initial), (axis_target, val_target) in zip(
            initial_position, target_position
        ):
            assert axis_initial == axis_target, "Mismatched axes in positions"
            if val_initial != None and val_target != None:
                distance = abs(val_target - val_initial)
                total_time += self.model(
                    distance, 200, 200, **self.axis_calibration[axis_initial]
                )
        return total_time


class FASSchedule:
    schedule = []

    def append_programmed_position(
        self, x=None, y=None, z=None, rot=None, tilt=None
    ) -> None:
        moves = {
            axis: value
            for axis, value in locals().items()
            if axis != "self" and value is not None
        }
        self.schedule.append(Position(**moves))

    def calculate_total_path_time(self):
        initial_position = Position(10, 10, 10, 0, 0)
        Ptime = PathTime()
        total_time = 0
        for position in self.schedule:
            total_time += Ptime.time_to_position(initial_position, position)
            initial_position = position
        return total_time

    def write_schedule_to_file(self, fname: str):
        import pickle

        with open(fname, "wb") as f:
            pickle.dump(self.schedule, f)

    def load_schedule_from_file(self, fname: str):
        import pickle

        with open(fname, "rb") as f:
            self.schedule = pickle.load(f)

    def optimize_path(self):
        if not self.schedule:
            return  # Early return if there are no positions

        path_time = (
            PathTime()
        )  # Instantiate the class that calculates time between positions
        remaining = set(range(len(self.schedule)))
        current_pos = remaining.pop()  # Start from the first position
        optimized_path = [self.schedule[current_pos]]

        # Progress bar for visual feedback
        with tqdm(total=len(self.schedule) - 1, desc="Optimizing path") as pbar:
            while remaining:
                next_pos, min_time = min(
                    (
                        (
                            pos,
                            path_time.time_to_position(
                                self.schedule[current_pos], self.schedule[pos]
                            ),
                        )
                        for pos in remaining
                    ),
                    key=lambda item: item[1],
                )
                optimized_path.append(self.schedule[next_pos])
                current_pos = next_pos
                remaining.remove(next_pos)
                pbar.update(1)

        self.schedule = optimized_path

    def __len__(self):
        return len(self.schedule)

    def __getitem__(self, idx):
        return self.schedule[idx]
