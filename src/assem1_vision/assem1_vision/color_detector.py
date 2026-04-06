#!/usr/bin/env python3
import os
os.environ["QT_QPA_PLATFORM"] = "xcb"   # 🔥 حل مشكلة GUI

import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
import cv2
import numpy as np
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import tf2_ros
import tf_transformations

class ColorDetector(Node):
    def __init__(self):
        super().__init__('color_detector')

        # Subscriber
        self.image_sub = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10)

        # Publisher
        self.coords_pub = self.create_publisher(
            String, '/color_coordinates', 10)

        # OpenCV
        self.bridge = CvBridge()

        # TF2
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        # Camera intrinsics
        self.fx = 585.0
        self.fy = 588.0
        self.cx = 320.0
        self.cy = 160.0

        self.get_logger().info("Color Detector Started (GUI + TF working)")

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

            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)

            contours,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for cnt in contours:
                if cv2.contourArea(cnt) > 50:
                    x,y,w,h = cv2.boundingRect(cnt)
                    cx_pix, cy_pix = x+w//2, y+h//2

                    # رسم
                    cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,255),2)
                    cv2.putText(frame,color_id,(x,y-10),
                                cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,255,255),2)

                    # pixel → camera
                    Z = 0.1
                    Y = (cx_pix - self.cx) * Z / self.fx * -10
                    X = (cy_pix - self.cy) * Z / self.fy

                    try:
                        # 🔥 هنا التعديل المهم
                        t = self.tf_buffer.lookup_transform(
                            "base_link",      # ✅ بدل panda_link0
                            "camera_link",
                            rclpy.time.Time(),
                            timeout=Duration(seconds=1.0))

                        trans = np.array([
                            t.transform.translation.x,
                            t.transform.translation.y,
                            t.transform.translation.z
                        ])

                        rot = [
                            t.transform.rotation.x,
                            t.transform.rotation.y,
                            t.transform.rotation.z,
                            t.transform.rotation.w
                        ]

                        T = tf_transformations.quaternion_matrix(rot)
                        T[:3,3] = trans

                        pt_cam = np.array([X,Y,Z,1.0])
                        pt_base = T @ pt_cam

                        msg_str = f"{color_id},{pt_base[0]:.3f},{pt_base[1]:.3f},{pt_base[2]:.3f}"
                        self.coords_pub.publish(String(data=msg_str))

                        self.get_logger().info(msg_str)

                    except Exception as e:
                        self.get_logger().warn(f"TF failed: {e}")

        # GUI
        try:
            cv2.namedWindow("Color Detection", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Color Detection", 640, 320)
            cv2.imshow("Color Detection", frame)
            cv2.waitKey(1)
        except Exception as e:
            self.get_logger().warn(f"OpenCV GUI error: {e}")


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