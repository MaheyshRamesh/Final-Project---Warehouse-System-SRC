cmake_minimum_required(VERSION 3.0.2)
project(warehouse_robot_danish)

find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  geometry_msgs
  sensor_msgs
)

catkin_package()

catkin_install_python(PROGRAMS
  scripts/mission_controller.py
  scripts/inventory_status_publisher.py
  scripts/operator_panel.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

install(DIRECTORY launch worlds rviz maps docs
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
