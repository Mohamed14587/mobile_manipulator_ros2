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
    assem1_description = get_package_share_directory("assem1_description")

    # ------------------- Arguments -------------------
    model_arg = DeclareLaunchArgument(
        name="model",
        default_value=os.path.join(
            assem1_description,
            "urdf",
            "assem1.urdf.xacro"
        ),
        description="Absolute path to robot urdf file"
    )

    world_name_arg = DeclareLaunchArgument(
        name="world_name",
        default_value="empty"
    )

    # ------------------- World -------------------
    world_path = PathJoinSubstitution([
        assem1_description,
        "worlds",
        PythonExpression([
            "'",
            LaunchConfiguration("world_name"),
            "' + '.world'"
        ])
    ])

    # ------------------- Gazebo resource path -------------------
    model_path = str(Path(assem1_description).parent.resolve())
    model_path += pathsep + os.path.join(assem1_description, 'models')

    gazebo_resource_path = SetEnvironmentVariable(
        "GZ_SIM_RESOURCE_PATH",
        model_path
    )

    # ------------------- ROS distro -------------------
    ros_distro = os.environ.get("ROS_DISTRO", "humble")
    is_ignition = "True" if ros_distro == "humble" else "False"

    # ------------------- Robot Description (PANDA STYLE) -------------------
    robot_description = ParameterValue(
        Command([
            "xacro ",
            LaunchConfiguration("model"),
            " is_ignition:=",
            is_ignition
        ]),
        value_type=str
    )

    # ------------------- Robot State Publisher -------------------
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{
            "robot_description": robot_description,
            "use_sim_time": True
        }],
        output="screen"
    )

    # ------------------- Gazebo -------------------
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory("ros_gz_sim"),
                "launch",
                "gz_sim.launch.py"
            )
        ]),
        launch_arguments={
            "gz_args": PythonExpression([
                "'",
                world_path,
                " -v 4 -r'"
            ])
        }.items()
    )

    # ------------------- Spawn Robot -------------------
    gz_spawn_entity = Node(
        package="ros_gz_sim",
        executable="create",
        output="screen",
        arguments=[
            "-topic", "robot_description",
            "-name", "assem1",
            "-x", "0.0",
            "-y", "0.0",
            "-z", "0.304",
            "-R", "0.0",
            "-P", "0.0",
            "-Y", "0.0",
        ],
    )

    # ------------------- Bridge -------------------
    gz_ros2_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
            "/camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo"
        ],
        output="screen"
    )

    ros_gz_image_bridge = Node(
        package="ros_gz_image",
        executable="image_bridge",
        arguments=["/camera/image_raw"],
        output="screen"
    )

    # ------------------- Launch -------------------
    return LaunchDescription([
        model_arg,
        world_name_arg,
        gazebo_resource_path,
        robot_state_publisher_node,
        gazebo,
        gz_spawn_entity,
        gz_ros2_bridge,
        ros_gz_image_bridge
    ])
