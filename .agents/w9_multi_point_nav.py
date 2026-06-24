#!/usr/bin/env python3

import sys
import math
import rospy
import actionlib

from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from geometry_msgs.msg import Quaternion
from actionlib_msgs.msg import GoalStatus


def yaw_to_quaternion(yaw):
    q = Quaternion()
    q.z = math.sin(yaw / 2.0)
    q.w = math.cos(yaw / 2.0)
    return q


class WarehouseNavigator:
    def __init__(self):
        rospy.init_node("w9_multi_point_navigation")

        self.client = actionlib.SimpleActionClient("move_base", MoveBaseAction)

        rospy.loginfo("Waiting for move_base action server...")
        server_ready = self.client.wait_for_server(rospy.Duration(20))

        if not server_ready:
            rospy.logerr("move_base is not running. Start navigation first.")
            sys.exit(1)

        rospy.loginfo("Connected to move_base.")

        # EDIT THESE COORDINATES AFTER CHECKING YOUR RViz MAP
        self.waypoints = [
            ("Home / Charging Station", -2.60, -2.80, -1.5708),
            ("Shelf A Inventory Zone", 2.00, 1.00, 0.0),
            ("Shelf B Inventory Zone", 4.00, 1.00, 0.0),
            ("Pickup Zone", 3.00, -1.00, 1.5708),
            ("Drop-off Zone", 1.00, -2.00, 3.1416),
            ("Return Home", -2.60, -2.80, -1.5708)
        ]

    def send_goal(self, name, x, y, yaw):
        goal = MoveBaseGoal()

        goal.target_pose.header.frame_id = "map"
        goal.target_pose.header.stamp = rospy.Time.now()

        goal.target_pose.pose.position.x = x
        goal.target_pose.pose.position.y = y
        goal.target_pose.pose.position.z = 0.0
        goal.target_pose.pose.orientation = yaw_to_quaternion(yaw)

        rospy.loginfo("Sending robot to: %s | x=%.2f, y=%.2f, yaw=%.2f", name, x, y, yaw)

        self.client.send_goal(goal)
        finished = self.client.wait_for_result(rospy.Duration(120))

        if not finished:
            rospy.logwarn("Timeout. Robot failed to reach: %s", name)
            self.client.cancel_goal()
            return False

        result_state = self.client.get_state()

        if result_state == GoalStatus.SUCCEEDED:
            rospy.loginfo("Arrived at: %s", name)
            return True
        else:
            rospy.logwarn("Failed to reach: %s. Goal state: %s", name, result_state)
            return False

    def run_full_mission(self):
        rospy.loginfo("Starting route: Home -> Shelf A -> Shelf B -> Pickup -> Drop-off -> Home")

        for name, x, y, yaw in self.waypoints:
            success = self.send_goal(name, x, y, yaw)

            if not success:
                rospy.logwarn("Mission stopped because robot failed at: %s", name)
                break

            rospy.sleep(2)

        rospy.loginfo("Warehouse multi-point navigation mission finished.")


if __name__ == "__main__":
    try:
        navigator = WarehouseNavigator()
        navigator.run_full_mission()
    except rospy.ROSInterruptException:
        pass
