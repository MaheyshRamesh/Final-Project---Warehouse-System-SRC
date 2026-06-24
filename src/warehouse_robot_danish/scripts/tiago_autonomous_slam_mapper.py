#!/usr/bin/env python3
"""
Week 9 Autonomous SLAM Mapping Script (Adapted for TIAGo)
Project: Autonomous Warehouse Inventory and Item Delivery Robot
ROS: Noetic
Robot: TIAGo

Purpose:
Run this script while Gazebo warehouse world and gmapping are already running.
The robot will move around the warehouse using LaserScan obstacle avoidance so
RViz/gmapping can build the warehouse map automatically.
"""

import math
import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan, Image
from nav_msgs.msg import Odometry, OccupancyGrid
import numpy as np
from cv_bridge import CvBridge
import tf
import tf.transformations


class TiagoAutonomousSLAMMapper:
    def __init__(self):
        rospy.init_node("tiago_autonomous_slam_mapper", anonymous=False)

        self.cmd_vel_topic = rospy.get_param("~cmd_vel_topic", "/key_vel")
        self.scan_topic = rospy.get_param("~scan_topic", "/scan_raw")

        self.runtime_minutes = float(rospy.get_param("~runtime_minutes", 12.0))
        self.forward_speed = float(rospy.get_param("~forward_speed", 0.25))
        self.backup_speed = float(rospy.get_param("~backup_speed", -0.15))
        self.turn_speed = float(rospy.get_param("~turn_speed", 0.55))

        self.front_clearance = float(rospy.get_param("~front_clearance", 0.25))
        self.side_clearance = float(rospy.get_param("~side_clearance", 0.25))
        self.max_valid_range = float(rospy.get_param("~max_valid_range", 3.5))

        self.scan = None
        self.state = "FORWARD"
        self.state_start = rospy.Time.now()
        self.start_time = rospy.Time.now()
        self.turn_direction = 1.0
        self.last_status_time = rospy.Time.now()

        self.cmd_pub = rospy.Publisher(self.cmd_vel_topic, Twist, queue_size=10)
        self.scan_sub = rospy.Subscriber(self.scan_topic, LaserScan, self.scan_callback)

        self.actual_linear_x = 0.0
        self.odom_sub = rospy.Subscriber("/mobile_base_controller/odom", Odometry, self.odom_callback)

        self.bridge = CvBridge()
        self.depth_front = self.max_valid_range
        self.depth_sub = rospy.Subscriber("/xtion/depth_registered/image_raw", Image, self.depth_callback)

        self.map_grid = None
        self.map_info = None
        self.tf_listener = tf.TransformListener()
        self.map_sub = rospy.Subscriber("/map", OccupancyGrid, self.map_callback)

        rospy.on_shutdown(self.stop_robot)

        rospy.loginfo("TIAGo Autonomous SLAM Mapper started.")
        rospy.loginfo("Listening to scan topic: %s", self.scan_topic)
        rospy.loginfo("Publishing velocity to: %s", self.cmd_vel_topic)
        rospy.loginfo("Runtime: %.1f minutes", self.runtime_minutes)

    def scan_callback(self, msg):
        self.scan = msg

    def map_callback(self, msg):
        self.map_grid = np.array(msg.data).reshape((msg.info.height, msg.info.width))
        self.map_info = msg.info

    def odom_callback(self, msg):
        self.actual_linear_x = msg.twist.twist.linear.x

    def depth_callback(self, msg):
        try:
            depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
            h, w = depth_image.shape
            center_region = depth_image[h//2:h//2+150, w//2-100:w//2+100]
            valid = center_region[(center_region > 0) & (~np.isnan(center_region))]
            if len(valid) > 0:
                self.depth_front = np.min(valid)
            else:
                self.depth_front = self.max_valid_range
        except Exception as e:
            rospy.logwarn_throttle(2.0, "Depth image error: %s", str(e))

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

    def evaluate_unexplored(self, relative_angle):
        if self.map_grid is None or self.map_info is None:
            return 0
        try:
            (trans, rot) = self.tf_listener.lookupTransform('/map', '/base_footprint', rospy.Time(0))
            _, _, robot_yaw = tf.transformations.euler_from_quaternion(rot)
            target_yaw = robot_yaw + relative_angle
            
            res = self.map_info.resolution
            ox = self.map_info.origin.position.x
            oy = self.map_info.origin.position.y
            
            rx = int((trans[0] - ox) / res)
            ry = int((trans[1] - oy) / res)
            
            unexplored_count = 0
            for r in range(10, 60):
                for a in np.linspace(-0.5, 0.5, 5):
                    cx = rx + int(r * math.cos(target_yaw + a))
                    cy = ry + int(r * math.sin(target_yaw + a))
                    if 0 <= cx < self.map_info.width and 0 <= cy < self.map_info.height:
                        if self.map_grid[cy, cx] == -1:
                            unexplored_count += 1
            return unexplored_count
        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
            return 0

    def choose_turn_direction(self, left_avg, right_avg):
        left_unexplored = self.evaluate_unexplored(math.pi / 2.0)
        right_unexplored = self.evaluate_unexplored(-math.pi / 2.0)
        
        rospy.loginfo("Map evaluation - Left Unknowns: %d, Right Unknowns: %d", left_unexplored, right_unexplored)
        
        if left_unexplored > right_unexplored + 10:
            self.turn_direction = 1.0
        elif right_unexplored > left_unexplored + 10:
            self.turn_direction = -1.0
        else:
            if left_avg >= right_avg:
                self.turn_direction = 1.0
            else:
                self.turn_direction = -1.0

    def build_cmd(self):
        cmd = Twist()

        front = self.sector_min(-22, 22)
        front_left = self.sector_min(22, 65)
        front_right = self.sector_min(-65, -22)
        # Shifted from ±60-120 to ±100-150 to ignore TIAGo's chassis.
        left_avg = self.sector_avg(100, 150)
        right_avg = self.sector_avg(-150, -100)

        danger_front = front < self.front_clearance or self.depth_front < (self.front_clearance + 0.1)
        danger_corner = front_left < self.side_clearance or front_right < self.side_clearance

        if (rospy.Time.now() - self.last_status_time).to_sec() > 5.0:
            rospy.loginfo(
                "State=%s | front=%.2f | left=%.2f | right=%.2f",
                self.state, front, left_avg, right_avg
            )
            self.last_status_time = rospy.Time.now()

        if self.state == "FORWARD":
            stuck = self.elapsed_in_state() > 2.0 and abs(self.actual_linear_x) < 0.02
            if danger_front or danger_corner or stuck:
                if stuck:
                    rospy.logwarn("Robot is physically stuck (hit unseen obstacle)! Reversing...")
                self.choose_turn_direction(left_avg, right_avg)
                self.change_state("BACKUP")
                cmd.linear.x = self.backup_speed
                cmd.angular.z = 0.0
            else:
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

            if self.elapsed_in_state() > 1.5 and front > self.front_clearance and self.depth_front > (self.front_clearance + 0.1) and not danger_corner:
                self.change_state("FORWARD")

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

        rospy.loginfo("Waiting for /scan_raw data...")
        while not rospy.is_shutdown() and self.scan is None:
            rate.sleep()
        rospy.loginfo("LaserScan received. Autonomous mapping movement started.")

        while not rospy.is_shutdown():
            if self.runtime_done():
                rospy.loginfo("Mapping runtime completed.")
                rospy.loginfo("Now save the map using:")
                rospy.loginfo("rosrun map_server map_saver -f ~/tiago_public_ws/src/warehouse_robot_danish/maps/tiago_warehouse_map")
                break

            cmd = self.build_cmd()
            self.cmd_pub.publish(cmd)
            rate.sleep()

        self.stop_robot()


if __name__ == "__main__":
    try:
        mapper = TiagoAutonomousSLAMMapper()
        mapper.run()
    except rospy.ROSInterruptException:
        pass
