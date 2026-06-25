# TIAGo Autonomous Warehouse: How to Launch

To ensure the TIAGo robot and all the environment variables load cleanly, **do not manually launch roslaunch commands**. 

Always use the provided autonomous navigation wrapper script:
```bash
cd ~/Documents/TTTC2343-Autonomous-Warehouse-Robot-Group-11--main
./.agents/run_autonomous_navigation.sh
```

### What this script does:
1. **Kills old ROS nodes:** Ensures `gzserver`, `rosmaster`, and rogue python scripts are dead so they don't port-block the new launch.
2. **Injects Costmap Fixes:** Automatically updates TIAGo's navigation config to support advanced obstacle avoidance.
3. **Syncs the World:** Copies your latest `danish_inventory_delivery_warehouse.world` into `~/.pal/pal_gazebo_worlds/` so that the TIAGo launch files can find it natively.
4. **Launches the Environment:** Opens 6 organized terminal tabs running:
   - Gazebo & Move Base
   - RViz (Mapping profile)
   - 3D Station Markers
   - QR Code Scanner Node
   - RQT Image View (for live camera feed)
   - The interactive Operator Panel UI

### Editing the World File in Gazebo
If you open Gazebo, drag objects around, and click **Save World**, be warned:
- **DO NOT** save the world while the TIAGo robot is spawned inside it! Gazebo will bake the robot directly into the map code, causing fatal physics crashes on your next launch.
- **DO NOT** use the Scale tool (box icon) to stretch objects. It often causes floating point bugs (e.g. `2.733e+23` size values) that destroy the map. Use the Translate tool (crosshairs) only. 

*(If you accidentally break your world, see `.agents/AGENTS.md` for instructions on how to strip out the corrupted data!)*
