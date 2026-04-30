import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from moveit_configs_utils import MoveItConfigsBuilder

def generate_launch_description():
    # 1. بناء الإعدادات من الملفات الموجودة فعلياً
    moveit_config = (
        MoveItConfigsBuilder("assem", package_name="assem_moveit")
        .robot_description(file_path="config/assem.ros2_control.xacro")
        .robot_description_semantic(file_path="config/assem.srdf")
        .trajectory_execution(file_path="config/moveit_controllers.yaml")
        .planning_pipelines(pipelines=["ompl"]) # عشان نسرع التشغيل
        .to_moveit_configs()
    )

    # 2. تشغيل الـ Move Group
    move_group_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory("assem_moveit"), "launch", "move_group.launch.py")
        ),
    )

    # 3. تشغيل الـ RViz باستخدام الملف اللي في مجلد rviz/
    rviz_base = os.path.join(get_package_share_directory("assem_moveit"), "rviz", "moveit.rviz")
    # ملاحظة: سنستخدم moveit.launch.py لو هو اللي بيفتح RViz عندك
    moveit_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory("assem_moveit"), "launch", "moveit.launch.py")
        ),
    )

    return LaunchDescription([
        move_group_launch,
        moveit_launch,
    ])