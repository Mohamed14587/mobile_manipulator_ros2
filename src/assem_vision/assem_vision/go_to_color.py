#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from pymoveit2 import MoveIt2
from pymoveit2.robots import panda


class GoToColor(Node):

    def __init__(self):
        super().__init__("go_to_color")

        self.target_color = "G"
        self.done = False

        # MoveIt interface
        self.moveit2 = MoveIt2(
            node=self,
            joint_names=panda.joint_names(),
            base_link_name=panda.base_link_name(),
            end_effector_name=panda.end_effector_name(),
            group_name=panda.MOVE_GROUP_ARM,
        )

        # حركة أبطأ = أدق
        self.moveit2.max_velocity = 0.15
        self.moveit2.max_acceleration = 0.15

        # Subscriber
        self.sub = self.create_subscription(
            String,
            "/color_coordinates",
            self.callback,
            10
        )

        self.get_logger().info("Waiting for GREEN object...")

    def callback(self, msg):

        if self.done:
            return

        try:
            color, x, y, z = msg.data.split(",")
            color = color.strip().upper()

            if color != self.target_color:
                return

            bx = float(x)
            by = float(y)
            bz = float(z)

            self.get_logger().info(
                f"Target G (base_link): {bx:.3f}, {by:.3f}, {bz:.3f}"
            )

            # 🔥 خليه يقف فوق البوكس
            target_position = [
                bx,
                by,
                bz + 0.12   # عدل الرقم ده لو محتاج ارتفاع مختلف
            ]

            # orientation عمودي (suction نازل لتحت)
            quat = [0.0, 0.707, 0.0, 0.707]

            self.moveit2.move_to_pose(
                position=target_position,
                quat_xyzw=quat
            )

            self.moveit2.wait_until_executed()

            self.get_logger().info("Reached above GREEN box ✅")

            self.done = True

        except Exception as e:
            self.get_logger().error(f"Error: {e}")


def main():
    rclpy.init()
    node = GoToColor()
    rclpy.spin(node)


if __name__ == "__main__":
    main()