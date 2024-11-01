import time
import serial
import logging

log = logging.getLogger(__name__)


class SerialController:
    """
    Controls serial communication with a device connected via a serial port.  
    Args:
        port (str): The name of the serial port to connect to (e.g., 'COM5' for Windows or '/dev/ttyUSB0' for Unix systems).
        answer_end (str): The delimiter used to identify the end of a response from the connected device. Defaults to "####".
        timeout (int): The timeout in seconds for reading from the serial port. Defaults to 10 seconds.
    """
    
    def __init__(self, port : str = 'COM5', answer_end : str = "####", timeout : int =10):
        self.ise = serial.Serial(port=port, timeout=timeout)
        self.ise.close()  # Close initially, open only when needed
        self.answer_end = answer_end
        self.sleep_time = 0.65
    def open(self)->None:
        if not self.ise.is_open:
            log.debug(f"Opening device connection")
            self.ise.open()

    def close(self)->None:
        if self.ise.is_open:
            log.debug(f"Closing device connection")
            self.ise.close()
            
    def send(self, *args : str)-> str:
        """
        Sends the specified commands to the connected serial device and reads the response.
        
        The method automatically opens the connection if it's not already open, sends each argument as a command,
        and then closes the connection. Responses are read until the specified 'answer_end' delimiter is encountered.
        
        Args:
            *args: Variable length argument list where each argument is a command to send to the device.
        
        Returns:
            str: The response from the serial device up to and including the 'answer_end' delimiter.
        """
        self.open()
        try:
            for i, arg in enumerate(args):
                log.debug(f"Sending command '{arg}' to device")
                self.ise.write((str(arg)+"\n").encode())
                if i!=len(args)-1:
                    time.sleep(self.sleep_time)
            start = time.time()
            response = self.ise.read_until((self.answer_end).encode(), 1000).decode()
            stop = time.time()
            self.last_answer_time = stop-start
            time.sleep(0.1)
            log.debug(f"Got following response {response} from device after {self.last_answer_time} s")
        except Exception as err:
            log.error(err)
        self.close()
        return response
    