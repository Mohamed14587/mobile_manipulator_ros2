cmake_minimum_required(VERSION 3.8)
project(assem1_controller)

find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)

# launch files
install(
  DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

# config files
install(
  DIRECTORY config
  DESTINATION share/${PROJECT_NAME}
)

# python executable
install(PROGRAMS
  assem1_controller/slider_controller.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()