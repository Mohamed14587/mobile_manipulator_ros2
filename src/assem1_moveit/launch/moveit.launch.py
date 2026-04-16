import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
from moveit_configs_utils import MoveItConfigsBuilder

def generate_launch_description():
    # Launch Arguments
    is_sim_arg = DeclareLaunchArgument(
        "is_sim", 
        default_value="false",
        description="Use simulation time if true"
    )

    is_ignition_arg = DeclareLaunchArgument(
        "is_ignition", 
        default_value="false",
        description="Use Ignition/Gazebo if true"
    )

    # MoveIt Config Builder
    moveit_config = (
        MoveItConfigsBuilder("assem1", package_name="assem1_moveit")
        .robot_description(
            file_path=os.path.join(
                get_package_share_directory("assem1_description"),
                "urdf", "assem1.urdf.xacro"
            ),
            mappings={"is_ignition": LaunchConfiguration("is_ignition")}
        )
        .robot_description_semantic(file_path="config/assem1.srdf")
        .robot_description_kinematics(file_path="config/kinematics.yaml")
        .planning_pipelines(
            default_planning_pipeline="ompl",
            pipelines=["ompl"]          # هذا السطر مهم جدًا
        )
        .trajectory_execution(file_path="config/moveit_controllers.yaml")
        .joint_limits(file_path="config/joint_limits.yaml")
        .to_moveit_configs()
    )

    # Move Group Node
    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            moveit_config.to_dict(),
            {"use_sim_time": LaunchConfiguration("is_sim")},
        ],
        arguments=["--ros-args", "--log-level", "warn"],
    )

    # RViz
    rviz_config = os.path.join(
        get_package_share_directory("assem1_moveit"),
        "rviz", "moveit.rviz"
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        output="screen",
        arguments=["-d", rviz_config],
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
        ],
    )

    return LaunchDescription([
        is_sim_arg,
        is_ignition_arg,
        move_group_node,
        rviz_node,
    ])