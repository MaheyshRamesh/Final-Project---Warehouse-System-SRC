# TTTC2343 Autonomous Warehouse Robot Group 11

## Project Overview

This project is a customized robot simulation project for TTTC2343. The system demonstrates an autonomous warehouse inventory and item delivery robot using ROS Noetic, Gazebo, RViz and TurtleBot3 Burger.

The project includes a customized Gazebo warehouse environment, SLAM mapping, autonomous navigation, multi-point navigation, UI-based destination selection, and simulated warehouse task execution.

## Group Members

- Danish Irfan bin Hakimi, A213696
- Shukri Aizat bin Shuazrin, A212202
- Ahmad Nazmi bin Bastian Affendy, A212353
- Maheysh A/L Ramesh, A211881

## Main Features

- Customized warehouse environment in Gazebo
- TurtleBot3 Burger robot integration
- SLAM mapping
- Saved warehouse map
- Autonomous navigation
- Multi-point navigation
- Warehouse robot control UI
- Simulated inventory scanning and item delivery task

## Main ROS Package

The main ROS package is located in:

src/warehouse_robot_danish

## Basic Build Command

cd ~/catkin_ws
catkin_make
source ~/catkin_ws/devel/setup.bash
export TURTLEBOT3_MODEL=burger

## Run Main Simulation

roslaunch warehouse_robot_danish demo_inventory_delivery.launch
