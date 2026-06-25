# Phase 3: QR Code Checkpoint Verification System

Integrate OpenCV-based QR code scanning into the existing autonomous warehouse navigation system. Each of the 5 main checkpoints (Home, Shelf A, Shelf B, Pickup, Drop-off) will have a physical QR code board in the Gazebo world. The robot must scan and verify the QR code at each station before advancing to the next waypoint, serving as a mandatory checkpoint verification mechanism.

## Design Decisions (Confirmed)

| Decision | Choice |
|----------|--------|
| Marker type | Standard QR codes (Python `qrcode` lib + OpenCV `QRCodeDetector`) |
| Encoded data | Plain station names: `HOME_BASE`, `SHELF_A`, `SHELF_B`, `PICKUP_ZONE`, `DROPOFF_ZONE` |
| Mounting height | Z=1.1m (TIAGo eye-level), facing robot's approach direction |
| Architecture | Separate `qr_scanner_node.py` ROS node publishing to `/warehouse/qr_detection` |
| UI feedback | Persistent "QR Status" label: `Scanning...` → `QR Match! [NAME]` → `Arrived at [NAME] ✔` |
| RViz feedback | Annotated image (green bounding box + decoded text) published to `/warehouse/qr_image` only when QR is actively detected |
| Functional purpose | Mandatory checkpoint verification — mission won't advance until QR match confirms correct location |
| QR placement | Replace 2 existing placeholder boards + add 3 new boards at remaining stations |
| Board orientation | Auto-calculated from waypoint yaw angles to face the robot's approach direction |

---

## Proposed Changes

### Component 1: QR Code Image Generation

#### [NEW] `scripts/generate_qr_codes.py`

A one-off utility script that generates 5 QR code PNG images using Python's `qrcode` library. Each image encodes a station name string. Output files:

| File | Encoded Data |
|------|-------------|
| `models/qr_home/materials/textures/qr_home.png` | `HOME_BASE` |
| `models/qr_shelf_a/materials/textures/qr_shelf_a.png` | `SHELF_A` |
| `models/qr_shelf_b/materials/textures/qr_shelf_b.png` | `SHELF_B` |
| `models/qr_pickup/materials/textures/qr_pickup.png` | `PICKUP_ZONE` |
| `models/qr_dropoff/materials/textures/qr_dropoff.png` | `DROPOFF_ZONE` |

Each PNG will be 300×300px with a white border for reliable detection.

---

### Component 2: Gazebo QR Board Models

#### [NEW] `models/qr_home/`, `models/qr_shelf_a/`, `models/qr_shelf_b/`, `models/qr_pickup/`, `models/qr_dropoff/`

Each directory contains a complete Gazebo model:
```
models/qr_<station>/
├── model.config          # Gazebo model metadata
├── model.sdf             # 0.5m × 0.5m flat board with QR texture
└── materials/
    ├── scripts/
    │   └── qr.material   # Ogre material definition
    └── textures/
        └── qr_<station>.png  # The actual QR code image
```

The `model.sdf` defines a thin static box (0.5m × 0.005m × 0.5m) with the QR texture applied to the front face. No collision geometry needed (these are visual-only boards).

> [!IMPORTANT]
> Gazebo resolves model URIs via the `GAZEBO_MODEL_PATH` environment variable. The launch script must export this path to include our `models/` directory, or we symlink the models into `~/.gazebo/models/`.

---

### Component 3: World File Updates

#### [MODIFY] [danish_inventory_delivery_warehouse.world](file:///home/maheysh/tiago_public_ws/src/warehouse_robot_danish/worlds/danish_inventory_delivery_warehouse.world)

**Remove:** The 2 existing placeholder `aruco_like_marker_shelf_A` and `aruco_like_marker_shelf_B` models (lines 304-336).

**Add:** 5 new QR board model `<include>` blocks. Board positions and orientations derived from waypoint coordinates in `operator_panel.py`:

