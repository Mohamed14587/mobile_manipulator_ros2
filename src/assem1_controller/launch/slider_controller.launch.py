import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    # استدعاء ملف الـ controller.launch.py الخاص بـ assem1
    controller = IncludeLaunchDescription(
            os.path.join(
                get_package_share_directory("assem1_controller"),
                "launch",
                "controller.launch.py"
            ),
            launch_arguments={"is_sim": "True"}.items()
        )

    # تشغيل واجهة السلايدرز مع عمل Remap للتوبيك عشان يبعت لـ joint_commands
    joint_state_publisher_gui_node = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        remappings=[
            ("/joint_states", "/joint_commands"),
        ]
    )

    # تشغيل كود البايثون اللي بيحول من joint_commands لـ trajectory
    slider_control_node = Node(
        package="assem1_controller",
        executable="slider_controller.py"
    )

    return LaunchDescription(
        [
            controller,
            joint_state_publisher_gui_node,
            slider_control_node
        ]
    )