import time
from pywillbot import RobotUR5, SensorFT300

robot = RobotUR5("192.168.1.20")
sensor = SensorFT300(robot)

for i in range(10):
    print(sensor.wrench)
    time.sleep(0.1)


sensor.close()
robot.close()