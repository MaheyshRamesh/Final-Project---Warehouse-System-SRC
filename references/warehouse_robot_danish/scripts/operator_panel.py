#!/usr/bin/env python3
import rospy
from std_msgs.msg import String

class OperatorPanel:
    def __init__(self):
        rospy.init_node('warehouse_operator_panel')
        rospy.Subscriber('/warehouse/inventory_status', String, self.callback)
        rospy.loginfo('Operator panel started. Listening to /warehouse/inventory_status')

    def callback(self, msg):
        rospy.loginfo('[WAREHOUSE STATUS] %s', msg.data)

if __name__ == '__main__':
    OperatorPanel()
    rospy.spin()
