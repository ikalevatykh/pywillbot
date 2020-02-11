import math
import time
from pywillbot import RobotUR5, GripperRG2, SensorFT300

robot = RobotUR5("192.168.1.20")
gripper = GripperRG2(robot)
sensor = SensorFT300(robot)
rx, ry, rz = 0, -math.pi, 0
acc = 0.2
vel = 0.2

gripper.open_gripper()

# pick
robot.movels([(0.0, -0.3, 0.4, rx, ry, rz), (0.0, -0.3, 0.27, rx, ry, rz)],
             acc=acc,
             vel=vel,
             wait=True)
gripper.close_gripper()

# place
robot.movels([(0.0, -0.3, 0.4, rx, ry, rz), (0.0, -0.5, 0.4, rx, ry, rz)],
             acc=acc,
             vel=vel,
             wait=True)
#  - go down
robot.movel((0.0, -0.5, 0.27, rx, ry, rz), acc=0.05, vel=0.05, wait=False)
sensor.set_zero()
count = 1
while sensor.force < 10.0:
    time.sleep(0.01)
    if count % 50 == 0:
        if not robot.is_program_running():
            break
    count += 1
robot.stopl()
gripper.open_gripper()
#  - go up
robot.movel((0.0, -0.5, 0.4, rx, ry, rz), acc=acc, vel=vel, wait=True)

robot.close()