# Warehouse Robot Project Setup and Run Guide

## 1. Copy package
Copy `warehouse_robot` into:

```bash
~/catkin_ws/src/
```

## 2. Build

```bash
cd ~/catkin_ws
catkin_make
source ~/catkin_ws/devel/setup.bash
```

## 3. Install dependencies if needed

```bash
sudo apt update
sudo apt install -y ros-noetic-turtlebot3* ros-noetic-gazebo-ros ros-noetic-xacro ros-noetic-robot-state-publisher
```

## 4. Set TurtleBot3 model

```bash
echo 'export TURTLEBOT3_MODEL=burger' >> ~/.bashrc
source ~/.bashrc
```

## 5. Run immediate demo

Terminal 1:

```bash
roscore
```

Terminal 2:

```bash
source ~/catkin_ws/devel/setup.bash
roslaunch warehouse_robot autonomous_mission.launch
```

## 6. Run world only

```bash
source ~/catkin_ws/devel/setup.bash
roslaunch warehouse_robot manual_world.launch
```

## 7. Optional nodes

Inventory checker:

```bash
rosrun warehouse_robot inventory_checker.py
```

Delivery status simulator:

```bash
rosrun warehouse_robot delivery_runner.py
```

Zone detector:

```bash
rosrun warehouse_robot zone_detector.py
```

## 8. Optional navigation mission
Only run this after you already have TurtleBot3 navigation/move_base working with a map:

```bash
roslaunch warehouse_robot navigation_waypoint_mission.launch
```

## Project concept
The robot represents an autonomous warehouse assistant. It moves between shelf zones, simulates checking inventory, travels to a packing/drop-off station, and returns to a home/charging area.
