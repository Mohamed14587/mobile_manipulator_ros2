import os
from os import pathsep
from pathlib import Path
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    # 1. إعداد المسارات لحزمة assem1
    # نستخدم الحزمة من مجلد الـ install لضمان التزامن
    assem1_description = get_package_share_directory("assem1_description")

    # تحديد ملف الـ Xacro الرئيسي
    model_path = os.path.join(assem1_description, "urdf", "assem1.urdf.xacro")
    
    model_arg = DeclareLaunchArgument(
        name="model", 
        default_value=model_path,
        description="Absolute path to robot urdf file"
    )

    # 2. تحديد العالم (World)
    world_name_arg = DeclareLaunchArgument(name="world_name", default_value="empty")

    world_path = PathJoinSubstitution([
            assem1_description,
            "worlds",
            PythonExpression(expression=["'", LaunchConfiguration("world_name"), "'", " + '.world'"])
        ]
    )

    # 3. إعداد بيئة جازيبو (GZ_SIM_RESOURCE_PATH)
    # نربط جازيبو مباشرة بمجلد الـ share الخاص بالـ install
    resource_path = str(Path(assem1_description).parent.resolve())
    
    gazebo_resource_path = SetEnvironmentVariable(
        "GZ_SIM_RESOURCE_PATH",
        resource_path
    )

    # 4. معالجة الـ Xacro
    ros_distro = os.environ.get("ROS_DISTRO", "humble")
    is_ignition = "True" if ros_distro == "humble" else "False"

    robot_description = ParameterValue(Command([
            "xacro ",
            LaunchConfiguration("model"),
            " is_ignition:=",
            is_ignition
        ]),
        value_type=str
    )

    # 5. Robot State Publisher
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description,
                     "use_sim_time": True}]
    )

    # 6. تشغيل محاكي Gazebo (Ignition)
    gazebo = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory("ros_gz_sim"), "launch"), "/gz_sim.launch.py"]),
                launch_arguments={
                    "gz_args": PythonExpression(["'", world_path, " -v 4 -r'"])
                }.items()
             )

    # 7. إدراج الروبوت (Spawn)
    # تم تغيير الاسم إلى assem1_arm_only لكسر أي كاش قديم في جازيبو
    gz_spawn_entity = Node(
        package="ros_gz_sim",
        executable="create",
        output="screen",
        arguments=[
            "-topic", "robot_description",
            "-name", "assem1",  # تغيير الاسم هنا جوهري
            "-allow_renaming", "true",
            "-z", "0.0",
        ],
    )

    # 8. الجسر (Bridge)
    gz_ros2_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
        ],
    )

    return LaunchDescription([
        model_arg,
        world_name_arg,
        gazebo_resource_path,
        robot_state_publisher_node,
        gazebo,
        gz_spawn_entity,
        gz_ros2_bridge,
    ])