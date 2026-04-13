import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command, LaunchConfiguration
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    is_sim = LaunchConfiguration("is_sim")
    
    is_sim_arg = DeclareLaunchArgument(
        "is_sim",
        default_value="True"
    )

    # 1. وصف الروبوت (Robot Description)
    # لازم نستخدم الملف بتاعنا assem1.urdf.xacro
    robot_description = ParameterValue(
        Command(
            [
                "xacro ",
                os.path.join(
                    get_package_share_directory("assem1_description"),
                    "urdf",
                    "assem1.urdf.xacro",
                ),
                " is_sim:=True",
                " is_ignition:=True" 
            ]
        ),
        value_type=str,
    )

    # 2. نود نشر حالة الروبوت
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description,
                     "use_sim_time": is_sim}],
    )

    # 3. Joint State Broadcaster Spawner
    # ده المسؤول عن نشر الـ TF بتاع المفاصل عشان RViz
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager",
            "/controller_manager",
        ],
    )

    # 4. Arm Controller Spawner
    # ده المسؤول عن تشغيل التحكم في armlink1 و armlink2
    arm_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["arm_controller", "--controller-manager", "/controller_manager"],
    )

    # لاحظ إننا شيلنا الـ gripper_controller_spawner والـ ros2_control_node يدوياً
    # لأن جازيبو إجنيشن بيقوم الـ controller_manager تلقائياً بالبلجن

    return LaunchDescription(
        [
            is_sim_arg,
            robot_state_publisher_node,
            joint_state_broadcaster_spawner,
            arm_controller_spawner,
        ]
    )