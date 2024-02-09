
    



class SerialController:
    
    def __init__(self, port='COM5', timeout=10):
        self.ise = serial.Serial(port=port, timeout=timeout)
        self.ise.close()  # Close initially, open only when needed
        self.answer_end = "####"
        
    def open(self):
        if not self.ise.is_open:
            self.ise.open()

    def close(self):
        if self.ise.is_open:
            self.ise.close()
            
    def send(self, *args):
        self.open()
        print(args)
        try:
            for i, arg in enumerate(args):
                self.ise.write((str(arg)+"\r\n").encode())
                if i!=len(args)-1:
                    time.sleep(0.5)
            response = self.ise.read_until((self.answer_end).encode(), 100).decode()
        except Exception as err:
            print(err)
        self.close()
        return response

def parse_number_string(number_string):
    if '-' in number_string:
        return -float(number_string.split('-')[1])
    return float(number_string)
    
@dataclass
class Units:
    um : float = 1
    mm : float = 1e3
    cm : float = 1e4
    m  : float = 1e6
    deg : float = 1
    cent_deg: float = 1/100
    rad : float = 180/np.pi
    
@dataclass
class Axis:
    x : str =  "X"
    y : str =  "Y"
    z : str =  "Z"
    rot : str =  "4"
    tilt  : str =  "5"
    
    
@dataclass
class Position:
    x: float = None
    y: float = None
    z: float = None
    rot: float = None   
    tilt: float = None
        
    
class FiveAxisSystem:
    
    def __init__(self, controller : SerialController):
        self.controller = controller
        self.axis_default_units = [Units.um, Units.um, Units.um, Units.cent_deg, Units.cent_deg]

    def _move_single_axis(self, axis: str, pos: int):
        print(f"Moving axis {axis} to position {pos}")
        return self.controller.send(f"{axis}-Achse:{pos}", "500", "100")
        
    def move_to_position(self, position : Position):
        for axis in fields(position):
            val = getattr(position, axis.name)
            if val != None:
                answer = self._move_single_axis(getattr(Axis, axis.name), val)
        self.current_position = self._transform_pos_answer(answer)

    def _transform_pos_answer(self, answer):
        answer_without_ending = answer.split(self.controller.answer_end)
        if len(answer_without_ending) > 1:
            split_axis = answer_without_ending[0].split("Achse:")
            axis_values = [parse_number_string(split_axis[i].split(" ")[0])*self.axis_default_units[i-1] for i in range(1, 6)]
            return Position(*axis_values)
        else:
            return None
        
