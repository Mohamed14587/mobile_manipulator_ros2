import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    # 1. تضمين ملف تشغيل الكنترولرز الأساسي (Spawners)
    controller = IncludeLaunchDescription(
            os.path.join(
                get_package_share_directory("assem1_controller"), # تغيير لاسم باكدج الكنترولر بتاعتك
                "launch",
                "controller.launch.py"
            ),
            launch_arguments={"is_sim": "True"}.items()
        )

    # 2. نود الواجهة الرسومية (المنزلقات - Sliders)
    # بنعمل remapping عشان السلايدرز تبعت لـ slider_controller.py مش للروبوت علطول
    joint_state_publisher_gui_node = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        remappings=[
            ("/joint_states", "/joint_commands"),
        ]
    )

    # 3. تشغيل كود البايثون اللي بيحول من Sliders لـ Trajectory
    slider_control_node = Node(
        package="assem1_controller", # تغيير لاسم باكدج الكنترولر بتاعتك
        executable="slider_controller.py"
    )

    return LaunchDescription(
        [
            controller,
            joint_state_publisher_gui_node,
            slider_control_node
        ]
    )