| Station | QR Board Position | Board Yaw | Rationale |
|---------|------------------|-----------|-----------|
| Home | Near `(0.21, -0.83)`, offset ~1.5m in front | π (faces West→robot approaches facing East yaw=0) | Board placed on wall/obstacle ahead of Home pad |
| Shelf A | `(-4.00, 0.45, 1.10)` (existing position) | π/2 (faces North→robot approaches facing South yaw=-π/2) | Reuses existing marker location on shelf face |
| Shelf B | `(3.40, -1.45, 1.10)` (existing position) | -π/2 (faces South→robot approaches facing North yaw=π/2) | Reuses existing marker location on shelf face |
| Pickup | Near `(4.55, -10.62)`, offset ~1.5m in front | 0 (faces East→robot approaches facing West yaw=π) | Board placed on nearby wall |
| Drop-off | Near `(6.89, 6.44)`, offset ~1.5m in front | π (faces West→robot approaches facing East yaw=0) | Board placed on nearby structure |

> [!NOTE]
> Exact positions will be fine-tuned after spawning in Gazebo to ensure the QR is clearly visible in TIAGo's camera frame when the robot is parked at each waypoint.

---

### Component 4: QR Scanner ROS Node

#### [NEW] `scripts/qr_scanner_node.py`

A standalone ROS node that:

