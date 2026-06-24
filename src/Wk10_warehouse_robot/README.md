# Autonomous Warehouse Inventory and Item Delivery Robot

ROS Noetic TurtleBot3 Burger project for a warehouse inventory and item-delivery simulation.

## What it does
- Loads a custom warehouse world in Gazebo.
- Spawns TurtleBot3 Burger.
- Runs a simple autonomous mission using `/cmd_vel`.
- Simulates shelf inventory checking.
- Simulates item delivery to a packing station.
- Includes optional `move_base` waypoint mission script for future navigation integration.

## Quick Run

```bash
cd ~/catkin_ws/src
# copy this warehouse_robot folder here
cd ~/catkin_ws
catkin_make
source ~/catkin_ws/devel/setup.bash
export TURTLEBOT3_MODEL=burger
roslaunch warehouse_robot autonomous_mission.launch
```

## Package Structure

```text
warehouse_robot/
├── launch/
│   ├── autonomous_mission.launch
│   ├── manual_world.launch
│   ├── mission_only.launch
│   ├── navigation_waypoint_mission.launch
│   ├── spawn_robot.launch
│   └── warehouse_world.launch
├── scripts/
│   ├── delivery_runner.py
│   ├── inventory_checker.py
│   ├── mission_controller.py
│   ├── waypoint_mission.py
│   └── zone_detector.py
├── worlds/
│   └── custom_warehouse.world
├── maps/
├── rviz/
├── docs/
│   └── SETUP_AND_RUN.md
├── CMakeLists.txt
└── package.xml
```

## Notes
The default mission uses direct velocity commands so it can run immediately without a saved map. For a stronger final demo, add SLAM and Navigation Stack, then use `waypoint_mission.py`.
