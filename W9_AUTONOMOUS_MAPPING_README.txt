W9 Autonomous SLAM Mapping Script
Project: Autonomous Warehouse Inventory and Item Delivery Robot

FILE INCLUDED
- w9_autonomous_slam_mapper.py

WHAT THIS SCRIPT DOES
This script is used during Week 9 SLAM mapping. It moves the TurtleBot3 Burger around the warehouse automatically while gmapping is running. The robot uses LaserScan obstacle avoidance to explore aisles, avoid shelves and walls, and allow RViz/gmapping to build the warehouse occupancy map.

WHERE TO PUT THE FILE
Copy the Python file into your ROS package scripts folder:

cp w9_autonomous_slam_mapper.py ~/catkin_ws/src/warehouse_robot_danish/scripts/
chmod +x ~/catkin_ws/src/warehouse_robot_danish/scripts/w9_autonomous_slam_mapper.py

BUILD AND SOURCE
cd ~/catkin_ws
catkin_make
source ~/catkin_ws/devel/setup.bash
export TURTLEBOT3_MODEL=burger

RUN FLOW
Terminal 1, launch warehouse world:
roslaunch warehouse_robot_danish demo_inventory_delivery.launch

Terminal 2, launch SLAM/gmapping:
roslaunch turtlebot3_slam turtlebot3_slam.launch slam_methods:=gmapping

Terminal 3, run autonomous mapper:
rosrun warehouse_robot_danish w9_autonomous_slam_mapper.py _runtime_minutes:=12

SAVE MAP AFTER THE ROBOT FINISHES
mkdir -p ~/catkin_ws/src/warehouse_robot_danish/maps
rosrun map_server map_saver -f ~/catkin_ws/src/warehouse_robot_danish/maps/warehouse_map

CHECK MAP FILES
ls ~/catkin_ws/src/warehouse_robot_danish/maps

EXPECTED FILES
warehouse_map.pgm
warehouse_map.yaml

TUNING OPTIONS
If robot moves too fast:
rosrun warehouse_robot_danish w9_autonomous_slam_mapper.py _forward_speed:=0.09

If robot stops too early near shelves:
rosrun warehouse_robot_danish w9_autonomous_slam_mapper.py _front_clearance:=0.60

If you want longer mapping:
rosrun warehouse_robot_danish w9_autonomous_slam_mapper.py _runtime_minutes:=18

IMPORTANT
Make sure the robot starts inside the warehouse. If it starts outside the wall, fix spawn_turtlebot3_burger.launch before running SLAM.
