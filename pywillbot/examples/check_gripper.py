import time
from pywillbot import RobotUR5, GripperRG2

robot = RobotUR5("192.168.1.20")
gripper = GripperRG2(robot)

gripper.close_gripper()
print(f'closed width: {gripper.width:0.2f}')

gripper.open_gripper()
print(f'opened width: {gripper.width:0.2f}')

robot.close()