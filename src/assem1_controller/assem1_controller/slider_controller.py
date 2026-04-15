#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

class SliderControl(Node):
    def __init__(self):
        super().__init__("slider_control")
        # التوبيكس الخاصة بكنترولرات assem1
        self.arm_pub_ = self.create_publisher(JointTrajectory, "arm_controller/joint_trajectory", 10)
        # الاشتراك في الأوامر القادمة من الـ GUI
        self.sub_ = self.create_subscription(JointState, "joint_commands", self.sliderCallback, 10)
        self.get_logger().info("Slider Control Node started for assem1")

    def sliderCallback(self, msg):
        arm_controller = JointTrajectory()
        
        # أسماء المفاصل الخاصة بروبوت assem1 (راجعناها في الـ URDF)
        arm_controller.joint_names = ["joint_1", "joint_2"]
        # تأكد من الاسم في ملف الـ YAML والـ URDF
        
        arm_goal = JointTrajectoryPoint()
        
        # تقسيم الأوضاع (Positions) بناءً على عدد مفاصلك
        # msg.position[0:2] تعني joint_1 و joint_2
        arm_goal.positions = msg.position[:2]
        
        # لو عندك جريبّر، هياخد القيمة اللي بعدها في المصفوفة
       
        
        arm_controller.points.append(arm_goal)
        
        self.arm_pub_.publish(arm_controller)

def main():
    rclpy.init()
    slider_node = SliderControl()
    rclpy.spin(slider_node)
    slider_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()