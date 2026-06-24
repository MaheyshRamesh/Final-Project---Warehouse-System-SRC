#!/bin/bash
# Script to launch all TIAGo mapping components in visible terminal windows

# Ensure graphical display variable is set
export DISPLAY=:0
export PATH=~/.local/bin:$PATH

# Kill any previous stuck instances to clean resources
killall -9 gzserver gzclient rosmaster roscore python3 python 2>/dev/null || true
pkill -f ros 2>/dev/null || true

echo "Spinning up Terminal 1: TIAGo Gazebo Simulation (with GUI)..."
gnome-terminal --title="1. TIAGo Gazebo Simulation" --geometry=80x24+0+0 -- bash -c "export PATH=~/.local/bin:\$PATH && source ~/tiago_public_ws/devel/setup.bash && source /home/maheysh/Documents/TTTC2343-Autonomous-Warehouse-Robot-Group-11--main/devel/setup.bash && roslaunch warehouse_robot_danish tiago_spawn.launch gui:=true; exec bash"

# Wait for Gazebo server to spin up
echo "Waiting 12 seconds for Gazebo to initialize..."
sleep 12

echo "Spinning up Terminal 2: SLAM Gmapping Node..."
gnome-terminal --title="2. SLAM Gmapping" --geometry=80x24+600+0 -- bash -c "export PATH=~/.local/bin:\$PATH && source ~/tiago_public_ws/devel/setup.bash && source /home/maheysh/Documents/TTTC2343-Autonomous-Warehouse-Robot-Group-11--main/devel/setup.bash && roslaunch warehouse_robot_danish tiago_mapping.launch scan_topic:=/scan_raw; exec bash"

sleep 3

echo "Spinning up Terminal 3: RViz Visualizer..."
gnome-terminal --title="3. RViz Visualization" --geometry=80x24+0+500 -- bash -c "export PATH=~/.local/bin:\$PATH && source ~/tiago_public_ws/devel/setup.bash && source /home/maheysh/Documents/TTTC2343-Autonomous-Warehouse-Robot-Group-11--main/devel/setup.bash && rosrun rviz rviz -d \$(rospack find warehouse_robot_danish)/config/mapping.rviz; exec bash"

sleep 2

echo "Spinning up Terminal 4: Auto-Mapping Driver Node..."
gnome-terminal --title="4. Auto-Mapping Driver" --geometry=80x24+600+500 -- bash -c "export PATH=~/.local/bin:\$PATH && source ~/tiago_public_ws/devel/setup.bash && rosrun warehouse_robot_danish tiago_autonomous_slam_mapper.py; exec bash"

echo "All components launched successfully in separate, labeled terminals!"
echo "Let the robot drive around for a bit to scan the entire environment in RViz."
echo "When done, run this command in a terminal to save the map:"
echo "source ~/tiago_public_ws/devel/setup.bash && source devel/setup.bash && rosrun map_server map_saver -f \$(pwd)/src/warehouse_robot_danish/maps/tiago_warehouse_map"
