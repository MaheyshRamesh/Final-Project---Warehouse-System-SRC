# Implementation Plan: Phase 2 - Autonomous Navigation & Task Execution

## Goal Description
Transition from Phase 1 (SLAM Mapping) to Phase 2 (Autonomous Task Execution). We will utilize the previously developed `w9_multi_point_nav.py` and `w9_warehouse_ui.py` scripts as our foundation to drive TIAGo using `move_base`. 

To directly address the lecturer's feedback regarding unclear station locations, we will introduce a dedicated visualizer node that overlays giant, color-coded floating text in RViz over each key area. Furthermore, the plan incorporates strict startup sequencing and waypoint calibration to prevent the `move_base` action server timeout issues encountered in earlier tests.

---

## Tracking Tasklist (All Complete)

- `[x]` **1. Core Navigation & Launch Sequence**
  - `[x]` Verified `tiago_navigation.launch` defaults to `warehouse_map.yaml`.
  - `[x]` Created `run_autonomous_navigation.sh` that sequentially launches Gazebo, AMCL/Navigation, and RViz.
  - `[x]` Script mandates user performs 2D Pose Estimate before running UI.

- `[x]` **2. Waypoint Calibration (RViz Clicked Points)**
  - `[x]` Used `rostopic echo /move_base_simple/goal` + RViz 2D Nav Goal to extract exact coordinates:
    - Home: `(1.31, -2.23, 0.0)`
    - Shelf A: `(8.75, -2.20, 0.0)`
    - Shelf B: `(8.75, -7.31, 0.0)`
    - Pickup: `(2.00, -9.16, 0.0)`
    - Drop-off: `(7.08, 5.49, -1.626)`

- `[x]` **3. Addressing Lecturer Feedback (Clear Stations)**
  - `[x]` Created `station_markers.py` with giant, color-coded `TEXT_VIEW_FACING` markers.

- `[x]` **4. Refactoring the W9 UI and Nav Node**
  - `[x]` Integrated `w9_warehouse_ui.py` into `operator_panel.py`.
  - `[x]` Implemented `wait_for_server()` to block UI until `move_base` is ready.
  - `[x]` Updated waypoint dictionary with calibrated coordinates.

- `[x]` **5. Critical Bug Fix: Laser Scan Relay**
  - `[x]` Diagnosed that `move_base` subscribes to `/scan` but Gazebo publishes on `/scan_raw`.
  - `[x]` Confirmed `<remap>` inside `<include>` does NOT work for costmap observation sources.
  - `[x]` Added `topic_tools relay` node to bridge `/scan_raw` → `/scan` in `tiago_navigation.launch`.

---

## Resolved Gotchas (Critical)

| # | Gotcha | Symptom | Fix |
|---|--------|---------|-----|
| 1 | Missing `~/.pal/pose.yaml` | AMCL + map_server crash on launch, RViz blank | `mkdir -p ~/.pal && echo "{}" > ~/.pal/pose.yaml` |
| 2 | Wrong local planner default | `move_base.launch` fails: file not found for `pal` planner | Pass `<arg name="local_planner" value="teb"/>` |
| 3 | `/scan` vs `/scan_raw` mismatch | Robot plans trajectory but wheels won't move; costmap spams "observation buffer not updated" | Add `<node pkg="topic_tools" type="relay" name="scan_relay" args="scan_raw scan"/>` |
| 4 | `<remap>` inside `<include>` | Remap silently ignored; costmap resolves topics via YAML params internally | Use `topic_tools relay` instead of `<remap>` |

---

## Required File List & Purposes

### 1. `launch/tiago_navigation.launch`
* **Purpose**: Loads the `warehouse_map.yaml`, initializes AMCL localization, relays `/scan_raw` → `/scan`, and starts the `move_base` navigation stack with the TEB local planner.

### 2. `scripts/station_markers.py` (New)
* **Purpose**: Directly addresses the lecturer's feedback. It continuously publishes giant, floating 3D text labels over the map in RViz so anyone looking at the screen instantly knows exactly where Home, Shelves, and Drop-off stations are located.

### 3. `scripts/operator_panel.py` (Refactored from W9 UI)
* **Purpose**: A Tkinter-based control panel for the operator. It safely connects to the `move_base` action server (waiting indefinitely until it is ready) and provides buttons to trigger waypoint navigation or full missions based on calibrated coordinates.

### 4. `run_autonomous_navigation.sh` (New, in `.agents/`)
* **Purpose**: A launch script that guarantees the stack is started correctly. It opens tabs for Gazebo, the Nav Stack, the Station Markers, and pauses to instruct the user to do the `2D Pose Estimate` before finally launching the Operator Panel UI.

