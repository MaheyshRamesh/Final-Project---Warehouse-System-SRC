#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import String

class MissionController:
    def __init__(self):
        rospy.init_node('warehouse_inventory_delivery_mission')
        self.cmd_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        self.status_pub = rospy.Publisher('/warehouse/mission_log', String, queue_size=10)
        self.rate = rospy.Rate(10)
        rospy.sleep(5.0)  # Give Gazebo time to spawn TurtleBot3.

    def log(self, text):
        rospy.loginfo(text)
        self.status_pub.publish(text)

    def stop(self, delay=1.0):
        self.cmd_pub.publish(Twist())
        rospy.sleep(delay)

    def drive(self, linear_x, angular_z, duration):
        msg = Twist()
        msg.linear.x = linear_x
        msg.angular.z = angular_z
        start = rospy.Time.now().to_sec()
        while not rospy.is_shutdown() and rospy.Time.now().to_sec() - start < duration:
            self.cmd_pub.publish(msg)
            self.rate.sleep()
        self.stop(0.8)

    def simulated_scan(self, shelf_name):
        self.log('Scanning {} marker and checking inventory label...'.format(shelf_name))
        rospy.sleep(2.0)
        self.log('{} verified: item location matches warehouse inventory record.'.format(shelf_name))
        rospy.sleep(1.0)

    def run(self):
        self.log('Mission started: Autonomous Warehouse Inventory and Item Delivery Robot')
        self.log('Leaving home/charging station.')
        self.drive(0.16, 0.0, 5.0)
        self.log('Turning toward Shelf A inventory scan zone.')
        self.drive(0.0, -0.45, 3.0)
        self.drive(0.16, 0.0, 5.0)
        self.simulated_scan('Shelf A')
        self.log('Moving from Shelf A to packing/drop-off station.')
        self.drive(0.0, 0.45, 3.4)
        self.drive(0.17, 0.0, 7.0)
        self.log('Arrived at drop-off station. Simulating item delivery.')
        rospy.sleep(2.0)
        self.log('Item delivered successfully. Returning to safe standby route.')
        self.drive(0.0, 0.45, 3.2)
        self.drive(0.14, 0.0, 4.0)
        self.stop()
        self.log('Mission completed: robot ready for next warehouse task.')

if __name__ == '__main__':
    try:
        MissionController().run()
    except rospy.ROSInterruptException:
        pass
