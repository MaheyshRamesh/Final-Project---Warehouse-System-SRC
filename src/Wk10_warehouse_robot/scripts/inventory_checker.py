#!/usr/bin/env python3
import rospy
from std_msgs.msg import String

SHELF_STATUS = {
    "A": "OK - product bin A1 detected",
    "B": "LOW STOCK - bin B2 needs refill",
    "C": "OK - product bin C3 detected",
}

if __name__ == "__main__":
    rospy.init_node("inventory_checker")
    pub = rospy.Publisher("/warehouse/inventory_status", String, queue_size=10)
    rate = rospy.Rate(0.5)
    rospy.loginfo("Inventory checker simulation started.")
    while not rospy.is_shutdown():
        for shelf, status in SHELF_STATUS.items():
            msg = f"Shelf {shelf}: {status}"
            rospy.loginfo(msg)
            pub.publish(msg)
            rate.sleep()
