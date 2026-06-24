# TIAGo Autonomous Warehouse Rules & Documentation

This file serves as the definitive reference for "what went right" and all the "gotchas" discovered during implementation. Any future agent or session MUST read and adhere to these findings.

## Phase 1: SLAM Mapping - Successes & Gotchas
1. **Obstacle Clearances (The "Agoraphobia" Bug):** TIAGo's default obstacle clearances (0.85m) were far too conservative for narrow warehouse aisles, causing the robot to freeze constantly. **Fix:** Aggressively reduced `front_clearance` and `side_clearance` to `0.25m`.
2. **LiDAR Blind Spots:** The TIAGo's 2D LiDAR is mounted high and completely misses the thin metal legs of the warehouse shelves. **Fix:** Successfully fused the 3D depth camera (`/xtion/depth_registered/image_raw`) to detect low-lying obstacles.
3. **Map-Aware Exploration:** Relying purely on blind random-walk logic caused the robot to get stuck bouncing in corners. **Fix:** Implemented a TF listener evaluating `-1` (unexplored) cells in the `OccupancyGrid` to intelligently steer toward unmapped areas.
4. **Manual Controller Teleop Setup:** 
   - *Gotcha:* The standard `teleop_twist_joy` publishes to `/cmd_vel` which TIAGo's `twist_mux` ignores. 
   - *Fix:* Must run with `cmd_vel:=joy_vel`.
   - *Gotcha:* Deadman switch mapping varies. 
   - *Fix:* Explicitly set `_enable_button:=0` (which is the Cross/X button on DS5). 
   - *Note:* The `[WARN] Couldn't set gain on joystick force feedback: Bad file descriptor` error is completely harmless.
5. **Map Saving:** The `map_saver` outputs a `.yaml` and a `.pgm` file. These two files are entirely codependent and must always be kept together in the same directory (`~/tiago_public_ws/src/warehouse_robot_danish/maps/`).

## Phase 2: Autonomous Navigation - Initialization Rules
When transitioning from the mapping phase to the autonomous task phase using `warehouse_map.yaml`, the agent MUST follow these setup steps:
1. Load the map via the navigation launch file (`tiago_navigation.launch`).
2. In RViz, click **2D Pose Estimate**.
3. Set the robot's exact position inside the warehouse.
4. Ensure the green arrow precisely matches the robot's physical facing direction.
*CRITICAL:* Only after the pose estimate perfectly matches the robot's physical location and orientation should you launch any autonomous task scripts or UI.

## Phase 2: Actionlib & UI Integration Gotchas
1. **The `move_base` Timeout Bug:** Past tests showed that scripts/UIs often fail silently because they attempt to send goals before `move_base` is fully initialized.
   - *Fix:* Any navigation Python script (like `operator_panel.py`) MUST implement `self.client.wait_for_server()` to block execution until the action server is confirmed online.
2. **Waypoint Calibration:** Hardcoded coordinates will fail. We must use RViz's "Publish Point" or "2D Nav Goal" feedback to extract the exact `(x, y, yaw)` coordinates for Home, Shelf A, Shelf B, Pickup, and Drop-off based entirely on the newly saved `warehouse_map.yaml`.
3. **Station Clarity:** To satisfy lecturer feedback regarding unclear stations, the system MUST run `station_markers.py` to overlay giant, color-coded `TEXT_VIEW_FACING` markers on RViz for all key locations.

## Phase 2: Launch Crash Gotchas (The Missing `pose.yaml`)
1. **AMCL Instacrash:** The standard TIAGo `localization.launch` (AMCL) hard-requires the file `~/.pal/pose.yaml` to exist. If it doesn't, `map_server` and `amcl` crash immediately on launch, leaving RViz completely blank (grey grid). 
   - *Fix:* Run `mkdir -p ~/.pal && echo "{}" > ~/.pal/pose.yaml`. This was applied and fixes the issue permanently.
2. **Local Planner Argument:** The `move_base.launch` defaults to `pal` local planner which does not exist in our workspace. 
   - *Fix:* Must explicitly pass `<arg name="local_planner" value="teb"/>` inside `tiago_navigation.launch`.
3. **RViz Config:** Always stick to using `mapping.rviz` (which we know works) instead of `navigation.rviz`. Remember to manually add the `MarkerArray` display for `/warehouse/station_markers` to see the giant 3D text!

## Phase 2: The Laser Scan Relay Gotcha (Robot Won't Move)
**Symptom:** `move_base` plans a trajectory (green line visible in RViz) but the robot physically refuses to drive. The terminal spams: `"The scan observation buffer has not been updated for X seconds"`.

**Root Cause:** TIAGo's Gazebo simulation publishes laser data on `/scan_raw`, but `move_base`'s costmap expects it on `/scan`. With zero laser data, the costmap considers the robot "blind" and activates an emergency safety lock on the wheels.

**What Didn't Work:** Using `<remap from="scan" to="scan_raw"/>` inside the `<include>` tag of `tiago_navigation.launch`. The costmap resolves its observation source topic internally via YAML parameters, so the `<include>`-level remap is silently ignored.

**The Fix That Works:** Add a `topic_tools relay` node in `tiago_navigation.launch` to republish `/scan_raw` onto `/scan`:
```xml
<node pkg="topic_tools" type="relay" name="scan_relay" args="scan_raw scan"/>
```
This bridges the two topics so `move_base` receives the laser data it needs. After this fix, the robot drives immediately.

**How to Verify:** Run `rostopic info /scan` — it must show `scan_relay` as a Publisher. If Publishers shows `None`, the relay is missing and the robot will not move.
