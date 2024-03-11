import time
import serial
import logging

log = logging.getLogger(__name__)


class SerialController:
    def __init__(self, port: str = "COM5", answer_end: str = "####", timeout: int = 10):
        self.ise = serial.Serial(port=port, timeout=timeout)
        self.ise.close()  # Close initially, open only when needed
        self.answer_end = answer_end
        self.sleep_time = 0.5

    def open(self) -> None:
        if not self.ise.is_open:
            log.debug(f"Opening device connection")
            self.ise.open()

    def close(self) -> None:
        if self.ise.is_open:
            log.debug(f"Closing device connection")
            self.ise.close()

    def send(self, *args: str) -> str:
        self.open()
        try:
            for i, arg in enumerate(args):
                log.debug(f"Sending command {arg} to device")
                self.ise.write((str(arg) + "\r\n").encode())
                if i != len(args) - 1:
                    time.sleep(self.sleep_time)
            start = time.time()
            response = self.ise.read_until((self.answer_end).encode(), 100).decode()
            stop = time.time()
            self.last_answer_time = stop - start
            time.sleep(0.1)

            log.debug(
                f"Got following response {response} from device after {self.last_answer_time} s"
            )
        except Exception as err:
            log.error(err)
        self.close()
        return response
