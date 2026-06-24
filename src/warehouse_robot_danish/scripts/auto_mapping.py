#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
import numpy as np
import random

class AutoMapping:
    def __init__(self):
        rospy.init_node('auto_mapping_driver', anonymous=True)
        
        # Publish velocity commands to twist multiplexer key_vel topic
        self.cmd_pub = rospy.Publisher('/key_vel', Twist, queue_size=10)
        
        # Subscribe to raw scan and odometry topics from TIAGo
        self.scan_sub = rospy.Subscriber('/scan_raw', LaserScan, self.scan_callback)
        self.odom_sub = rospy.Subscriber('/mobile_base_controller/odom', Odometry, self.odom_callback)
        
        self.twist = Twist()
        
        # Sensor states
        self.min_front = 10.0
        self.min_left = 10.0
        self.min_right = 10.0
        self.min_front_right = 10.0
        self.min_front_left = 10.0
        
        # Odometry states for stuck detection
        self.current_x = 0.0
        self.current_y = 0.0
        self.last_x = 0.0
        self.last_y = 0.0
        
        # State machine variables
        self.state = "WANDER"
        self.state_start_time = rospy.Time(0)
        
        # Wander parameters
        self.wander_timer = rospy.Time(0)
        self.wander_yaw_rate = 0.0
        self.wander_duration = rospy.Duration(6.0) # Change curvature every 6s
        
        # Obstacle avoidance parameters
        self.avoid_duration = rospy.Duration(0.0)
        self.avoid_yaw_rate = 0.0
        
        # Stuck detection parameters
        self.last_position_update_time = rospy.Time(0)
        self.stuck_duration = rospy.Duration(1.5) # Trigger stuck if no motion in 1.5s
        self.recovery_phase = 1 # 1: Backup, 2: Pivot
        self.recovery_timer = rospy.Time(0)
        
        self.rate = rospy.Rate(10) # 10 Hz
        rospy.loginfo("Improved State-Machine Auto-mapping driver initialized.")

    def odom_callback(self, data):
        self.current_x = data.pose.pose.position.x
        self.current_y = data.pose.pose.position.y

    def scan_callback(self, data):
        # Laser scan ranges from right to left (-110 deg to +110 deg)
        ranges = np.array(data.ranges)
        # Filter out infs and nans
        ranges = np.where(np.isnan(ranges) | np.isinf(ranges), 10.0, ranges)
        
        num_readings = len(ranges)
        if num_readings == 0:
            return
            
        # Segment the readings, filtering out the robot's self-collisions:
        # We start from index 25 (approx -101.7 deg) to index 565 (approx 77.2 deg)
        # to avoid scanning the robot's own base structure and tucked arm.
        # Slices:
        # Right sector: index 25 to 221 (approx -101.7 to -36.7 deg)
        # Front sector: index 222 to 443 (approx -36.7 to +36.7 deg)
        # Left sector: index 444 to 565 (approx +36.7 to +77.2 deg)
        right_sector = ranges[25 : 222]
        front_right_sector = ranges[222 : 271]
        front_center_sector = ranges[271 : 395]
        front_left_sector = ranges[395 : 444]
        left_sector = ranges[444 : 566]
        
        self.min_right = np.min(right_sector) if len(right_sector) > 0 else 10.0
        self.min_left = np.min(left_sector) if len(left_sector) > 0 else 10.0
        self.min_front = np.min(front_center_sector) if len(front_center_sector) > 0 else 10.0
        self.min_front_right = np.min(front_right_sector) if len(front_right_sector) > 0 else 10.0
        self.min_front_left = np.min(front_left_sector) if len(front_left_sector) > 0 else 10.0

    def run(self):
        # Wait until we receive valid odom data
        rospy.loginfo("Waiting for odometry connection...")
        while not rospy.is_shutdown() and self.current_x == 0.0 and self.current_y == 0.0:
            self.rate.sleep()
        rospy.loginfo("Odometry connected.")
        
        self.last_x = self.current_x
        self.last_y = self.current_y
        self.last_position_update_time = rospy.Time.now()
        self.wander_timer = rospy.Time.now()
        self.state_start_time = rospy.Time.now()
        
        while not rospy.is_shutdown():
            now = rospy.Time.now()
            
            # --- 1. Stuck Detection ---
            # Calculate distance moved
            dist = np.sqrt((self.current_x - self.last_x)**2 + (self.current_y - self.last_y)**2)
            
            trying_to_move = abs(self.twist.linear.x) > 0.05 or abs(self.twist.angular.z) > 0.05
            
            if trying_to_move:
                # If we have moved, reset the stuck timer
                if dist > 0.03:
                    self.last_x = self.current_x
                    self.last_y = self.current_y
                    self.last_position_update_time = now
                else:
                    # Check if we have been stuck for too long
                    if (now - self.last_position_update_time) > self.stuck_duration:
                        if self.state != "RECOVERY":
                            rospy.logwarn("Robot stall detected (odom inactive). Initiating STUCK RECOVERY...")
                            self.state = "RECOVERY"
                            self.recovery_phase = 1
                            self.recovery_timer = now
                            self.state_start_time = now
            else:
                self.last_position_update_time = now
                self.last_x = self.current_x
                self.last_y = self.current_y

            # Timeout Stuck Avoidance: if stuck in AVOID_OBSTACLE state too long (> 5.0 seconds)
            if self.state == "AVOID_OBSTACLE" and (now - self.state_start_time) > rospy.Duration(5.0):
                rospy.logwarn("Robot stuck in obstacle avoidance state too long. Initiating STUCK RECOVERY...")
                self.state = "RECOVERY"
                self.recovery_phase = 1
                self.recovery_timer = now
                self.state_start_time = now

            # --- 2. State Machine Logic ---
            if self.state == "RECOVERY":
                # Phase 1: Reverse at linear.x = -0.15 m/s for 2.0s while turning slightly away from closer obstacle
                if self.recovery_phase == 1:
                    if (now - self.recovery_timer) < rospy.Duration(2.0):
                        self.twist.linear.x = -0.15
                        if self.min_left < self.min_right:
                            self.twist.angular.z = -0.4 # Turn CW (right)
                        else:
                            self.twist.angular.z = 0.4  # Turn CCW (left)
                    else:
                        rospy.loginfo("Recovery Phase 1 complete. Starting Phase 2 (pivoting)...")
                        self.recovery_phase = 2
                        self.recovery_timer = now
                        # Pivot away from closer obstacle
                        self.avoid_yaw_rate = 0.6 if self.min_left > self.min_right else -0.6
                        self.avoid_duration = rospy.Duration(random.uniform(2.0, 3.5))
                
                # Phase 2: Pivot in place to face a completely different angle
                elif self.recovery_phase == 2:
                    if (now - self.recovery_timer) < self.avoid_duration:
                        self.twist.linear.x = 0.0
                        self.twist.angular.z = self.avoid_yaw_rate
                    else:
                        rospy.loginfo("Stuck recovery complete. Resuming WANDER.")
                        self.state = "WANDER"
                        self.wander_timer = now
                        self.last_position_update_time = now
                        self.last_x = self.current_x
                        self.last_y = self.current_y
                        self.state_start_time = now
                        
            elif self.state == "AVOID_OBSTACLE":
                # Pivot in place towards clearer side for a randomized duration to "bounce" clean
                if (now - self.state_start_time) < self.avoid_duration:
                    self.twist.linear.x = 0.0
                    self.twist.angular.z = self.avoid_yaw_rate
                else:
                    # After timer expires, re-evaluate front path
                    front_blocked = (self.min_front < 1.0 or 
                                     self.min_front_right < 0.75 or 
                                     self.min_front_left < 0.75)
                    if front_blocked:
                        rospy.loginfo("Front path still blocked. Continuing to pivot...")
                        self.avoid_yaw_rate = 0.5 if self.min_left > self.min_right else -0.5
                        self.avoid_duration = rospy.Duration(random.uniform(1.0, 2.0))
                        self.state_start_time = now
                    else:
                        rospy.loginfo("Front path clear. Resuming WANDER.")
                        self.state = "WANDER"
                        self.wander_timer = now
                        self.state_start_time = now
                        
            elif self.state == "ALIGN_SIDE":
                # Align to corridor or steer away from side walls
                # Check for critical scrape risks (distance < 0.32m or corners < 0.40m)
                left_scrape = self.min_left < 0.32 or self.min_front_left < 0.40
                right_scrape = self.min_right < 0.32 or self.min_front_right < 0.40
                
                front_blocked = (self.min_front < 1.0 or 
                                 self.min_front_right < 0.75 or 
                                 self.min_front_left < 0.75)
                
                if front_blocked:
                    rospy.loginfo("Front obstacle detected during side alignment. Switching to AVOID_OBSTACLE.")
                    self.state = "AVOID_OBSTACLE"
                    self.avoid_yaw_rate = 0.5 if self.min_left > self.min_right else -0.5
                    self.avoid_duration = rospy.Duration(random.uniform(1.5, 2.5))
                    self.state_start_time = now
                elif left_scrape:
                    # Critical scrape risk on left: pivot right in place
                    self.twist.linear.x = 0.0
                    self.twist.angular.z = -0.5
                elif right_scrape:
                    # Critical scrape risk on right: pivot left in place
                    self.twist.linear.x = 0.0
                    self.twist.angular.z = 0.5
                else:
                    # Gentle steering away while moving forward
                    self.twist.linear.x = 0.18
                    if self.min_left < self.min_right:
                        self.twist.angular.z = -0.3 # steer right
                    else:
                        self.twist.angular.z = 0.3  # steer left
                        
                    # Check if cleared side walls
                    if self.min_left > 0.55 and self.min_right > 0.55:
                        rospy.loginfo("Side clearance restored. Resuming WANDER.")
                        self.state = "WANDER"
                        self.wander_timer = now
                        self.state_start_time = now
                        
            else: # WANDER State
                # Check for obstacles
                front_blocked = (self.min_front < 1.0 or 
                                 self.min_front_right < 0.75 or 
                                 self.min_front_left < 0.75)
                
                if front_blocked:
                    rospy.loginfo(f"Obstacle in front (front: {self.min_front:.2f}m, FL: {self.min_front_left:.2f}m, FR: {self.min_front_right:.2f}m). Switching to AVOID_OBSTACLE.")
                    self.state = "AVOID_OBSTACLE"
                    self.avoid_yaw_rate = 0.5 if self.min_left > self.min_right else -0.5
                    self.avoid_duration = rospy.Duration(random.uniform(1.5, 2.5))
                    self.state_start_time = now
                elif self.min_left < 0.45 or self.min_right < 0.45:
                    rospy.loginfo(f"Approaching side wall (left: {self.min_left:.2f}m, right: {self.min_right:.2f}m). Switching to ALIGN_SIDE.")
                    self.state = "ALIGN_SIDE"
                    self.state_start_time = now
                else:
                    # Periodically change direction slightly to prevent loops/death-spirals
                    if (now - self.wander_timer) > self.wander_duration:
                        r = random.random()
                        if r < 0.6:
                            # 60% chance to go straight
                            self.wander_yaw_rate = 0.0
                        elif r < 0.8:
                            # 20% chance to curve left
                            self.wander_yaw_rate = random.uniform(0.05, 0.15)
                        else:
                            # 20% chance to curve right
                            self.wander_yaw_rate = random.uniform(-0.15, -0.05)
                        self.wander_timer = now
                    
                    self.twist.linear.x = 0.30
                    self.twist.angular.z = self.wander_yaw_rate
            
            self.cmd_pub.publish(self.twist)
            self.rate.sleep()

if __name__ == '__main__':
    try:
        driver = AutoMapping()
        driver.run()
    except rospy.ROSInterruptException:
        pass
