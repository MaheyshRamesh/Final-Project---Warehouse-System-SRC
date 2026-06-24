#!/bin/bash
# run_manual_mapping_keyboard.sh - Launches manual SLAM mapping via Keyboard Teleop in a single window

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
  --tab --active --title="4. Keyboard Teleop" --command="bash -c 'sleep 15; echo \"READY TO DRIVE! Use your arrow keys to steer the robot.\"; source ~/tiago_public_ws/devel/setup.bash && rosrun key_teleop key_teleop.py; exec bash'"

echo "Suite launched! Check the new terminal window."
echo "Drive the robot around manually using the '4. Keyboard Teleop' tab."
