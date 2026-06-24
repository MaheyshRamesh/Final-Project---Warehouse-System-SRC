#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import PointStamped
import math

class WaypointUpdater:
    def __init__(self):
        rospy.init_node('waypoint_updater')
        self.waypoints = []
        self.names = ["Home", "Shelf A", "Shelf B", "Pickup", "Drop-off"]
        
        print("==================================================")
        print("WAYPOINT CALIBRATION SCRIPT")
        print("==================================================")
        print("Open RViz and use the 'Publish Point' tool (top bar).")
        print(f"Please click the exact location for: {self.names[0]}")
        
        rospy.Subscriber("/clicked_point", PointStamped, self.point_callback)
        
    def point_callback(self, msg):
        idx = len(self.waypoints)
        if idx < len(self.names):
            x = round(msg.point.x, 2)
            y = round(msg.point.y, 2)
            print(f"[Captured] {self.names[idx]}: ({x}, {y})")
            self.waypoints.append((x, y))
            
            if len(self.waypoints) < len(self.names):
                print(f"Please click the exact location for: {self.names[len(self.waypoints)]}")
            else:
                self.finish()
                
    def finish(self):
        print("\n==================================================")
        print("ALL WAYPOINTS CAPTURED!")
        print("Here is the updated dictionary for operator_panel.py:")
        print("        self.stations = {")
        print(f"            \"Home\": ({self.waypoints[0][0]}, {self.waypoints[0][1]}, 0.0),")
        print(f"            \"Shelf A\": ({self.waypoints[1][0]}, {self.waypoints[1][1]}, -1.57),")
        print(f"            \"Shelf B\": ({self.waypoints[2][0]}, {self.waypoints[2][1]}, 1.57),")
        print(f"            \"Pickup\": ({self.waypoints[3][0]}, {self.waypoints[3][1]}, 3.14),")
        print(f"            \"Drop-off\": ({self.waypoints[4][0]}, {self.waypoints[4][1]}, 0.0)")
        print("        }")
        
        print("\nHere is the updated list for station_markers.py:")
        print(f"            {{\"id\": 0, \"name\": \"HOME BASE\", \"x\": {self.waypoints[0][0]}, \"y\": {self.waypoints[0][1]}, \"color\": (0.0, 1.0, 0.0)}},")
        print(f"            {{\"id\": 1, \"name\": \"SHELF A\", \"x\": {self.waypoints[1][0]}, \"y\": {self.waypoints[1][1]}, \"color\": (1.0, 1.0, 0.0)}},")
        print(f"            {{\"id\": 2, \"name\": \"SHELF B\", \"x\": {self.waypoints[2][0]}, \"y\": {self.waypoints[2][1]}, \"color\": (1.0, 0.5, 0.0)}},")
        print(f"            {{\"id\": 3, \"name\": \"PICKUP\", \"x\": {self.waypoints[3][0]}, \"y\": {self.waypoints[3][1]}, \"color\": (0.0, 0.5, 1.0)}},")
        print(f"            {{\"id\": 4, \"name\": \"DROP-OFF\", \"x\": {self.waypoints[4][0]}, \"y\": {self.waypoints[4][1]}, \"color\": (1.0, 0.0, 0.0)}}")
        print("==================================================")
        print("Please copy/paste these into the respective scripts, or ask the AI to do it.")
        rospy.signal_shutdown("Finished capturing waypoints.")

if __name__ == '__main__':
    try:
        WaypointUpdater()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
