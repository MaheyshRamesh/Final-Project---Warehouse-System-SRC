#!/usr/bin/env python3
"""
Week 9 Autonomous SLAM Mapping Script
Project: Autonomous Warehouse Inventory and Item Delivery Robot
ROS: Noetic
Robot: TurtleBot3 Burger

Purpose:
Run this script while Gazebo warehouse world and gmapping are already running.
The robot will move around the warehouse using LaserScan obstacle avoidance so
RViz/gmapping can build the warehouse map automatically.

Typical run flow:
1. roslaunch warehouse_robot_danish demo_inventory_delivery.launch
2. roslaunch turtlebot3_slam turtlebot3_slam.launch slam_methods:=gmapping
3. rosrun warehouse_robot_danish w9_autonomous_slam_mapper.py _runtime_minutes:=12
4. rosrun map_server map_saver -f ~/catkin_ws/src/warehouse_robot_danish/maps/warehouse_map
"""

import math
import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan


class W9AutonomousSLAMMapper:
    def __init__(self):
        rospy.init_node("w9_autonomous_slam_mapper", anonymous=False)

        self.cmd_vel_topic = rospy.get_param("~cmd_vel_topic", "/cmd_vel")
        self.scan_topic = rospy.get_param("~scan_topic", "/scan")

        self.runtime_minutes = float(rospy.get_param("~runtime_minutes", 12.0))
        self.forward_speed = float(rospy.get_param("~forward_speed", 0.13))
        self.backup_speed = float(rospy.get_param("~backup_speed", -0.08))
        self.turn_speed = float(rospy.get_param("~turn_speed", 0.55))

        self.front_clearance = float(rospy.get_param("~front_clearance", 0.75))
        self.side_clearance = float(rospy.get_param("~side_clearance", 0.45))
        self.max_valid_range = float(rospy.get_param("~max_valid_range", 3.5))

        self.scan = None
        self.state = "FORWARD"
        self.state_start = rospy.Time.now()
        self.start_time = rospy.Time.now()
        self.turn_direction = 1.0
        self.last_status_time = rospy.Time.now()

        self.cmd_pub = rospy.Publisher(self.cmd_vel_topic, Twist, queue_size=10)
        self.scan_sub = rospy.Subscriber(self.scan_topic, LaserScan, self.scan_callback)

        rospy.on_shutdown(self.stop_robot)

        rospy.loginfo("Week 9 Autonomous SLAM Mapper started.")
        rospy.loginfo("Listening to scan topic: %s", self.scan_topic)
        rospy.loginfo("Publishing velocity to: %s", self.cmd_vel_topic)
        rospy.loginfo("Runtime: %.1f minutes", self.runtime_minutes)

    def scan_callback(self, msg):
        self.scan = msg

    def clean_range(self, value):
        if math.isnan(value) or math.isinf(value) or value <= 0.0:
            return self.max_valid_range
        return min(value, self.max_valid_range)

    def sector_min(self, start_deg, end_deg):
        """Return the nearest obstacle distance in a scan angle sector."""
        if self.scan is None:
            return self.max_valid_range

        start = math.radians(start_deg)
        end = math.radians(end_deg)
        values = []

        for i, raw in enumerate(self.scan.ranges):
            angle = self.scan.angle_min + i * self.scan.angle_increment

            if start <= end:
                inside = start <= angle <= end
            else:
                inside = angle >= start or angle <= end

            if inside:
                values.append(self.clean_range(raw))

        if not values:
            return self.max_valid_range
        return min(values)

    def sector_avg(self, start_deg, end_deg):
        """Return average free space in a scan angle sector."""
        if self.scan is None:
            return self.max_valid_range

        start = math.radians(start_deg)
        end = math.radians(end_deg)
        values = []

        for i, raw in enumerate(self.scan.ranges):
            angle = self.scan.angle_min + i * self.scan.angle_increment

            if start <= end:
                inside = start <= angle <= end
            else:
                inside = angle >= start or angle <= end

            if inside:
                values.append(self.clean_range(raw))

        if not values:
            return self.max_valid_range
        return sum(values) / len(values)

    def change_state(self, new_state):
        if self.state != new_state:
            rospy.loginfo("Mapping state changed: %s -> %s", self.state, new_state)
            self.state = new_state
            self.state_start = rospy.Time.now()

    def elapsed_in_state(self):
        return (rospy.Time.now() - self.state_start).to_sec()

    def runtime_done(self):
        elapsed = (rospy.Time.now() - self.start_time).to_sec()
        return elapsed >= self.runtime_minutes * 60.0

    def choose_turn_direction(self, left_avg, right_avg):
        # Positive angular.z turns left, negative turns right.
        if left_avg >= right_avg:
            self.turn_direction = 1.0
        else:
            self.turn_direction = -1.0

    def build_cmd(self):
        cmd = Twist()

        front = self.sector_min(-22, 22)
        front_left = self.sector_min(22, 65)
        front_right = self.sector_min(-65, -22)
        left_avg = self.sector_avg(60, 120)
        right_avg = self.sector_avg(-120, -60)

        danger_front = front < self.front_clearance
        danger_corner = front_left < self.side_clearance or front_right < self.side_clearance

        # Print status every few seconds, useful as demo evidence.
        if (rospy.Time.now() - self.last_status_time).to_sec() > 5.0:
            rospy.loginfo(
                "State=%s | front=%.2f | left=%.2f | right=%.2f",
                self.state, front, left_avg, right_avg
            )
            self.last_status_time = rospy.Time.now()

        if self.state == "FORWARD":
            if danger_front or danger_corner:
                self.choose_turn_direction(left_avg, right_avg)
                self.change_state("BACKUP")
                cmd.linear.x = self.backup_speed
                cmd.angular.z = 0.0
            else:
                # Move forward slowly. Add small steering so it does not hug one side too much.
                cmd.linear.x = self.forward_speed
                side_error = right_avg - left_avg
                cmd.angular.z = max(min(-0.18 * side_error, 0.22), -0.22)

        elif self.state == "BACKUP":
            cmd.linear.x = self.backup_speed
            cmd.angular.z = 0.0
            if self.elapsed_in_state() > 1.0:
                self.change_state("TURN")

        elif self.state == "TURN":
            cmd.linear.x = 0.0
            cmd.angular.z = self.turn_direction * self.turn_speed

            # Turn at least 1 second, then continue if front area is clear.
            if self.elapsed_in_state() > 1.2 and front > self.front_clearance and not danger_corner:
                self.change_state("FORWARD")

            # If still turning too long, reverse direction to escape corners.
            if self.elapsed_in_state() > 4.0:
                self.turn_direction *= -1.0
                self.change_state("BACKUP")

        return cmd

    def stop_robot(self):
        stop = Twist()
        for _ in range(6):
            self.cmd_pub.publish(stop)
            rospy.sleep(0.05)
        rospy.loginfo("Robot stopped.")

    def run(self):
        rate = rospy.Rate(10)

        rospy.loginfo("Waiting for /scan data...")
        while not rospy.is_shutdown() and self.scan is None:
            rate.sleep()
        rospy.loginfo("LaserScan received. Autonomous mapping movement started.")

        while not rospy.is_shutdown():
            if self.runtime_done():
                rospy.loginfo("Mapping runtime completed.")
                rospy.loginfo("Now save the map using:")
                rospy.loginfo("rosrun map_server map_saver -f ~/catkin_ws/src/warehouse_robot_danish/maps/warehouse_map")
                break

            cmd = self.build_cmd()
            self.cmd_pub.publish(cmd)
            rate.sleep()

        self.stop_robot()


if __name__ == "__main__":
    try:
        mapper = W9AutonomousSLAMMapper()
        mapper.run()
    except rospy.ROSInterruptException:
        pass
