#!/usr/bin/env python3
import rospy
from std_msgs.msg import String

if __name__ == "__main__":
    rospy.init_node("delivery_runner")
    pub = rospy.Publisher("/warehouse/delivery_status", String, queue_size=10)
    rospy.sleep(1.0)
    stages = [
        "Task accepted: deliver item from Shelf A to packing station",
        "Moving to Shelf A",
        "Item pickup simulated",
        "Moving to packing station",
        "Delivery completed",
    ]
    for stage in stages:
        rospy.loginfo(stage)
        pub.publish(stage)
        rospy.sleep(2.0)
