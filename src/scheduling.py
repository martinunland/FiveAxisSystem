from tqdm import tqdm
import numpy as np

from FAS import Position

def linear(x,slope, const):
    return x * slope + const

class PathTime:
    axis_calibration = {
        "x" : {"a_slope": 15.4858e-3, "a_const": 667.16e-3, "s_slope": 21.69987e-3, "s_const": -161.1e-6, "t0": 805.71e-3},
        "y" : {"a_slope": 15.4858e-3, "a_const": 667.16e-3, "s_slope": 21.69987e-3, "s_const": -161.1e-6, "t0": 805.71e-3},
        "z" : {"a_slope": 16.7938e-3, "a_const": 641.75e-3, "s_slope": 21.74835e-3, "s_const": -404.0e-6, "t0": 812.973e-3},
        "tilt" : {"a_slope": 10.919, "a_const": 131.51, "s_slope": 60.3046e-3, "s_const": -1.389e-3, "t0": 	821.750e-3},
        "rot" : {"a_slope": 3.271, "a_const": 33.37, "s_slope": 20.0614e-3, "s_const": -2.06e-3, "t0": 821.928e-3}
    }
    def ramp_motion_time(self, distance, max_speed, acceleration):
        # Distance covered during rampind up down
        d_ramp = max_speed * max_speed / acceleration
        distance_left = distance - d_ramp

        # Check if max speed is reached
        if distance_left<0:
            # Triangular motion (max speed not reached)
            time = np.sqrt( 4 * distance / (acceleration))
        else:
            # Trapezoidal motion (max speed reached)
            # Distance covered during rampind up down
            t_const = distance_left / max_speed
            t_ramp = 2 * max_speed / acceleration
            time = t_ramp+t_const
        return time
    
    def model(self, distance, speed_adc, acceleration_adc,  a_slope, a_const, s_slope, s_const, t0):
        acceleration = linear(acceleration_adc, a_slope, a_const)
        max_speed = linear(speed_adc, s_slope, s_const)
        return self.ramp_motion_time(distance, max_speed, acceleration)+t0
    

    def time_to_position(self, initial_position: Position, target_position: Position):
        total_time = 0
        for (axis_initial, val_initial), (axis_target, val_target) in zip(initial_position, target_position):
            assert axis_initial == axis_target, "Mismatched axes in positions"
            if val_initial != None and val_target != None:
                distance = abs(val_target-val_initial)
                total_time += self.model(distance, **self.axis_calibration[axis_initial])
        return total_time
    
class FASSchedule:
    schedule = []

    def append_programmed_position(self, x=None, y=None, z=None, rot=None, tilt=None) -> None:
        moves = {axis: value for axis, value in locals().items() if axis != "self" and value is not None}
        self.schedule.append(Position(**moves))
        
    def calculate_total_path_time(self):
        initial_position = Position(10,10,10,0,0)
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
            self.schedule=pickle.load(f)

    def optimize_path(self):
        if not self.schedule:
            return  # Early return if there are no positions

        path_time = PathTime()  # Instantiate the class that calculates time between positions
        remaining = set(range(len(self.schedule)))
        current_pos = remaining.pop()  # Start from the first position
        optimized_path = [self.schedule[current_pos]]

        # Progress bar for visual feedback
        with tqdm(total=len(self.schedule) - 1, desc='Optimizing path') as pbar:
            while remaining:
                next_pos, min_time = min(
                    ((pos, path_time.time_to_position(self.schedule[current_pos], self.schedule[pos])) for pos in remaining),
                    key=lambda item: item[1]
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