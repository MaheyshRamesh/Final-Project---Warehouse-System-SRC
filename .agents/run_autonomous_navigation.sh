#!/bin/bash
export DISPLAY=:0
export PATH=~/.local/bin:$PATH

echo "Cleaning up any old ROS processes..."
killall -9 gzserver gzclient rosmaster roscore python3 python 2>/dev/null || true
pkill -f ros 2>/dev/null || true
sleep 2

echo "Injecting Costmap Recovery Fix into TIAGo Navigation Config..."
cp ~/Documents/TTTC2343-Autonomous-Warehouse-Robot-Group-11--main/src/warehouse_robot_danish/config/recovery_behaviors.yaml ~/tiago_public_ws/src/pal_navigation_cfg_public/pal_navigation_cfg_tiago/config/base/common/recovery_behaviors.yaml


echo "Launching Phase 2 Navigation Stack..."

gnome-terminal --window --geometry=120x35 \
  --tab --title="1. Gazebo" --command="bash -c 'source ~/tiago_public_ws/devel/setup.bash && roslaunch warehouse_robot_danish tiago_spawn.launch gui:=true; exec bash'" \
  --tab --title="2. Navigation & AMCL" --command="bash -c 'sleep 8; source ~/tiago_public_ws/devel/setup.bash && roslaunch warehouse_robot_danish tiago_navigation.launch; exec bash'" \
  --tab --title="3. RViz" --command="bash -c 'sleep 10; source ~/tiago_public_ws/devel/setup.bash && rosrun rviz rviz -d \$(rospack find warehouse_robot_danish)/config/mapping.rviz; exec bash'" \
  --tab --title="4. Station Markers" --command="bash -c 'sleep 15; source ~/tiago_public_ws/devel/setup.bash && rosrun warehouse_robot_danish station_markers.py; exec bash'" \
  --tab --active --title="5. Operator Panel" --command="bash -c 'sleep 18; echo \"\"; echo \"======================================================\"; echo \"ACTION REQUIRED: SET 2D POSE ESTIMATE IN RVIZ FIRST!\"; echo \"======================================================\"; echo \"Wait for the map to load in RViz, then:\"; echo \"1. Click \\\"2D Pose Estimate\\\"\"; echo \"2. Click exactly where TIAGo is in the warehouse.\"; echo \"3. Drag the green arrow so it points the same way TIAGo is facing.\"; echo \"\"; echo \"ONLY AFTER YOU HAVE DONE THIS, press ENTER to launch the Operator Panel UI.\"; read; source ~/tiago_public_ws/devel/setup.bash && rosrun warehouse_robot_danish operator_panel.py; exec bash'"

echo "Launched successfully!"
