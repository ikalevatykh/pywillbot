import socket
import time
import threading


class SensorFT300(threading.Thread):
    """FT300 sensor interface
    
        Arguments:
            robot {urx.Robot} -- robot
        
        Keyword Arguments:
            port {int} -- port ot listen on (default: {63351})
    """

    def __init__(self, robot, port=63351):
        super().__init__()
        self._host = robot.host
        self._port = port
        self._lock = threading.Lock()
        self._stop_event = False
        self._wrench = None
        self._bias = [0] * 6

        self.start()
        while self.wrench is None:
            time.sleep(0.1)
        self.set_zero()

    @property
    def wrench(self):
        with self._lock:
            if self._wrench is not None:
                return [float(v) - b for v, b in zip(self._wrench.split(b' , '), self._bias)]

    @property
    def force(self):
        w = self.wrench
        return (w[0]**2 + w[1]**2 + w[2]**2)**0.5

    def set_zero(self):
        self._bias = [0] * 6
        self._bias = self.wrench

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self._host, self._port))
        data = b''
        while not self._stop_event:
            data += sock.recv(1024)
            end = data.rfind(b')')
            start = data.rfind(b'(', 0, end)
            if end - start > 0:
                with self._lock:
                    self._wrench = data[start + 1:end]
                data = b''
        sock.close()

    def stop(self):
        self._stop_event = True

    def close(self):
        self.stop()
        self.join()