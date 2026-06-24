import rospy
import cv2
import time
import os
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

save_dir = "/home/maheysh/Documents/TTTC2343-Autonomous-Warehouse-Robot-Group-11--main/temp_screenshots/"
bridge = CvBridge()
last_save_time = 0

def callback(msg):
    global last_save_time
    now = time.time()
    if now - last_save_time >= 60.0:
        cv_image = bridge.imgmsg_to_cv2(msg, "bgr8")
        filename = os.path.join(save_dir, f"cam_{int(now)}.jpg")
        cv2.imwrite(filename, cv_image)
        rospy.loginfo(f"Saved temporary screenshot: {filename}")
        last_save_time = now

rospy.init_node('auto_screenshotter', anonymous=True)
rospy.Subscriber("/xtion/rgb/image_raw", Image, callback)
rospy.spin()
