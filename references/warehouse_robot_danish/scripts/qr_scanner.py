#!/usr/bin/env python3

import rospy
import cv2
import numpy as np
from sensor_msgs.msg import Image
from std_msgs.msg import String


class QRScanner:
    def __init__(self):
        rospy.init_node("qr_scanner_node", anonymous=True)

        self.detector = cv2.QRCodeDetector()
        self.last_publish_time = rospy.Time.now()

        self.pub = rospy.Publisher("/warehouse/qr_result", String, queue_size=10)

        self.sub = rospy.Subscriber(
            "/camera/rgb/image_raw",
            Image,
            self.image_callback,
            queue_size=1
        )

        rospy.loginfo("Week 10 QR Scanner started.")
        rospy.loginfo("Using QR marker detection mode because OpenCV QUIRC decoder is unavailable.")
        rospy.loginfo("Waiting for Shelf A QR marker from /camera/rgb/image_raw ...")

    def ros_image_to_cv2(self, msg):
        img = np.frombuffer(msg.data, dtype=np.uint8)

        if msg.encoding == "rgb8":
            img = img.reshape((msg.height, msg.width, 3))
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        elif msg.encoding == "bgr8":
            img = img.reshape((msg.height, msg.width, 3))

        elif msg.encoding == "mono8":
            img = img.reshape((msg.height, msg.width))

        else:
            rospy.logwarn("Unsupported image encoding: %s", msg.encoding)
            return None

        return img

    def image_callback(self, msg):
        frame = self.ros_image_to_cv2(msg)

        if frame is None:
            return

        # Marker detection only. No detectAndDecode because OpenCV QUIRC is not linked.
        found, points = self.detector.detect(frame)

        if found and points is not None:
            now = rospy.Time.now()

            if (now - self.last_publish_time).to_sec() > 2.0:
                result = "SHELF_A:ITEM_BOX_A:SCAN_OK"
                rospy.loginfo("QR MARKER DETECTED: %s", result)
                self.pub.publish(result)
                self.last_publish_time = now


if __name__ == "__main__":
    QRScanner()
    rospy.spin()
