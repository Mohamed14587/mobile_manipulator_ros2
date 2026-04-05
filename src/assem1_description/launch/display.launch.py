import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    # تأكد أن هذا هو اسم الباكدج الفعلي لديك
    pkg_name = 'assem1_description'
    
    # تم تحديث اسم الملف هنا ليكون mobile_manipulator.xacro
    xacro_file = os.path.join(get_package_share_directory(pkg_name), 'urdf', 'mobile_manipulator.xacro')

    # تحويل محتوى الـ xacro إلى نص لتجنب انهيار العقدة
    robot_description_content = ParameterValue(Command(['xacro ', xacro_file]), value_type=str)

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_content}]
    )

    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui'
    )

    rviz_config = os.path.join(
      get_package_share_directory(pkg_name),
    'rviz',
    'display.rviz'
         )


    rviz_node = Node(
    package='rviz2',
    executable='rviz2',
    name='rviz2',
    arguments=['-d', rviz_config],
    output='screen'
     )

    return LaunchDescription([
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz_node
    ])