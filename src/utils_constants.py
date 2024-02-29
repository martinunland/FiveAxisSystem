from numpy import pi


class Units:
    CM = 1
    UM = CM * 10000.0
    MM = CM * 10.0
    M = CM / 100.0
    DEG = 1
    RAD = 180 * DEG / pi
    CENT_DEG = DEG * 100


class Axis:
    x: str = "X"
    y: str = "Y"
    z: str = "Z"
    rot: str = "4"
    tilt: str = "5"


axis_units = {
    "x": Units.UM,
    "y": Units.UM,
    "z": Units.UM,
    "rot": Units.CENT_DEG,
    "tilt": Units.CENT_DEG,
}

system_default_units = {
    "x": Units.CM,
    "y": Units.CM,
    "z": Units.CM,
    "rot": Units.DEG,
    "tilt": Units.DEG,
}


def parse_number_string(number_string):
    if "-" in number_string:
        return -float(number_string.split("-")[1])
    return float(number_string)


def system_to_axis_units(val, axis):
    axis_unit = axis_units[axis]
    system_units = system_default_units[axis]
    return val * axis_unit / system_units


def axis_to_system_units(val, axis):
    axis_unit = axis_units[axis]
    system_units = system_default_units[axis]
    return val * system_units / axis_unit
