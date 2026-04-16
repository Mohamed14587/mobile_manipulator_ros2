cmake_minimum_required(VERSION 3.8)
project(assem_controller)

find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)

install(
  DIRECTORY assem_controller
  DESTINATION lib/python3.10/site-packages
)

install(
  DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

install(
  DIRECTORY config
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  assem_controller/slider_controller.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()