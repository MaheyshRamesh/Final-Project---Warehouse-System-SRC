# 🤖 TIAGo Autonomous Warehouse Inventory & Delivery Robot
**Course:** TTTC2343 Customized Robot Simulation Development  
**Group:** 11  

## 📖 Project Overview
This repository contains the complete ROS Noetic simulation package for an autonomous warehouse assistant. Built entirely within Gazebo using the **TIAGo mobile robot**, this system executes a full logistics pipeline: leaving a charging dock, navigating narrow inventory aisles, utilizing computer vision to scan QR codes for stock verification, and delivering items to a drop-off station.

This project goes significantly beyond basic point-to-point navigation by implementing 3D depth-camera sensor fusion for dynamic obstacle avoidance, actionlib state machines, and an intelligent intercept-routing User Interface.

## 👥 Group Members
- **Danish Irfan bin Hakimi (A213696)**
- **Shukri Aizat bin Shuazrin (A212202)**
- **Ahmad Nazmi bin Bastian Affendy (A212353)**
- **Maheysh A/L Ramesh (A211881)**

---

## ✨ Core Technical Features

### 1. 3D Sensor Fusion for SLAM Mapping
TIAGo's default 2D laser scanner is mounted too high to detect thin shelf legs or low-lying boxes. We successfully implemented a sensor fusion pipeline using `pointcloud_to_laserscan` to compress the robot's 3D depth camera (`/xtion/depth_registered`) into a virtual floor-level laser, which was then merged with `/scan_raw` using `laserscan_multi_merger`. This produced a highly robust occupancy grid.

### 2. Aggressive Costmap Tuning & Dynamic Avoidance
Navigating the tightly constrained corridors of the custom Gazebo warehouse caused the default `move_base` planner to freeze. We aggressively tuned the TEB local planner and reduced TIAGo's obstacle clearances to `0.25m`. The fused RGB-D scan was fed directly into the `local_costmap`, allowing the robot to calculate live trajectory deviations around unmapped boxes dropped dynamically into its path.

### 3. Actionlib-based Operator UI
A custom Python Tkinter graphical interface (`operator_panel.py`) was developed to dispatch `MoveBaseGoal` commands. Instead of simple point-to-point dispatching, the UI implements **Intelligent Intercept Routing**—forcing the robot to cleanly reverse out of narrow shelf aisles to predefined "Exit Waypoints" before attempting to traverse the main warehouse, entirely preventing shelf collisions.

### 4. Computer Vision Task Execution
At every major waypoint, the robot halts and enters a verification loop. A custom ROS node (`qr_scanner_node.py`) processes the `/xtion/rgb/image_raw` feed via `cv_bridge` (bgr8 encoding) and decodes 1-meter custom QR boards using `pyzbar`. The mission only proceeds if the physical location string matches the expected destination.

---

## 🚀 How to Launch

**DO NOT launch the standard TIAGo files manually.** We have provided an automated bash wrapper that handles Costmap parameter injection, XML bug stripping, and topic relays.

```bash
cd ~/Documents/TTTC2343-Autonomous-Warehouse-Robot-Group-11--main
./.agents/run_autonomous_navigation.sh
```

### What the launch script does:
1. **Kills old ROS nodes:** Ensures `gzserver` and rogue python scripts are dead so they don't port-block the new launch.
2. **Injects Costmap Fixes:** Loads our custom parameters to support narrow-aisle navigation.
3. **Syncs the World:** Copies the latest `danish_inventory_delivery_warehouse.world` into the local Gazebo cache.
4. **Launches the Environment:** Opens 6 organized terminal tabs running Gazebo, RViz, 3D Station Markers, the QR Scanner Node, the Camera Feed, and the Operator Panel.

---

## 📁 Repository Structure
- `/src/warehouse_robot_danish`: The main ROS package containing all custom Python nodes, launch scripts, and models.
- `/maps`: The finalized `.pgm` and `.yaml` occupancy grids used by AMCL.
- `/models`: Custom 1-meter QR stand meshes designed specifically for TIAGo's camera height.
- `/docs`: Final PDF and DOCX reports detailing our methodology and architecture.
- `/report_screenshots`: Evidence of `rqt_graph` topologies and RViz costmap behavior.

---
*Developed for TTTC2343 Final Project.*
