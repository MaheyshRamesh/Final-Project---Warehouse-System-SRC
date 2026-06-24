#!/bin/bash
# run_autonomous_navigation.sh - Launches Phase 2 Autonomous Navigation

export DISPLAY=:0
export PATH=~/.local/bin:$PATH

echo "Cleaning up any old ROS/Gazebo processes..."
killall -9 gzserver gzclient rosmaster roscore python3 python 2>/dev/null || true
pkill -f ros 2>/dev/null || true
sleep 2

echo "Launching TIAGo Autonomous Navigation Suite..."

# Launch all nodes in a single terminal window with tabs mimicking Phase 1
gnome-terminal --window --geometry=100x30 \
  --tab --title="1. Gazebo Simulation" --command="bash -c 'source ~/tiago_public_ws/devel/setup.bash && roslaunch warehouse_robot_danish tiago_spawn.launch gui:=true; exec bash'" \
  --tab --title="2. Navigation & AMCL" --command="bash -c 'sleep 10; source ~/tiago_public_ws/devel/setup.bash && roslaunch warehouse_robot_danish tiago_navigation.launch; exec bash'" \
  --tab --title="3. RViz" --command="bash -c 'sleep 12; source ~/tiago_public_ws/devel/setup.bash && rosrun rviz rviz -d \$(rospack find warehouse_robot_danish)/config/mapping.rviz; exec bash'" \
  --tab --title="4. Station Markers" --command="bash -c 'sleep 15; source ~/tiago_public_ws/devel/setup.bash && rosrun warehouse_robot_danish station_markers.py; exec bash'" \
  --tab --active --title="5. Operator Panel" --command="bash -c 'sleep 18; echo \"====================================\"; echo \"CRITICAL: DO NOT RUN ANY MISSIONS YET!\"; echo \"====================================\"; echo \"1. Go to the RViz window (Tab 3).\"; echo \"2. Click \\\"2D Pose Estimate\\\" in the top toolbar.\"; echo \"3. Click and drag on the map where the robot actually is to localize it.\"; echo \"4. Once localized, press ENTER in this terminal to start the Operator UI.\"; read -p \"Press ENTER after setting 2D Pose Estimate...\" ; source ~/tiago_public_ws/devel/setup.bash && rosrun warehouse_robot_danish operator_panel.py; exec bash'"

echo "Suite launched! Follow the instructions in the Operator Panel tab to localize before using the UI."
