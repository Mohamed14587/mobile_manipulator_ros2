import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    
    # 1. قراءة ملف الروبوت (URDF) عشان الـ GUI ترسم المؤشرات فوراً وماتستناش جازيبو
    urdf_file = os.path.join(
        get_package_share_directory("assem1_description"), 
        "urdf", 
        "assem1.urdf.xacro"
    )
    
    robot_description = ParameterValue(
        Command(["xacro ", urdf_file, " is_ignition:=True"]),
        value_type=str
    )

    # 2. تشغيل واجهة المستخدم (الريموت)
    joint_state_publisher_gui_node = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        parameters=[{"robot_description": robot_description}], # تم حل مشكلة Waiting for robot_description هنا
        remappings=[
            ("/joint_states", "/joint_commands"),
        ]
    )

    # 3. تشغيل كود بايثون المترجم للأوامر
    slider_control_node = Node(
        package="assem1_controller",
        executable="slider_controller.py"
    )

    return LaunchDescription([
        # لاحظ: تم حذف استدعاء controller.launch.py من هنا لأن جازيبو يتولى تشغيله بالفعل
        joint_state_publisher_gui_node,
        slider_control_node
    ])