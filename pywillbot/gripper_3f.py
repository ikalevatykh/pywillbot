import socket
import time
import threading

from .robotiq import modbus_tcp

__all__ = ['Gripper3F']


class Gripper3F(threading.Thread):
    """Robotiq 3 finger gripper interface
        
        Keyword Arguments:
            address {str} -- gripper IP address (default: {'192.168.1.11'})
    """

    def __init__(self, address='192.168.1.11'):
        super().__init__()
        self._address = address
        self._lock = threading.Lock()
        self._stop_event = False
        self._status = Status()
        self._command = Command()

        self.start()
        self.activate()

    @property
    def ready(self):
        """ Activation and mode change are completed """
        with self._lock:
            return self._status.gIMC == 0x03

    def activate(self):
        """ Activate gripper """
        with self._lock:
            self._command.rACT = 1
            self._command.rGTO = 1
            self._command.rSPA = 255
            self._command.rFRA = 150

        while not self.ready:
            time.sleep(0.1)

    def change_mode(self, mode):
        """ Change gripper mode """
        with self._lock:
            self._command.rMOD = mode

        while not self.ready:
            time.sleep(0.1)

    def basic_mode(self):
        self.change_mode(0)

    def pinch_mode(self):
        self.change_mode(1)

    def wide_mode(self):
        self.change_mode(2)

    @property
    def moving(self):
        """ Motion status """
        with self._lock:
            return self._status.gSTA == 0x00

    @property
    def target_position(self):
        """ Echo of the requested position (0-255) """
        with self._lock:
            return self._status.gPRA

    @property
    def position(self):
        """ Actual position (0-255) """
        with self._lock:
            return self._status.gPOA

    def set_velocity(self, velocity):
        """ Set target velocity

            Arguments:
                velocity {int} -- target velocity (0x00 - 0x255)
        """
        with self._lock:
            self._command.rSPA = velocity

    def set_force(self, force):
        """ Set target force

            Arguments:
                force {int} -- target force (0x00 - 0x255)
        """
        with self._lock:
            self._command.rFRA = velocity

    def move(self, width, wait=True):
        """ Move fingers

            Arguments:
                width {int} -- fingers position (0x00 - full opening, 0x255 - full closing)
            
            Keyword Arguments:
                wait {bool} -- wait until gripper stop (default: {True})
        """
        with self._lock:
            self._command.rPRA = width

        while wait and self.moving:
            time.sleep(0.1)

    def close(self, wait=True):
        """ Close fingers """
        self.move(255, wait)

    def open(self, wait, width=0):
        """ Open fingers """
        self.move(0, wait)

    def run(self):
        client = modbus_tcp.communication()
        client.connectToDevice(self._address)

        while not self._stop_event:
            # get status
            status = client.getStatus(16)
            time.sleep(0.05)

            with self._lock:
                self._status = Status(status)
                message = self._command.message()

            # send the most recent command
            client.sendCommand(message)
            time.sleep(0.05)

        client.disconnectFromDevice()

    def stop(self):
        self._stop_event = True

    def close(self):
        self.stop()
        self.join()


class Status:

    def __init__(self, status=[0] * 16):
        self.gACT = (status[0] >> 0) & 0x01
        self.gMOD = (status[0] >> 1) & 0x03
        self.gGTO = (status[0] >> 3) & 0x01
        self.gIMC = (status[0] >> 4) & 0x03
        self.gSTA = (status[0] >> 6) & 0x03
        self.gDTA = (status[1] >> 0) & 0x03
        self.gDTB = (status[1] >> 2) & 0x03
        self.gDTC = (status[1] >> 4) & 0x03
        self.gDTS = (status[1] >> 6) & 0x03
        self.gFLT = status[2]
        self.gPRA = status[3]
        self.gPOA = status[4]
        self.gCUA = status[5]
        self.gPRB = status[6]
        self.gPOB = status[7]
        self.gCUB = status[8]
        self.gPRC = status[9]
        self.gPOC = status[10]
        self.gCUC = status[11]
        self.gPRS = status[12]
        self.gPOS = status[13]
        self.gCUS = status[14]


class Command:

    def __init__(self):
        self.rACT = 0
        self.rMOD = 0
        self.rGTO = 0
        self.rATR = 0
        self.rGLV = 0
        self.rICF = 0
        self.rICS = 0
        self.rPRA, self.rSPA, self.rFRA = 0, 0, 0
        self.rPRB, self.rSPB, self.rFRB = 0, 0, 0
        self.rPRC, self.rSPC, self.rFRC = 0, 0, 0
        self.rPRS, self.rSPS, self.rFRS = 0, 0, 0

    def message(self):
        clamp = lambda n, smallest, largest: max(smallest, min(n, largest))

        rACT = clamp(self.rACT, 0, 1)
        rMOD = clamp(self.rACT, 0, 3)
        rGTO = clamp(self.rGTO, 0, 1)
        rATR = clamp(self.rATR, 0, 1)
        rGLV = clamp(self.rGLV, 0, 1)
        rICF = clamp(self.rICF, 0, 1)
        rICS = clamp(self.rICS, 0, 1)

        return [
            rACT + (rMOD << 1) + (rGTO << 3) + (rATR << 4),
            rGLV + (rICF << 2) + (rICS << 3),  #
            0,
            clamp(self.rPRA, 0, 255),
            clamp(self.rSPA, 0, 255),
            clamp(self.rFRA, 0, 255),
            clamp(self.rPRB, 0, 255),
            clamp(self.rSPB, 0, 255),
            clamp(self.rFRB, 0, 255),
            clamp(self.rPRC, 0, 255),
            clamp(self.rSPC, 0, 255),
            clamp(self.rFRC, 0, 255),
            clamp(self.rPRS, 0, 255),
            clamp(self.rSPS, 0, 255),
            clamp(self.rFRS, 0, 255)
        ]
