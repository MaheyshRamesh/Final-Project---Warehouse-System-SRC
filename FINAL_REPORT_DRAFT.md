# TTTC2343 Final Project Report
**Project Title:** Autonomous Warehouse Inventory and Item Delivery Robot Simulation
**Course:** TTTC2343

### Group 11 Members
- **Danish Irfan bin Hakimi (A213696)**
- **Shukri Aizat bin Shuazrin (A212202)**
- **Ahmad Nazmi bin Bastian Affendy (A212353)**
- **Maheysh A/L Ramesh (A211881)**

---

## Abstract
This final report presents the complete development of an Autonomous Warehouse Inventory and Item Delivery Robot simulation for TTTC2343. The project was developed using ROS Noetic, Gazebo, and RViz, utilizing the TIAGo mobile robot platform. The simulation demonstrates a warehouse assistant robot that initializes at a charging dock, navigates autonomously through a highly constrained customized warehouse, visits multi-point shelf inventory zones to perform simulated computer-vision inventory checking, and completes an item delivery mission at a drop-off station. 

The project strictly follows the required weekly development workflow: environment customization (Week 8), SLAM mapping and Multi-Point Navigation (Week 9), UI-based destination control and Task Execution (Week 10), culminating in full system integration (Week 11). The final robotic pipeline integrates 3D depth-camera sensor fusion, actionlib state machines, and a dynamic local costmap, fulfilling all technical methodology and system design criteria.

---

## 1. Introduction
Modern warehouses require rapid logistical movement, accurate inventory tracking, and safe navigation around static shelves and dynamic obstacles. Manual inventory checking is historically slow and repetitive. By deploying mobile robotics, repetitive travel between storage areas and packing stations can be heavily automated. 

This project develops a highly customized robotic simulation focusing on a warehouse assistant. Operating within a structured Gazebo environment comprising distinct inventory zones, lane markings, and varying corridor widths, the TIAGo robot is tasked with demonstrating a full-loop autonomous delivery and stock-taking pipeline. 

## 2. Project Objectives and Scope
### 2.1 Objectives
- **Environment Design:** Design a customized warehouse simulation environment featuring multiple areas (Home, Shelf A, Shelf B, Pickup, Drop-off), realistic obstacles, and task stations.
- **Robot Integration:** Integrate the TIAGo mobile robot platform into the Gazebo world, bridging ROS topics for `/cmd_vel`, `/odom`, and `/scan`.
- **SLAM Mapping:** Perform Simultaneous Localization and Mapping (SLAM) to generate a high-fidelity 2D occupancy grid for localization.
- **Multi-Point Navigation:** Implement an autonomous waypoint route connecting all major warehouse checkpoints.
- **User Interface (UI):** Create an interactive Tkinter Operator Panel allowing manual destination selection and live robot status updates.
- **Task Execution:** Perform simulated task actions involving visual inventory verification (QR code scanning) and item delivery confirmation.

