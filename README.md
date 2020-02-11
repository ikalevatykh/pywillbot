# pywillbot
Control WILLBOT without ROS. Useful for simple projects.

# Install

    $ python setup.py install


# Examples

Read wrench data from FT300 sensor:

    $ python -m pywillbot.examples.print_wrench
    
Open/close RG2 gripper:

    $ python -m pywillbot.examples.check_gripper
    
Gently place a part with force feedback:
 
    $ python -m pywillbot.examples.gentle_place
