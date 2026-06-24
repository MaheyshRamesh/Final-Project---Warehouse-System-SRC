#!/usr/bin/env python3

import sys
import math
import threading
import tkinter as tk

import rospy
import actionlib

from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from geometry_msgs.msg import Quaternion
from actionlib_msgs.msg import GoalStatus


def yaw_to_quaternion(yaw):
    q = Quaternion()
    q.z = math.sin(yaw / 2.0)
    q.w = math.cos(yaw / 2.0)
    return q


class WarehouseUI:
    def __init__(self):
        rospy.init_node("w9_warehouse_ui", disable_signals=True)

        self.client = actionlib.SimpleActionClient("move_base", MoveBaseAction)

        rospy.loginfo("Waiting for move_base...")
        server_ready = self.client.wait_for_server(rospy.Duration(20))

        if not server_ready:
            rospy.logerr("move_base is not running. Start navigation first.")
            sys.exit(1)

        rospy.loginfo("Connected to move_base.")

        # EDIT THESE COORDINATES AFTER CHECKING YOUR RViz MAP
        self.points = {
            "Home": (-2.60, -2.80, -1.5708),
            "Shelf A": (2.00, 1.00, 0.0),
            "Shelf B": (4.00, 1.00, 0.0),
            "Pickup": (3.00, -1.00, 1.5708),
            "Drop-off": (1.00, -2.00, 3.1416)
        }

        self.route = ["Home", "Shelf A", "Shelf B", "Pickup", "Drop-off", "Home"]

        self.root = tk.Tk()
        self.root.title("Warehouse Robot Control Panel")
        self.root.geometry("420x500")

        title = tk.Label(
            self.root,
            text="Warehouse Robot Control Panel",
            font=("Arial", 15, "bold")
        )
        title.pack(pady=10)

        subtitle = tk.Label(
            self.root,
            text="Autonomous Inventory and Delivery Robot",
            font=("Arial", 10)
        )
        subtitle.pack(pady=5)

        self.status_label = tk.Label(
            self.root,
            text="Status: Ready",
            font=("Arial", 10),
            fg="blue"
        )
        self.status_label.pack(pady=10)

        for point_name in self.points:
            button = tk.Button(
                self.root,
                text="Go to " + point_name,
                width=30,
                height=2,
                command=lambda name=point_name: self.run_thread(name)
            )
            button.pack(pady=5)

        mission_button = tk.Button(
            self.root,
            text="Start Full Mission",
            width=30,
            height=2,
            bg="green",
            fg="white",
            command=self.run_full_mission_thread
        )
        mission_button.pack(pady=10)

        stop_button = tk.Button(
            self.root,
            text="Cancel Current Goal",
            width=30,
            height=2,
            bg="red",
            fg="white",
            command=self.cancel_goal
        )
        stop_button.pack(pady=5)

        close_button = tk.Button(
            self.root,
            text="Close UI",
            width=30,
            height=2,
            command=self.close_ui
        )
        close_button.pack(pady=5)

    def set_status(self, text):
        self.status_label.config(text="Status: " + text)
        rospy.loginfo(text)

    def send_goal(self, point_name):
        x, y, yaw = self.points[point_name]

        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = "map"
        goal.target_pose.header.stamp = rospy.Time.now()

        goal.target_pose.pose.position.x = x
        goal.target_pose.pose.position.y = y
        goal.target_pose.pose.position.z = 0.0
        goal.target_pose.pose.orientation = yaw_to_quaternion(yaw)

        self.set_status("Sending robot to " + point_name)
        self.client.send_goal(goal)

        finished = self.client.wait_for_result(rospy.Duration(120))

        if not finished:
            self.client.cancel_goal()
            self.set_status("Timeout at " + point_name)
            return False

        result_state = self.client.get_state()

        if result_state == GoalStatus.SUCCEEDED:
            self.set_status("Arrived at " + point_name)
            return True
        else:
            self.set_status("Failed to reach " + point_name)
            return False

    def run_thread(self, point_name):
        thread = threading.Thread(target=self.send_goal, args=(point_name,))
        thread.daemon = True
        thread.start()

    def run_full_mission(self):
        self.set_status("Starting full mission")

        for point in self.route:
            success = self.send_goal(point)

            if not success:
                self.set_status("Mission stopped at " + point)
                return

            rospy.sleep(2)

        self.set_status("Full mission completed")

    def run_full_mission_thread(self):
        thread = threading.Thread(target=self.run_full_mission)
        thread.daemon = True
        thread.start()

    def cancel_goal(self):
        self.client.cancel_goal()
        self.set_status("Current goal cancelled")

    def close_ui(self):
        self.client.cancel_goal()
        self.root.destroy()

    def start(self):
        self.root.mainloop()


if __name__ == "__main__":
    ui = WarehouseUI()
    ui.start()
