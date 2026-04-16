#!/usr/bin/env python3
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

        # المشترك والمحرر
        self.image_sub = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10)
        self.coords_pub = self.create_publisher(String, '/color_coordinates', 10)

        # OpenCV bridge
        self.bridge = CvBridge()

        # إعداد TF2
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        # بارامترات الكاميرا (Intrinsic parameters)
        self.fx, self.fy = 585.0, 588.0
        self.cx, self.cy = 320.0, 160.0

        self.get_logger().info("Color Detector Node Started - Logger Enabled")

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f"Failed to convert image: {e}")
            return

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # نطاقات الألوان (الأحمر تم تضييقه بناءً على طلبك)
        color_ranges = {
            "R": [(0, 100, 50), (8, 255, 255)],
            "G": [(55, 200, 200), (75, 255, 255)],
            "B": [(90, 200, 200), (130, 255, 255)]
        }

        for color_id, (lower, upper) in color_ranges.items():
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for cnt in contours:
                if cv2.contourArea(cnt) > 150:
                    # 1. حساب المستطيل المائل والسنتر
                    rect = cv2.minAreaRect(cnt)
                    box = cv2.boxPoints(rect)
                    box = np.int0(box)

                    M = cv2.moments(cnt)
                    if M["m00"] != 0:
                        cx_pix = int(M["m10"] / M["m00"])
                        cy_pix = int(M["m01"] / M["m00"])
                        
                        # 2. الرسم على الصورة (نقطة سوداء فقط بدون كلمة Center)
                        cv2.drawContours(frame, [box], 0, (0, 255, 255), 2)
                        cv2.circle(frame, (cx_pix, cy_pix), 5, (0, 0, 0), -1)
                        cv2.putText(frame, color_id, (box[0][0], box[0][1] - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

                        # 3. التحويل الإحداثي
                        Z = 0.5 # القيمة الافتراضية للعمق
                        X_cam = (cx_pix - self.cx) * Z / self.fx
                        Y_cam = (cy_pix - self.cy) * Z / self.fy

                        try:
                            t = self.tf_buffer.lookup_transform(
                                "base_link", 
                                "camera_link", 
                                rclpy.time.Time(),
                                timeout=Duration(seconds=0.1))

                            rot = [t.transform.rotation.x, t.transform.rotation.y, 
                                   t.transform.rotation.z, t.transform.rotation.w]
                            T = tf_transformations.quaternion_matrix(rot)
                            T[0:3, 3] = [t.transform.translation.x, 
                                         t.transform.translation.y, 
                                         t.transform.translation.z]

                            pt_cam = np.array([X_cam, Y_cam, Z, 1.0])
                            pt_base = T @ pt_cam

                            # 4. طباعة الإحداثيات في التيرمينال ونشرها
                            msg_str = f"{color_id}: X={pt_base[0]:.3f}, Y={pt_base[1]:.3f}, Z={pt_base[2]:.3f}"
                            self.get_logger().info(msg_str) # إعادة التفعيل هنا
                            self.coords_pub.publish(String(data=msg_str))
                            
                        except Exception:
                            pass

        cv2.imshow("Detection Window", frame)
        cv2.waitKey(1)

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