#!/usr/bin/env python3
"""Optional move_base waypoint mission.
Run this only after SLAM/navigation is configured and move_base is active.
"""
import rospy
import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from geometry_msgs.msg import Quaternion
import tf.transformations as tft

WAYPOINTS = [
    ("Shelf A", 2.2, 1.3, 0.0),
    ("Shelf C", 2.0, -1.6, -1.57),
    ("Drop-off", -2.4, -3.0, 3.14),
    ("Home", 0.0, -4.0, 1.57),
]

def make_goal(x, y, yaw):
    goal = MoveBaseGoal()
    goal.target_pose.header.frame_id = "map"
    goal.target_pose.header.stamp = rospy.Time.now()
    goal.target_pose.pose.position.x = x
    goal.target_pose.pose.position.y = y
    q = tft.quaternion_from_euler(0, 0, yaw)
    goal.target_pose.pose.orientation = Quaternion(*q)
    return goal

if __name__ == "__main__":
    rospy.init_node("warehouse_waypoint_mission")
    client = actionlib.SimpleActionClient("move_base", MoveBaseAction)
    rospy.loginfo("Waiting for move_base action server...")
    client.wait_for_server()
    rospy.loginfo("Connected to move_base.")

    for name, x, y, yaw in WAYPOINTS:
        rospy.loginfo("Sending goal: %s", name)
        client.send_goal(make_goal(x, y, yaw))
        client.wait_for_result()
        rospy.loginfo("Reached or finished goal: %s", name)
        rospy.sleep(1.0)