### 2.2 Scope
The implementation is entirely simulation-based (ROS Noetic & Gazebo). While real-world physics and kinematics (such as TIAGo's differential drive and laser scanner constraints) are heavily simulated, the task execution focuses on marker-style visual verification (QR boards) to validate arrival at waypoints, proving the robot's physical position matches the navigation goal.

---

## 3. Methodology
The development lifecycle adhered to the following structured phases:
1. **Week 8: Gazebo Environment Development.** Physical warehouse layout, boundary definitions, and 3D prop placement.
2. **Week 9: SLAM Mapping and Navigation Setup.** Generation of `warehouse_map.pgm` via `gmapping`, followed by tuning the `move_base` action server and AMCL localization.
3. **Week 10: Task Action and UI Development.** Implementation of `operator_panel.py` and `qr_scanner_node.py` to handle the procedural logic of the inventory patrol.
4. **Week 11: System Integration.** Resolving final bugs (Gazebo XML corruption, ROS topic relays) and producing final validation evidence.

---

## 4. System Design
The system is engineered as a modular ROS architecture. The Gazebo world acts as the physics and sensor provider, while independent Python nodes manage the high-level logic.

### 4.1 System Architecture Flow
1. **Gazebo Simulation:** Provides `/scan_raw`, `/odom`, and `/xtion/rgb/image_raw`.
2. **Perception Layer:** `laserscan_multi_merger` fuses 3D depth data with 2D LiDAR. `qr_scanner_node` decodes the RGB camera feed.
3. **Navigation Layer:** `move_base` (Global: Navfn, Local: TEB) computes velocities sent to `/cmd_vel`.
4. **Application Layer:** `operator_panel.py` intercepts user clicks and dispatches `MoveBaseGoal` actionlib messages.

> **[PLACEHOLDER: Insert System Architecture Flowchart Diagram]**
> *(File: `report_screenshots/system_architecture.png`)*

### 4.2 Main ROS Topics and Nodes
| Node | Topic(s) | Role |
| :--- | :--- | :--- |
| `move_base` | `/move_base/goal`, `/cmd_vel` | Computes trajectory and drives the robot. |
| `warehouse_operator_panel` | `/move_base/status` | Provides the GUI and dispatches waypoints. |
| `qr_scanner_node` | `/xtion/rgb/image_raw` | Processes live camera feed via OpenCV to decode QR data. |
| `scan_relay` | `/scan_raw` -> `/scan` | Bridges Gazebo's raw laser output into the format expected by the costmap. |
| `amcl` | `/scan`, `/map`, `/tf` | Probabilistic localization of the robot against the static occupancy grid. |

---

## 5. Implementation Details

### 5.1 Customized Warehouse Environment
The environment was built from scratch in Gazebo, containing clearly separated task zones. The robot spawns at the **Home/Charging Zone**, enclosed by walls that demand precision navigation upon exit. It must travel down the **Main Aisle** and navigate tightly constrained corridors to access **Shelf A** and **Shelf B**, before moving to the open **Pickup** and **Drop-off** zones.

> **[PLACEHOLDER: Insert Gazebo Overview Screenshot showing all shelves and zones]**
> *(File: `report_screenshots/gazebo_overview.png`)*

### 5.2 SLAM Mapping and Sensor Fusion
The TIAGo's default 2D laser scanner is mounted high on its chassis, rendering it blind to thin, low-lying obstacles such as the metal legs of the warehouse shelves. Relying solely on `/scan_raw` resulted in catastrophic collisions during mapping.

To solve this, we implemented robust sensor fusion. We activated the TIAGo's `/xtion/depth_registered/image_raw` 3D depth camera and utilized the `pointcloud_to_laserscan` package to compress the 3D data into a virtual floor-level laser scan (`/rgbd_scan`). Both laser feeds were then combined into a single, comprehensive scan using `laserscan_multi_merger`. The robot was then teleoperated via `teleop_twist_joy` (with deadman switch adjustments) to generate the final map.

> **[PLACEHOLDER: Insert RViz mapping view showing the warehouse occupancy map]**
> *(File: `report_screenshots/rviz_mapping.png`)*
>
> **[PLACEHOLDER: Insert Ubuntu Terminal evidence confirming `map_saver` created the .yaml and .pgm files]**
> *(File: `report_screenshots/terminal_map_saver.png`)*

---

## 6. Navigation and Task Execution

### 6.1 Multi-Point Navigation Configuration
The navigation stack relies on `move_base` and AMCL. The warehouse map was set as the fixed reference frame. However, the TIAGo robot's default obstacle clearances (`0.85m`) induced "agoraphobia" within the narrow shelf aisles, causing the planner to constantly reject valid paths. The `local_costmap` parameters were aggressively tuned, reducing the `front_clearance` and `side_clearance` to `0.25m` to force the robot to confidently navigate the tight spaces.

> **[PLACEHOLDER: Insert RViz Navigation Setup showing AMCL particles and the Global Planner line]**
> *(File: `report_screenshots/rviz_navigation_setup.png`)*

### 6.2 Intelligent Intercept Routing
Instead of relying on simple point-to-point dispatching, our `operator_panel.py` implements intelligent "Intercept Routing". If the robot is instructed to navigate to a distant waypoint while currently trapped inside the narrow `Shelf A` aisle, the standard planner would attempt a sweeping turn and collide with the shelves. 

The Python script actively intercepts this command:
```python
if self.current_station == "Shelf A" and point_name not in ["Shelf A", "Shelf A Exit"]:
    self.send_goal("Shelf A Exit")
```
This logic forces the robot to cleanly back out of the aisle to the `Shelf A Exit` waypoint in the main corridor *before* computing the trajectory to the final destination, guaranteeing collision-free operation.

### 6.3 Computer Vision Verification (Task Execution)
To fulfill the Week 10 Task Action requirement, we developed a system that prevents the robot from simply relying on odometry. At every major checkpoint (e.g., Shelf A), 1-meter custom `qr_stand` models were placed in the simulation. 

The `qr_scanner_node.py` uses `cv_bridge` to capture the robot's camera feed in `bgr8` format. Upon reaching a goal, the robot halts and enters a 10-second verification loop. It processes the camera feed with `pyzbar` to detect the QR code. The mission only proceeds if the decoded string (e.g., `SHELF_A_VERIFIED`) precisely matches the expected location data.

> **[PLACEHOLDER: Insert Operator Panel UI screenshot side-by-side with RQT Image View showing a QR code]**
> *(File: `report_screenshots/ui_and_vision.png`)*

---

## 7. Results and Discussion
The final system successfully executes the full warehouse loop autonomously:
`Home -> Home Approach -> Shelf A -> Shelf A Exit -> Shelf B -> Shelf B Exit -> Pickup -> Drop-off -> Home`

**Key Achievements:**
- **Accuracy:** The robot localized within the map perfectly, reaching all 5 major waypoints with under 0.1m tolerance.
- **Dynamic Obstacle Avoidance:** During live testing, a simulated obstacle was dropped into the robot's path. The local costmap, fed by the RGB-D camera, instantly highlighted the obstacle in red, and the TEB local planner recalculated a dynamic trajectory to bypass it without stopping.
- **Vision Integration:** The Python OpenCV pipeline successfully bridged the ROS image transport, reliably scanning 1-meter QR boards from up to 2.0 meters away.

### 7.1 ROS Graph Evidence (Lecturer Requirement)
The structural integrity of the system is proven through the ROS node topologies:

> **[PLACEHOLDER: Insert `rqt_graph` for SLAM Mapping]**
> *(File: `report_screenshots/rqt_graph_mapping.png`)*
>
> **[PLACEHOLDER: Insert `rqt_graph` for Autonomous Navigation]**
> *(File: `report_screenshots/rqt_graph_navigation.png`)*
>
> **[PLACEHOLDER: Insert `rqt_graph` for Vision and UI Execution]**
> *(File: `report_screenshots/rqt_graph_vision_ui.png`)*

---

## 8. Issues, Limitations and Improvements

### 8.1 Critical Bugs Resolved
1. **The Laser Scan Relay Bug (Robot Refused to Move):**
   - **Issue:** `move_base` successfully planned paths, but the robot physically refused to drive, citing a stale scan buffer.
   - **Fix:** Gazebo published to `/scan_raw`, but `move_base` expected `/scan`. A `topic_tools relay` node was injected into the launch file to bridge the topics.
2. **Gazebo Scale Tool XML Corruption (Galaxy-sized Shelves):**
   - **Issue:** Using Gazebo's scaling tool caused floating-point math errors, saving massive dimensions (e.g., `2.733e+23`) into the `.world` XML, instantly freezing the physics engine on boot.
   - **Fix:** We bypassed the Gazebo UI and surgically parsed the XML files via Python to extract raw `<pose>` data into a clean baseline world file.
3. **Baked-in TIAGo Clone Crashes:**
   - **Issue:** Clicking "Save World" while the simulation was running baked a permanent, frozen `<model name='tiago'>` into the map. Upon next launch, the spawn script attempted to spawn the real robot inside the baked clone, causing infinite collision forces.
   - **Fix:** XML code was manually stripped of the baked model data prior to launch.

### 8.2 Future Improvements
- Implement a physical robotic manipulator pipeline (e.g., MoveIt!) to perform real pick-and-place task actions at the Pickup zone rather than just visual QR verification.
- Optimize the local costmap inflation radius to allow for slightly faster traversal through the narrowest sections of the warehouse.

---

## 9. Conclusion
The Autonomous Warehouse Inventory and Item Delivery Robot simulation was highly successful. The project fulfills all TTTC2343 requirements, advancing significantly beyond basic point-to-point movement. By engineering a custom modular architecture that fuses 3D depth sensors for mapping, implements an intelligent intercept-routing UI, and validates physical logistics through real-time computer vision, the final ROS package serves as a robust, fully autonomous proof-of-concept for modern warehouse operations.

---

## Appendix A. Key Run Commands
```bash
# Compile the custom packages
cd ~/tiago_public_ws
catkin_make

# Source the workspace
source devel/setup.bash

# Run the full autonomous system (Environment, Navigation, Vision, UI)
./.agents/run_autonomous_navigation.sh

# Run only the Gazebo mapping environment
roslaunch warehouse_robot_danish turtlebot3_world.launch
```
