#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import PointStamped

class ExitCapturer:
    def __init__(self):
        rospy.init_node('exit_capturer')
        self.waypoints = []
        self.names = ["Shelf A Exit", "Shelf B Exit"]
        
        print("==================================================")
        print("AISLE EXIT CALIBRATION")
        print("==================================================")
        print(f"Please use 'Publish Point' in RViz to click: {self.names[0]}")
        
        rospy.Subscriber("/clicked_point", PointStamped, self.point_callback)
        
    def point_callback(self, msg):
        idx = len(self.waypoints)
        if idx < len(self.names):
            x = round(msg.point.x, 2)
            y = round(msg.point.y, 2)
            print(f"[Captured] {self.names[idx]}: ({x}, {y})")
            self.waypoints.append((x, y))
            
            if len(self.waypoints) < len(self.names):
                print(f"Please use 'Publish Point' in RViz to click: {self.names[len(self.waypoints)]}")
            else:
                self.finish()
                
    def finish(self):
        print("\n==================================================")
        print("EXIT POINTS CAPTURED!")
        print(f"Shelf A Exit: ({self.waypoints[0][0]}, {self.waypoints[0][1]})")
        print(f"Shelf B Exit: ({self.waypoints[1][0]}, {self.waypoints[1][1]})")
        print("==================================================")
        rospy.signal_shutdown("Finished capturing exits.")

if __name__ == '__main__':
    try:
        ExitCapturer()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
