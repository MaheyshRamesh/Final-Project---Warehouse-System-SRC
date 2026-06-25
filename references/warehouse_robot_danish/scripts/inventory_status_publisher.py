#!/usr/bin/env python3
import rospy
from std_msgs.msg import String

class InventoryStatusPublisher:
    def __init__(self):
        rospy.init_node('inventory_status_publisher')
        self.pub = rospy.Publisher('/warehouse/inventory_status', String, queue_size=10)
        self.rate = rospy.Rate(1)
        self.states = [
            'SYSTEM READY: TurtleBot3 Burger assigned to warehouse inventory route.',
            'SHELF A: marker board prepared for inventory checking.',
            'SHELF B: delivery item waiting for verification.',
            'DROPOFF: packing station ready to receive item.',
            'HOME: charging station available after mission completion.'
        ]

    def run(self):
        i = 0
        while not rospy.is_shutdown():
            self.pub.publish(self.states[i % len(self.states)])
            i += 1
            self.rate.sleep()

if __name__ == '__main__':
    try:
        InventoryStatusPublisher().run()
    except rospy.ROSInterruptException:
        pass
