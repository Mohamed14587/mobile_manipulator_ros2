#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

class SliderControl(Node):
    def __init__(self):
        super().__init__("slider_control")
        # هننشر على توبيك الـ arm_controller الخاص بالروبوت بتاعنا
        self.arm_pub_ = self.create_publisher(JointTrajectory, "arm_controller/joint_trajectory", 10)
        
        # الاشتراك في السلايدرز
        self.sub_ = self.create_subscription(JointState, "joint_commands", self.sliderCallback, 10)
        
        self.get_logger().info("Assem1 Slider Control Node started")

    def sliderCallback(self, msg):
        arm_controller = JointTrajectory()
        
        # أسماء المفاصل اللي حددناها في الـ URDF والـ YAML
        arm_controller.joint_names = ["joint1", "joint2"]
        
        arm_goal = JointTrajectoryPoint()
        
        # بياخد أول قيمتين بس من السلايدر (أو حسب ترتيبهم في الـ GUI)
        # لو السلايدر بيبعت أكتر من قيمتين، msg.position[:2] هتضمن إننا ناخد أول اتنين بس
        if len(msg.position) >= 2:
            arm_goal.positions = [msg.position[0], msg.position[1]]
            
            # تحديد زمن الوصول للهدف (مهم عشان الحركة متكونش فجائية)
            arm_goal.time_from_start.sec = 0
            arm_goal.time_from_start.nanosec = 100000000 # 0.1 ثانية
            
            arm_controller.points.append(arm_goal)
            self.arm_pub_.publish(arm_controller)

def main():
    rclpy.init()
    slider_node = SliderControl()
    try:
        rclpy.spin(slider_node)
    except KeyboardInterrupt:
        pass
    slider_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()