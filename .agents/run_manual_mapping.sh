#!/bin/bash
# run_manual_mapping.sh - Launches manual SLAM mapping via PS5 Controller Teleop

export DISPLAY=:0
export PATH=~/.local/bin:$PATH

# Clean up previous runs
echo "Cleaning up any old ROS/Gazebo processes..."
killall -9 gzserver gzclient rosmaster roscore python3 python 2>/dev/null || true
pkill -f ros 2>/dev/null || true
sleep 2

echo "Launching TIAGo Mapping Suite..."

# Launch all nodes in a single terminal window with 4 tabs
gnome-terminal --window --geometry=100x30 \
  --tab --title="1. Gazebo Simulation" --command="bash -c 'source ~/tiago_public_ws/devel/setup.bash && roslaunch warehouse_robot_danish tiago_spawn.launch gui:=true; exec bash'" \
  --tab --title="2. SLAM (Gmapping)" --command="bash -c 'sleep 10; source ~/tiago_public_ws/devel/setup.bash && roslaunch warehouse_robot_danish tiago_mapping.launch scan_topic:=/scan_raw; exec bash'" \
  --tab --title="3. RViz" --command="bash -c 'sleep 12; source ~/tiago_public_ws/devel/setup.bash && rosrun rviz rviz -d \$(rospack find warehouse_robot_danish)/config/mapping.rviz; exec bash'" \
  --tab --active --title="4. Controller Teleop" --command="bash -c 'sleep 15; echo \"READY TO DRIVE! Hold the X button (Cross) and use the left joystick to steer.\"; source ~/tiago_public_ws/devel/setup.bash && rosparam set /teleop_node/enable_button 0 && rosrun joy joy_node _autorepeat_rate:=20 & rosrun teleop_twist_joy teleop_node cmd_vel:=joy_vel _enable_button:=0; exec bash'"

echo "Suite launched! Check the new terminal window."
echo "Drive the robot around manually using your PS5 controller."
