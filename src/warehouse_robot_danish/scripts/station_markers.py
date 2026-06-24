#!/usr/bin/env python3

import rospy
from visualization_msgs.msg import Marker, MarkerArray

class StationMarkers:
    def __init__(self):
        rospy.init_node('station_markers')
        self.pub = rospy.Publisher('/warehouse/station_markers', MarkerArray, queue_size=1, latch=True)

        self.stations = [
            {"id": 0, "name": "HOME BASE", "x": 1.31, "y": -2.23, "color": (0.0, 1.0, 0.0)},      # Green
            {"id": 1, "name": "SHELF A", "x": 8.75, "y": -2.20, "color": (0.0, 0.8, 1.0)},        # Light Blue
            {"id": 2, "name": "SHELF B", "x": 8.75, "y": -7.31, "color": (0.0, 0.4, 1.0)},        # Dark Blue
            {"id": 3, "name": "PICKUP ZONE", "x": 2.00, "y": -9.16, "color": (1.0, 0.64, 0.0)},  # Orange
            {"id": 4, "name": "DROP-OFF", "x": 7.08, "y": 5.49, "color": (1.0, 0.0, 0.0)}       # Red
        ]

    def create_marker(self, station):
        marker = Marker()
        marker.header.frame_id = "map"
        marker.header.stamp = rospy.Time.now()
        marker.ns = "stations"
        marker.id = station["id"]
        marker.type = Marker.TEXT_VIEW_FACING
        marker.action = Marker.ADD

        # Position (Hover 2.5 meters above ground)
        marker.pose.position.x = station["x"]
        marker.pose.position.y = station["y"]
        marker.pose.position.z = 2.5
        marker.pose.orientation.w = 1.0

        # Scale (Text size)
        marker.scale.z = 0.6  # Giant text

        # Color
        marker.color.r = station["color"][0]
        marker.color.g = station["color"][1]
        marker.color.b = station["color"][2]
        marker.color.a = 1.0

        marker.text = station["name"]
        return marker

    def run(self):
        rate = rospy.Rate(1) # Publish once per second
        while not rospy.is_shutdown():
            marker_array = MarkerArray()
            for station in self.stations:
                marker_array.markers.append(self.create_marker(station))
            
            self.pub.publish(marker_array)
            rate.sleep()

if __name__ == '__main__':
    try:
        node = StationMarkers()
        node.run()
    except rospy.ROSInterruptException:
        pass
