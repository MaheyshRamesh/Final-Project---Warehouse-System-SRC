#!/usr/bin/env python3

import rospy
import cv2
import numpy as np
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image
from std_msgs.msg import String

class QRScannerNode:
    def __init__(self):
        rospy.init_node('qr_scanner_node', anonymous=True)
        
        self.bridge = CvBridge()
        self.qr_detector = cv2.QRCodeDetector()
        
        # Publishers
        self.qr_text_pub = rospy.Publisher('/warehouse/qr_detection', String, queue_size=1)
        self.qr_img_pub = rospy.Publisher('/warehouse/qr_image', Image, queue_size=1)
        
        # Subscriber
        self.image_sub = rospy.Subscriber('/xtion/rgb/image_raw', Image, self.image_callback, queue_size=1, buff_size=2**24)
        
        # Rate limiting processing (e.g. 5 Hz)
        self.last_process_time = rospy.Time.now()
        self.process_interval = rospy.Duration(0.2) # 5 Hz
        
        rospy.loginfo("QR Scanner Node initialized. Listening to /xtion/rgb/image_raw...")

    def image_callback(self, data):
        current_time = rospy.Time.now()
        if current_time - self.last_process_time < self.process_interval:
            return
        
        self.last_process_time = current_time
        
        try:
            # The TIAGo camera often publishes in a different encoding, 'bgr8' is standard for OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            rospy.logerr(f"CvBridge Error: {e}")
            return
            
        try:
            from pyzbar.pyzbar import decode
            decoded_objects = decode(cv_image)
            
            data_str = None
            bbox = None
            for obj in decoded_objects:
                data_str = obj.data.decode('utf-8')
                # PyZbar provides polygon points
                if len(obj.polygon) >= 4:
                    bbox = [np.array(obj.polygon, np.int32)]
                elif len(obj.polygon) == 3: # rare but possible
                    pass # handle later
                break # Only handle the first QR code detected
                
            if data_str:
                self.qr_text_pub.publish(data_str)
                
                # Draw bounding box
                if bbox is not None:
                    cv2.polylines(cv_image, bbox, True, (0, 255, 0), 3)
                    
                    # Draw text overlay
                    cv2.putText(cv_image, data_str, (bbox[0][0][0], bbox[0][0][1] - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            
            # Publish image ALWAYS (annotated if QR found, otherwise raw feed)
            try:
                annotated_msg = self.bridge.cv2_to_imgmsg(cv_image, "bgr8")
                self.qr_img_pub.publish(annotated_msg)
            except CvBridgeError as e:
                rospy.logerr(f"CvBridge Error on publish: {e}")
                    
        except ImportError:
            rospy.logerr_throttle(2.0, "pyzbar is not installed! Cannot decode QR codes.")

if __name__ == '__main__':
    try:
        node = QRScannerNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
