#!/bin/bash
export DISPLAY=:0
export PATH=~/.local/bin:$PATH

echo "Cleaning up any old ROS processes..."
killall -9 gzserver gzclient rosmaster roscore python3 python 2>/dev/null || true
pkill -f ros 2>/dev/null || true
sleep 2

echo "Launching Depth Camera Mapping Stack..."

gnome-terminal --window --geometry=120x35 \
  --tab --title="1. Gazebo" --command="bash -c 'source ~/tiago_public_ws/devel/setup.bash && roslaunch warehouse_robot_danish tiago_spawn.launch gui:=true; exec bash'" \
  --tab --title="2. Depth SLAM" --command="bash -c 'sleep 8; source ~/tiago_public_ws/devel/setup.bash && roslaunch warehouse_robot_danish tiago_mapping_depth.launch; exec bash'" \
  --tab --title="3. RViz" --command="bash -c 'sleep 10; source ~/tiago_public_ws/devel/setup.bash && rosrun rviz rviz -d \$(rospack find warehouse_robot_danish)/config/mapping.rviz; exec bash'" \
  --tab --active --title="4. Joypad Teleop" --command="bash -c 'sleep 12; echo \"Use your DS5 controller to drive the robot around and map the warehouse.\"; source ~/tiago_public_ws/devel/setup.bash && rosrun joy joy_node dev:=/dev/input/js0 & rosrun teleop_twist_joy teleop_node _enable_button:=0 _axis_linear:=1 _axis_angular:=0 _scale_linear:=1.0 _scale_angular:=1.0 cmd_vel:=joy_vel; exec bash'"

echo "Launched successfully!"
