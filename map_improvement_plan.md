# Map Improvement Plan: Depth Camera Fusion for Complete Warehouse Coverage

## Problem Statement
The current SLAM-generated map (`warehouse_map.pgm`) was built using only TIAGo's 2D LiDAR (`/scan_raw`), which is mounted at chest height (~0.75m). This creates two critical failures:

1. **Incomplete Static Map:** Shelf legs, low boxes, pallets, and any obstacle below the scan line are invisible to the LiDAR. The saved map has blank space where shelves physically exist, causing `move_base` to plan paths straight through solid objects.
2. **No Live Low-Obstacle Detection:** During autonomous navigation, the local costmap only uses `/scan` (2D LiDAR). When the robot encounters an unmapped low obstacle, it has zero sensor data to detect it, so it drives into it and gets stuck instead of reversing and re-routing.

---

## Solution Overview

### Part A: Re-Map with Depth Camera Fusion (Better Static Map)
Convert TIAGo's Xtion depth camera pointcloud into a virtual floor-level laser scan using `pointcloud_to_laserscan`. Feed this merged scan into `gmapping` during a fresh teleop mapping run. The result is a `.pgm` map that includes ALL obstacles from floor to ceiling.

### Part B: Add Depth Camera to Navigation Costmap (Live Obstacle Avoidance)
Add the depth-camera-derived scan as a **second observation source** in `move_base`'s local and global costmaps. This gives the robot real-time vision of low obstacles during autonomous missions, enabling proper reverse-and-reroute behavior.

---

## Part A: Re-Mapping (Depth Camera Fusion)

### Step 1: Create `tiago_mapping_depth.launch`

This launch file will:
1. Start `pointcloud_to_laserscan` to convert `/xtion/depth_registered/points` → `/rgbd_scan`
2. Start a `laser_multi_merger` (from `ira_laser_tools`) or a simple `topic_tools relay` to merge `/scan_raw` + `/rgbd_scan` → `/scan_merged`
3. Feed `/scan_merged` into `gmapping`

**Simpler alternative (if `ira_laser_tools` is unavailable):**
Use `depthimage_to_laserscan` (already installed at `/opt/ros/noetic/share/depthimage_to_laserscan`) which converts the depth image directly to a virtual laser scan. Then configure `gmapping` to use the depth-derived scan only, since it already covers everything the chest-height LiDAR sees plus everything below it.

#### `pointcloud_to_laserscan` Parameters (Tuned for TIAGo)
```yaml
# Floor-level virtual scan from depth camera
min_height: 0.05        # 5cm above ground (ignore floor noise)
max_height: 1.5         # capture everything up to 1.5m
angle_min: -1.047       # -60 degrees (depth camera FOV)
angle_max: 1.047        # +60 degrees
angle_increment: 0.005  # ~0.3 degree resolution
scan_time: 0.1          # 10Hz
range_min: 0.3          # min depth camera range
range_max: 5.0          # max useful depth range
target_frame: base_footprint
use_inf: true
```

> [!IMPORTANT]
> The depth camera has a narrower FOV (~120°) compared to the LiDAR (360°). This means the depth-only scan won't see behind the robot. For mapping, this is fine since the robot faces forward while driving. For navigation (Part B), we keep both sensors active.

#### `depthimage_to_laserscan` Alternative Parameters
```yaml
scan_height: 100        # Use 100 rows from the depth image center
scan_time: 0.033        # 30Hz
range_min: 0.3
range_max: 5.0
output_frame_id: base_footprint
```

### Step 2: Teleop Re-Mapping Session
1. Launch Gazebo with `tiago_spawn.launch`
2. Launch `tiago_mapping_depth.launch` (new)
3. Launch RViz with `mapping.rviz`
4. Use the DS5 controller to manually drive through every aisle
5. Save the new map: `rosrun map_server map_saver -f warehouse_map`
6. Copy both `.pgm` and `.yaml` to `maps/` directory

### Step 3: Verify Map Quality
- Open the new `.pgm` in an image viewer
- Confirm shelf legs and low obstacles appear as black pixels
- Compare side-by-side with the old map to see the improvement

---

