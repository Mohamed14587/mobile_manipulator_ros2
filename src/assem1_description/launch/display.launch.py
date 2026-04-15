import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    assem1_description_dir = get_package_share_directory("assem1_description")

    # تحديد مسار ملف الـ xacro الأساسي
    model_arg = DeclareLaunchArgument(name="model", default_value=os.path.join(
                                        assem1_description_dir, "urdf", "assem1.urdf.xacro"
                                        ),
                                      description="Absolute path to robot urdf file")

    # تحديد نوع السيميوليشن بناءً على نسخة ROS
    ros_distro = os.environ["ROS_DISTRO"]
    is_ignition = "True" if ros_distro == "humble" else "False"

    robot_description = ParameterValue(Command([
            "xacro ",
            LaunchConfiguration("model"),
            " is_ignition:=",
            is_ignition
        ]),
        value_type=str
    )

    # نود نشر حالة الروبوت (التحويلات بين اللينكات)
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description}]
    )

    # نود واجهة التحكم اليدوي (Sliders)
    joint_state_publisher_gui_node = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui"
    )

    # نود تشغيل RViz مع ملف الإعدادات الخاص بالروبوت
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