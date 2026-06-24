# Walkthrough: Phase 2 - Autonomous Navigation & Task Execution

## Summary
Phase 2 is fully operational. TIAGo can now autonomously navigate the warehouse using calibrated waypoints, driven by an operator UI panel, with clear visual station labels in RViz.

---

## What Was Built

### 1. Navigation Launch (`tiago_navigation.launch`)
- Loads `warehouse_map.yaml` via `map_server`.
- Starts AMCL localization.
- **Relays `/scan_raw` → `/scan`** via `topic_tools relay` so `move_base`'s costmap receives live laser data.
- Launches `move_base` with the TEB local planner.

### 2. Station Markers (`station_markers.py`)
- Publishes giant, color-coded `TEXT_VIEW_FACING` 3D text markers floating above every station in RViz.
- Directly addresses lecturer feedback about station clarity.
- Colors: Green (Home), Light Blue (Shelf A), Dark Blue (Shelf B), Orange (Pickup), Red (Drop-off).

### 3. Operator Panel UI (`operator_panel.py`)
- Tkinter GUI with individual station buttons + a full autonomous mission button.
- Implements `wait_for_server()` to block until `move_base` is confirmed online.
- Uses calibrated waypoints extracted via RViz 2D Nav Goal:
  - Home: `(1.31, -2.23, 0.0)`
  - Shelf A: `(8.75, -2.20, 0.0)`
  - Shelf B: `(8.75, -7.31, 0.0)`
  - Pickup: `(2.00, -9.16, 0.0)`
  - Drop-off: `(7.08, 5.49, -1.626)`

### 4. Launch Script (`run_autonomous_navigation.sh`)
- One-click script that opens 5 terminal tabs in correct order with proper sleep delays.
- Forces user to complete 2D Pose Estimate before the UI launches.

---

## Critical Bugs Fixed

### Bug 1: AMCL Instacrash (Missing `pose.yaml`)
- **Symptom:** RViz completely blank, grey grid, no map.
- **Cause:** `~/.pal/pose.yaml` didn't exist.
- **Fix:** `mkdir -p ~/.pal && echo "{}" > ~/.pal/pose.yaml`

### Bug 2: Local Planner Not Found
- **Symptom:** `tiago_navigation.launch` fails immediately.
- **Cause:** Default `pal` planner doesn't exist in our workspace.
- **Fix:** Explicitly pass `<arg name="local_planner" value="teb"/>`.

### Bug 3: Robot Plans But Won't Move (The Scan Relay)
- **Symptom:** Green trajectory line visible in RViz, but wheels locked. Terminal spams `"The scan observation buffer has not been updated for X seconds"`.
- **Cause:** `move_base` subscribes to `/scan` (zero publishers). Gazebo publishes laser data on `/scan_raw`. Costmap gets no data → safety lock engages.
- **What Didn't Work:** `<remap from="scan" to="scan_raw"/>` inside `<include>` — silently ignored because costmap resolves topics via YAML params internally.
- **Fix:** Added `<node pkg="topic_tools" type="relay" name="scan_relay" args="scan_raw scan"/>` in `tiago_navigation.launch`.
- **Verification:** `rostopic info /scan` must show `scan_relay` as a Publisher.

---

## How to Run

```bash
cd ~/Documents/TTTC2343-Autonomous-Warehouse-Robot-Group-11--main/.agents
./run_autonomous_navigation.sh
```

1. Wait for Gazebo + RViz to load.
2. In RViz: **Add → By Topic → /warehouse/station_markers → MarkerArray → OK** (to see giant text).
3. Click **2D Pose Estimate**, click where TIAGo is, drag arrow to match facing direction.
4. Go to 5th terminal tab, press **ENTER**.
5. Click **Start Full Autonomous Mission** in the UI.
