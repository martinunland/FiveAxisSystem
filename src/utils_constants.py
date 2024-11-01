from numpy import pi


class Units:
    CM = 1
    UM = CM*10000.
    MM = CM*10.
    M = CM/100.
    DEG = 1
    RAD = 180*DEG/pi
    CENT_DEG = DEG*100
    

class Axis:
    X : str =  "X"
    Y : str =  "Y"
    Z : str =  "Z"
    ROT : str =  "4"
    TILT  : str =  "5"


axis_units = {
    "X": Units.UM,
    "Y": Units.UM,
    "Z": Units.UM,
    "ROT": Units.CENT_DEG,
    "TILT": Units.CENT_DEG,
}

system_default_units = {
    "X": Units.CM,
    "Y": Units.CM,
    "Z": Units.CM,
    "ROT": Units.DEG,
    "TILT": Units.DEG,
}

def parse_number_string(number_string):
    if '-' in number_string:
        return -float(number_string.split('-')[1])
    return float(number_string)
    
def system_to_axis_units(val, axis):
    axis_unit = axis_units[axis]
    system_units = system_default_units[axis]
    return val * axis_unit / system_units

def axis_to_system_units(val, axis):
    axis_unit = axis_units[axis]
    system_units = system_default_units[axis]
    return val * system_units / axis_unit