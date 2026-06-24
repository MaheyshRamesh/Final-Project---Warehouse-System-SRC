#!/usr/bin/env python3
import math
import rospy
from nav_msgs.msg import Odometry
from std_msgs.msg import String

ZONES = {
    "HOME": (0.0, -4.2),
    "SHELF_A": (2.4, 2.0),
    "SHELF_B": (-2.4, 2.0),
    "SHELF_C": (2.4, -0.9),
    "DROPOFF": (-2.5, -3.0),
}

class ZoneDetector:
    def __init__(self):
        rospy.init_node("warehouse_zone_detector")
        self.pub = rospy.Publisher("/warehouse/current_zone", String, queue_size=10)
        self.last_zone = None
        rospy.Subscriber("/odom", Odometry, self.odom_callback)
        rospy.loginfo("Zone detector started. Monitoring /odom.")

    def odom_callback(self, msg):
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        closest_name = None
        closest_dist = 999.0
        for name, (zx, zy) in ZONES.items():
            dist = math.hypot(x - zx, y - zy)
            if dist < closest_dist:
                closest_name = name
                closest_dist = dist
        if closest_dist < 1.2 and closest_name != self.last_zone:
            self.last_zone = closest_name
            text = f"Robot near zone: {closest_name}"
            rospy.loginfo(text)
            self.pub.publish(text)

if __name__ == "__main__":
    ZoneDetector()
    rospy.spin()
