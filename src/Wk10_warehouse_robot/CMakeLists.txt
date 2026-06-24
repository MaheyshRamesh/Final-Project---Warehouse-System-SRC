cmake_minimum_required(VERSION 3.0.2)
project(warehouse_robot)

find_package(catkin REQUIRED COMPONENTS
  rospy
  roscpp
  std_msgs
  geometry_msgs
  nav_msgs
  tf
  actionlib
  move_base_msgs
)

catkin_package()

include_directories(
  ${catkin_INCLUDE_DIRS}
)

catkin_install_python(PROGRAMS
  scripts/mission_controller.py
  scripts/inventory_checker.py
  scripts/delivery_runner.py
  scripts/zone_detector.py
  scripts/waypoint_mission.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

install(DIRECTORY launch worlds maps rviz docs
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
