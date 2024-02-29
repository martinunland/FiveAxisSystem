from tqdm import tqdm
import numpy as np
import functools
from FAS import Position


def linear(x, slope, const):
    return x * slope + const


def linear_const(x, slope, const, limit):
    if x > limit:
        return linear(x, slope, const)
    else:
        return linear(limit, slope, const)


class PathTime:
    axis_calibration = {
        "x": {
            "a_slope": 0.20790012334298638,
            "a_const": 1.9295769879330378,
            "s_slope": 0.2166979108929974,
            "s_const": -0.00020895898299489192,
            "t0": 0.8035466610250618,
            "limit": 26.512215558982945,
        },
        "y": {
            "a_slope": 0.20790012334298638,
            "a_const": 1.9295769879330378,
            "s_slope": 0.2166979108929974,
            "s_const": -0.00020895898299489192,
            "t0": 0.8035466610250618,
            "limit": 26.512215558982945,
        },
        "z": {
            "a_slope": 0.21404669070648036,
            "a_const": 1.8086909751945424,
            "s_slope": 0.21691036585457518,
            "s_const": -0.0011633157825590718,
            "t0": 0.8150417874577068,
            "limit": 26.394586571979318,
        },
        "tilt": {
            "a_slope": 22.103368696634956,
            "a_const": -221.28313103153457,
            "s_slope": 0.06032301996107505,
            "s_const": -0.0014802523160998356,
            "t0": 0.8218185898560731,
            "limit": 16.871716286810294,
        },
        "rot": {
            "a_slope": 6.878106827773913,
            "a_const": -70.07796079140954,
            "s_slope": 0.020048707857610395,
            "s_const": -0.001139030453163392,
            "t0": 0.8219959728476175,
            "limit": 16.431994985962138,
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
        t0,
        limit,
    ):
        acceleration = linear_const(acceleration_adc, a_slope, a_const, limit)
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
                    distance, **self.axis_calibration[axis_initial]
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
