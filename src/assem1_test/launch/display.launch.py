import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    pkg_name = 'assem1_test'

    # مسار ملف الـ URDF
    urdf_file = os.path.join(
        get_package_share_directory(pkg_name),
        'urdf',
        'Assem1.urdf'
    )

    # قراءة محتوى الملف
    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()

    robot_description = ParameterValue(robot_desc, value_type=str)

    # robot_state_publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description}],
        output='screen'
    )

    # joint_state_publisher_gui
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui'
    )

    # RViz config
    rviz_config = os.path.join(
        get_package_share_directory(pkg_name),
        'rviz',
        'display.rviz'
    )

    # RViz node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config],
        output='screen'
    )

    return LaunchDescription([
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz_node
    ])
