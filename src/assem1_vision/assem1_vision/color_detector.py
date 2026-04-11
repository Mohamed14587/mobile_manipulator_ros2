#!/usr/bin/env python3
import os
os.environ["QT_QPA_PLATFORM"] = "xcb"

import rclpy
from rclpy.node import Node
from rclpy.duration import Duration

import cv2
import numpy as np

from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge

import tf2_ros
from scipy.spatial.transform import Rotation as R


class ColorDetector(Node):
    def __init__(self):
        super().__init__('color_detector')

        self.image_sub = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10)

        self.coords_pub = self.create_publisher(
            String, '/color_coordinates', 10)

        self.bridge = CvBridge()

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        # Camera intrinsics
        self.fx = 585.0
        self.fy = 588.0
        self.cx = 320.0
        self.cy = 160.0

        self.get_logger().info("🔥 Color Detector (SCIPY VERSION)")

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f"Image conversion failed: {e}")
            return

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        color_ranges = {
            "R": [(0,150,150),(5,255,255)],
            "G": [(55,200,200),(60,255,255)],
            "B": [(90,200,200),(128,255,255)]
        }

        for color_id, (lower, upper) in color_ranges.items():
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))

            kernel = np.ones((5,5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

            contours,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for cnt in contours:
                if cv2.contourArea(cnt) > 100:

                    # 🔥 Rotated box
                    rect = cv2.minAreaRect(cnt)
                    box = cv2.boxPoints(rect)
                    box = np.intp(box)

                    cx_pix = int(rect[0][0])
                    cy_pix = int(rect[0][1])
                    angle = rect[2]

                    cv2.drawContours(frame, [box], 0, (0,255,255), 2)
                    cv2.circle(frame, (cx_pix, cy_pix), 5, (255,0,0), -1)

                    cv2.putText(frame, f"{color_id}",
                                (cx_pix-20, cy_pix-20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                                (0,255,255), 2)

                    # pixel → camera
                    Z = 0.1
                    Y = (cx_pix - self.cx) * Z / self.fx * -10
                    X = (cy_pix - self.cy) * Z / self.fy

                    try:
                        t = self.tf_buffer.lookup_transform(
                            "base_link",
                            "camera_link",
                            rclpy.time.Time(),
                            timeout=Duration(seconds=1.0))

                        trans = np.array([
                            t.transform.translation.x,
                            t.transform.translation.y,
                            t.transform.translation.z
                        ])

                        quat = [
                            t.transform.rotation.x,
                            t.transform.rotation.y,
                            t.transform.rotation.z,
                            t.transform.rotation.w
                        ]

                        # 🔥 Scipy transform
                        rot_matrix = R.from_quat(quat).as_matrix()

                        T = np.eye(4)
                        T[:3,:3] = rot_matrix
                        T[:3,3] = trans

                        pt_cam = np.array([X, Y, Z, 1.0])
                        pt_base = T @ pt_cam

                        msg_str = f"{color_id},{pt_base[0]:.3f},{pt_base[1]:.3f},{pt_base[2]:.3f},{angle:.2f}"
                        self.coords_pub.publish(String(data=msg_str))

                        self.get_logger().info(msg_str)

                    except Exception as e:
                        self.get_logger().warn(f"TF failed: {e}")

        try:
            cv2.imshow("Color Detection", frame)
            cv2.waitKey(1)
        except Exception as e:
            self.get_logger().warn(f"GUI error: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = ColorDetector()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()