## Part B: Live Obstacle Avoidance (Navigation Costmap Upgrade)

### Step 4: Create Custom Costmap Override Config

Create `config/depth_costmap_params.yaml`:
```yaml
# Add depth camera as second observation source for local costmap
local_costmap:
  obstacle_laser_layer:
    observation_sources: base_scan rgbd_scan
    
    base_scan:
      sensor_frame: base_laser_link
      data_type: LaserScan
      topic: scan
      expected_update_rate: 0.3
      observation_persistence: 0.0
      inf_is_valid: true
      marking: true
      clearing: true
      raytrace_range: 4.0
      obstacle_range: 3.0

    rgbd_scan:
      sensor_frame: base_footprint
      data_type: LaserScan
      topic: rgbd_scan
      expected_update_rate: 0.5
      observation_persistence: 0.5
      inf_is_valid: true
      marking: true
      clearing: false
      raytrace_range: 4.5
      obstacle_range: 3.5

# Same for global costmap
global_costmap:
  obstacle_laser_layer:
    observation_sources: base_scan rgbd_scan
    
    base_scan:
      sensor_frame: base_laser_link
      data_type: LaserScan
      topic: scan
      expected_update_rate: 0.3
      observation_persistence: 0.0
      inf_is_valid: true
      marking: true
      clearing: true
      raytrace_range: 4.0
      obstacle_range: 3.0

    rgbd_scan:
      sensor_frame: base_footprint
      data_type: LaserScan
      topic: rgbd_scan
      expected_update_rate: 0.5
      observation_persistence: 0.5
      inf_is_valid: true
      marking: true
      clearing: false
      raytrace_range: 4.5
      obstacle_range: 3.5
```

> [!NOTE]
> `clearing: false` on `rgbd_scan` prevents the narrow-FOV depth camera from erasing valid LiDAR obstacles outside its field of view. `observation_persistence: 0.5` keeps depth detections alive briefly even if the camera looks away.

### Step 5: Update `tiago_navigation.launch`

Add the `pointcloud_to_laserscan` node and load the custom costmap override:
```xml
<!-- Convert depth camera to virtual floor-level laser scan -->
<node pkg="pointcloud_to_laserscan" type="pointcloud_to_laserscan_node" name="depth_to_scan">
  <remap from="cloud_in" to="/xtion/depth_registered/points"/>
  <remap from="scan" to="rgbd_scan"/>
  <rosparam file="$(find warehouse_robot_danish)/config/depth_scan_params.yaml" command="load"/>
</node>

<!-- Override costmap to include depth camera -->
<rosparam file="$(find warehouse_robot_danish)/config/depth_costmap_params.yaml" command="load" ns="move_base"/>
```

---

## File List

| File | Status | Purpose |
|------|--------|---------|
| `launch/tiago_mapping_depth.launch` | NEW | SLAM mapping with depth camera fusion |
| `config/depth_scan_params.yaml` | NEW | `pointcloud_to_laserscan` parameters tuned for TIAGo |
| `config/depth_costmap_params.yaml` | NEW | Costmap override adding `rgbd_scan` as second observation source |
| `launch/tiago_navigation.launch` | MODIFY | Add depth-to-scan node + load costmap override |
| `maps/warehouse_map.pgm` | REPLACE | New map with shelf legs and low obstacles |
| `maps/warehouse_map.yaml` | REPLACE | Updated map metadata |

---

## Verification Plan

### After Re-Mapping (Part A)
- [ ] Open new `.pgm` — shelf legs visible as black pixels
- [ ] Overlay on Gazebo — obstacles align with physical world
- [ ] No large unexplored (grey) patches remaining

### After Costmap Upgrade (Part B)
- [ ] `rostopic hz /rgbd_scan` shows ~10Hz during navigation
- [ ] Place a box in an aisle in Gazebo → robot detects and re-routes around it
- [ ] No more "observation buffer not updated" warnings for the rgbd source
- [ ] Robot successfully completes full autonomous mission without getting stuck

---

## Rollback
If anything breaks, revert to the known-good state:
```bash
cd ~/Documents/TTTC2343-Autonomous-Warehouse-Robot-Group-11--main
git reset --hard ff8d153
```
