#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

class SliderController(Node):
    def __init__(self):
        super().__init__('slider_control')
        
        self.subscription = self.create_subscription(
            JointState,
            '/joint_commands',
            self.sliderCallback,
            10)
            
        self.arm_pub = self.create_publisher(
            JointTrajectory,
            '/arm_controller/joint_trajectory',
            10)
            
        self.get_logger().info('Slider Control Node started')

    def sliderCallback(self, msg):
        if len(msg.position) >= 2:
            arm_msg = JointTrajectory()
            arm_msg.joint_names = ['armlinl1', 'armlinl2'] 
            
            arm_goal = JointTrajectoryPoint()
            arm_goal.positions = [msg.position[0], msg.position[1]]
            
            arm_msg.points.append(arm_goal)
            self.arm_pub.publish(arm_msg)

def main(args=None):
    rclpy.init(args=args)
    node = SliderController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()