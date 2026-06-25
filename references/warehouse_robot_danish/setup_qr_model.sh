#!/bin/bash

mkdir -p ~/.gazebo/models
cp -r ~/catkin_ws/src/warehouse_robot_danish/models/qr_shelf_a ~/.gazebo/models/

echo "QR Shelf A model copied to ~/.gazebo/models"
