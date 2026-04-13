import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    # تعديل مسار الحزمة لـ assem1_description
    assem1_description_dir = get_package_share_directory("assem1_description")

    # تحديد مسار ملف الـ xacro بتاعك
    model_arg = DeclareLaunchArgument(
        name="model", 
        default_value=os.path.join(assem1_description_dir, "urdf", "assem1.urdf.xacro"),
        description="Absolute path to robot urdf file"
    )

    # التحقق من الـ Distro عشان Ignition
    ros_distro = os.environ.get("ROS_DISTRO", "humble")
    is_ignition = "True" if ros_distro == "humble" else "False"

    # معالجة الـ Xacro وتحويله لـ URDF
    robot_description = ParameterValue(Command([
            "xacro ",
            LaunchConfiguration("model"),
            " is_ignition:=",
            is_ignition
        ]),
        value_type=str
    )

    # عقدة Robot State Publisher
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description}]
    )

    # عقدة الـ GUI لتحريك المفاصل يدوياً في RViz
    joint_state_publisher_gui_node = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui"
    )

    # تشغيل RViz باستخدام ملف الـ config بتاعك
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", os.path.join(assem1_description_dir, "rviz", "display.rviz")],
    )

    return LaunchDescription([
        model_arg,
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz_node
    ])