1. **Subscribes** to `/xtion/rgb/image_raw` (TIAGo's head-mounted RGB camera, `sensor_msgs/Image`)
2. Uses `cv_bridge` to convert ROS Image → OpenCV BGR frame
3. Runs `cv2.QRCodeDetector().detectAndDecode()` on every frame
4. **On detection:**
   - Publishes the decoded station name string to `/warehouse/qr_detection` (`std_msgs/String`)
   - Draws a green bounding box + decoded text overlay on the frame
   - Publishes the annotated frame to `/warehouse/qr_image` (`sensor_msgs/Image`)
5. **On no detection:**
   - Stops publishing to both topics (RViz image panel goes blank naturally)

**Rate limiting:** Process at ~5 Hz (skip frames) to avoid CPU overload from OpenCV on every 30fps camera frame.

**Dependencies:** `rospy`, `cv2`, `cv_bridge`, `sensor_msgs`, `std_msgs`

---

### Component 5: Operator Panel UI Updates

#### [MODIFY] [operator_panel.py](file:///home/maheysh/tiago_public_ws/src/warehouse_robot_danish/scripts/operator_panel.py)

**UI Changes:**
- Add a `self.qr_label` below the existing `self.status_label`
  - Default text: `"QR: Idle"`
  - During navigation: `"QR: Scanning..."` (yellow)
  - On QR match: `"QR Match! SHELF_A"` (bright green, bold)
  - On arrival confirmed: `"Arrived at SHELF_A ✔"` (green)
  - On timeout (no QR detected): `"QR: No code found ⚠"` (orange)

**ROS Subscriber:**
- Subscribe to `/warehouse/qr_detection` (`std_msgs/String`)
- Store the latest detected QR text in `self.last_qr_detected`
- Update the `qr_label` in real-time via Tkinter's `root.after()` thread-safe mechanism

**Mission Flow Changes (in `send_goal` or `run_full_mission`):**
- After `move_base` reports `SUCCEEDED` at a main checkpoint (Home, Shelf A, Shelf B, Pickup, Drop-off):
  1. Set QR label to `"QR: Scanning..."`
  2. Wait up to 10 seconds for `self.last_qr_detected` to match the expected station name
  3. If match found → set label to `"QR Match! [NAME]"`, pause 2 seconds, then set to `"Arrived at [NAME] ✔"` and proceed
  4. If timeout → set label to `"QR: No code found ⚠"` but still proceed (graceful degradation — don't block the entire mission over a scan failure)
- **Skip QR verification for transit waypoints** (Home Approach, Shelf A Exit, Shelf B Exit, Main Aisle) — these have no QR codes

**Mapping dictionary** added to the class:
```python
self.qr_expected = {
    "Home": "HOME_BASE",
    "Shelf A": "SHELF_A",
    "Shelf B": "SHELF_B",
    "Pickup": "PICKUP_ZONE",
    "Drop-off": "DROPOFF_ZONE"
}
```

---

### Component 6: Launch Script Updates

#### [MODIFY] [run_autonomous_navigation.sh](file:///home/maheysh/Documents/TTTC2343-Autonomous-Warehouse-Robot-Group-11--main/.agents/run_autonomous_navigation.sh)

- Add a new terminal tab: `"6. QR Scanner"` that launches `qr_scanner_node.py` with a 15-second sleep delay (same as station markers)
- Export `GAZEBO_MODEL_PATH` to include our custom `models/` directory before launching Gazebo

#### [MODIFY] [mapping.rviz](file:///home/maheysh/tiago_public_ws/src/warehouse_robot_danish/config/mapping.rviz) *(or instruct user manually)*

- Add an `Image` display subscribed to `/warehouse/qr_image` so the annotated QR snapshot appears in an RViz panel

---

## File Summary

| File | Status | Purpose |
|------|--------|---------|
| `scripts/generate_qr_codes.py` | NEW | One-off script to generate 5 QR PNG images |
| `models/qr_home/**` | NEW | Gazebo model with HOME_BASE QR texture |
| `models/qr_shelf_a/**` | NEW | Gazebo model with SHELF_A QR texture |
| `models/qr_shelf_b/**` | NEW | Gazebo model with SHELF_B QR texture |
| `models/qr_pickup/**` | NEW | Gazebo model with PICKUP_ZONE QR texture |
| `models/qr_dropoff/**` | NEW | Gazebo model with DROPOFF_ZONE QR texture |
| `worlds/danish_inventory_delivery_warehouse.world` | MODIFY | Remove 2 placeholder markers, add 5 QR board includes |
| `scripts/qr_scanner_node.py` | NEW | ROS node: camera → OpenCV QR detect → publish to topics |
| `scripts/operator_panel.py` | MODIFY | Add QR status label, subscriber, checkpoint verification logic |
| `.agents/run_autonomous_navigation.sh` | MODIFY | Add QR scanner tab, export model path |
| `config/mapping.rviz` | MODIFY | Add Image display for `/warehouse/qr_image` |

---

## Verification Plan

### Automated Tests
```bash
# 1. Verify QR images were generated and are scannable
python3 -c "import cv2; det=cv2.QRCodeDetector(); img=cv2.imread('models/qr_shelf_a/materials/textures/qr_shelf_a.png'); data,_,_=det.detectAndDecode(img); print(data)"
# Expected output: SHELF_A

# 2. Verify QR scanner node is publishing
rostopic echo -n 1 /warehouse/qr_detection
rostopic hz /warehouse/qr_image
```

### Manual Verification
1. Launch the full environment with `run_autonomous_navigation.sh`
2. Set 2D Pose Estimate in RViz
3. Add Image display in RViz → subscribe to `/warehouse/qr_image`
4. Click **"Start Full Autonomous Mission"** in the Operator Panel
5. **At each checkpoint, verify:**
   - The QR label in the UI transitions: `Scanning...` → `QR Match! [NAME]` → `Arrived at [NAME] ✔`
   - The RViz Image panel shows the annotated camera frame with green bounding box around the QR
   - The mission only advances after QR verification succeeds
6. Verify that transit waypoints (exits, approaches) are skipped for QR scanning
7. Confirm full autonomous mission completes end-to-end

---

## Open Questions

> [!IMPORTANT]
> **GAZEBO_MODEL_PATH Strategy:** Should we symlink the QR models into `~/.gazebo/models/` (simpler, works globally) or export the path in the launch script (self-contained in the project repo)? I recommend the launch script approach so everything is portable.

> [!NOTE]  
> **QR Board Size:** I've proposed 0.5m × 0.5m boards. These should be large enough for TIAGo's camera to reliably detect from ~1-2m away. If detection is unreliable during testing, we can scale up to 0.7m × 0.7m.

> [!NOTE]
> **Timeout Behavior:** I've proposed 10 seconds with graceful degradation (warn but proceed). Would you prefer the mission to hard-stop if a QR isn't found, or is the warning sufficient?
