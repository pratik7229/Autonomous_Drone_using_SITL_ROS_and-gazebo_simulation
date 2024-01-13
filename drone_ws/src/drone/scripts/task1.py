#!/usr/bin/env python

import rospy
from mavros_msgs.srv import CommandBool, SetMode
from mavros_msgs.srv import CommandTOL
from mavros_msgs.msg import State
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Header
import time

class DroneController:
    def __init__(self):
        rospy.init_node('drone_controller', anonymous=True)

        self.current_state = State()
        self.current_pose = PoseStamped()

        # Subscribe to the MAVROS state and local position topics
        rospy.Subscriber('/mavros/state', State, self.state_callback)
        rospy.Subscriber('/mavros/local_position/pose', PoseStamped, self.pose_callback)

        # Create services for arming and setting mode
        self.arming_client = rospy.ServiceProxy('/mavros/cmd/arming', CommandBool)
        self.set_mode_client = rospy.ServiceProxy('/mavros/set_mode', SetMode)

        # Create a publisher for the local position goal
        self.pose_goal_pub = rospy.Publisher('/mavros/setpoint_position/local', PoseStamped, queue_size=10)

    def state_callback(self, state):
        self.current_state = state

    def pose_callback(self, pose):
        self.current_pose = pose

    def arm(self):
        rospy.wait_for_service('/mavros/cmd/arming')
        try:
            self.set_mode('GUIDED')
            self.arming_client(True)
            rospy.loginfo("Drone armed")
        except rospy.ServiceException as e:
            rospy.logerr("Service call failed: %s", e)

    def set_mode(self, mode):
        rospy.wait_for_service('/mavros/set_mode')
        try:
            self.set_mode_client(0, mode)
            rospy.loginfo("Mode set to %s", mode)
        except rospy.ServiceException as e:
            rospy.logerr("Service call failed: %s", e)

    def takeoff(self):
        rospy.wait_for_service('/mavros/cmd/takeoff')
        try:
            takeoff = rospy.ServiceProxy('/mavros/cmd/takeoff', CommandTOL)
            response = takeoff(altitude=10.0)  # Set the desired takeoff altitude
            rospy.loginfo("Takeoff command sent. Response: %s", response)
        except rospy.ServiceException as e:
            rospy.logerr("Service call failed: %s", e)

    def land(self):
        # Set the mode to LAND
        self.set_mode('LAND')
        rospy.loginfo("Landing...")

if __name__ == "__main__":
    try:
        controller = DroneController()

        # Arm the drone
        controller.arm()

        # Change the mode to GUIDED
        controller.set_mode('GUIDED')

        # Take off
        controller.takeoff()

        # Wait for 10 seconds
        rospy.loginfo("Waiting for 10 seconds...")
        time.sleep(10.0)

        # Land the drone
        controller.land()

        rospy.spin()

    except rospy.ROSInterruptException:
        pass
