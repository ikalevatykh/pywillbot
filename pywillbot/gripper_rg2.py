import math
import time

from urx.urscript import URScript


class GripperRG2:
    """RG2 gripper interface
    
        Arguments:
            robot {urx.Robot} -- robot
        
        Keyword Arguments:
            slow_mode {bool} -- decrease gripper velocity (default: {False})
    """

    def __init__(self, robot, slow_mode=False):
        self._robot = robot
        if not self.ready:
            self.init_gripper()

    def init_gripper(self):
        print('initializing gripper...')
        self._send_program('set_tool_voltage(24)')
        counter = 0
        while counter < 2:
            time.sleep(1)
            if self.ready:
                counter += 1
        print('gripper OK')

    def open_gripper(self, wait=2):
        self._send_program('set_digital_out(8,False)')
        time.sleep(wait)

    def close_gripper(self, wait=2):
        self._send_program('set_digital_out(8,True)')
        time.sleep(wait)

    @property
    def ready(self):
        return self._robot.get_digital_in(17, wait=True) == 1

    @property
    def width(self):
        voltage = self._robot.secmon._dict["ToolData"]["analogInput2"]
        return 110 * voltage / 3.05

    @property
    def object_gripped(self):
        return self._robot.get_digital_in(16) > 0

    def _send_program(self, program):
        urscript = URScript()
        urscript.add_line_to_program(program)
        self._robot.send_program(urscript())
