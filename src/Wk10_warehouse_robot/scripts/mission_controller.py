#!/usr/bin/env python3
"""Simple warehouse mission controller for TurtleBot3 Burger.
It uses /cmd_vel, so it can run immediately in Gazebo without requiring a saved map.
"""
import rospy
from geometry_msgs.msg import Twist

class WarehouseMissionController:
    def __init__(self):
        rospy.init_node("warehouse_mission_controller", anonymous=False)
        self.cmd_pub = rospy.Publisher("/cmd_vel", Twist, queue_size=10)
        self.rate = rospy.Rate(10)
        rospy.sleep(5.0)  # give Gazebo and robot spawn time to settle
        rospy.loginfo("Warehouse mission controller started.")

    def publish_for(self, linear_x=0.0, angular_z=0.0, seconds=1.0):
        msg = Twist()
        msg.linear.x = linear_x
        msg.angular.z = angular_z
        start = rospy.Time.now().to_sec()
        while not rospy.is_shutdown() and rospy.Time.now().to_sec() - start < seconds:
            self.cmd_pub.publish(msg)
            self.rate.sleep()
        self.stop()

    def stop(self):
        self.cmd_pub.publish(Twist())
        rospy.sleep(0.5)

    def scan_inventory(self, zone_name):
        rospy.loginfo("Arrived at %s. Simulating inventory scan...", zone_name)
        for i in range(1, 4):
            rospy.loginfo("%s scan pass %d/3: shelf marker checked", zone_name, i)
            rospy.sleep(0.7)
        rospy.loginfo("%s scan completed. Inventory status: OK", zone_name)

    def run(self):
        rospy.loginfo("Mission: Home -> Shelf A -> Shelf C -> Drop-off -> Home")

        rospy.loginfo("Leaving charging station.")
        self.publish_for(linear_x=0.18, seconds=7.0)
        self.scan_inventory("Shelf A")

        rospy.loginfo("Turning toward second shelf zone.")
        self.publish_for(angular_z=-0.45, seconds=3.3)
        self.publish_for(linear_x=0.18, seconds=5.5)
        self.scan_inventory("Shelf C")

        rospy.loginfo("Moving to packing/drop-off station.")
        self.publish_for(angular_z=-0.45, seconds=3.1)
        self.publish_for(linear_x=0.18, seconds=5.0)
        rospy.loginfo("Item delivered to drop-off station.")
        rospy.sleep(1.0)

        rospy.loginfo("Returning to home station.")
        self.publish_for(angular_z=0.45, seconds=3.1)
        self.publish_for(linear_x=0.18, seconds=4.0)
        self.stop()
        rospy.loginfo("Warehouse mission completed.")

if __name__ == "__main__":
    try:
        WarehouseMissionController().run()
    except rospy.ROSInterruptException:
        pass
