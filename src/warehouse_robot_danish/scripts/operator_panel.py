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
        rospy.init_node("warehouse_operator_panel", disable_signals=True)

        self.client = actionlib.SimpleActionClient("move_base", MoveBaseAction)

        # CRITICAL FIX: Wait indefinitely until the server is perfectly ready.
        rospy.loginfo("Waiting for move_base action server to become fully active...")
        self.client.wait_for_server()
        rospy.loginfo("Connected to move_base successfully!")

        # Waypoints loaded from W9 drafts - these will be re-calibrated in RViz shortly.
        self.points = {
            "Home": (0.21, -0.83, 0.0),
            "Home Approach": (2.16, -1.43, 3.14),
            "Shelf A": (8.56, -3.34, -1.57),
            "Shelf A Exit": (7.04, -3.39, 3.14),
            "Shelf B": (8.65, -6.9, 1.57),
            "Shelf B Exit": (6.97, -6.98, 3.14),
            "Pickup": (4.55, -10.62, 3.14),
            "Drop-off": (6.89, 6.44, 0.0),
            "Main Aisle": (3.35, -2.35, 3.14)
        }

        self.route = ["Home", "Home Approach", "Shelf A", "Shelf A Exit", "Shelf B", "Shelf B Exit", "Pickup", "Drop-off", "Main Aisle", "Home Approach", "Home"]
        self.current_station = "Home"

        # UI Setup
        self.root = tk.Tk()
        self.root.title("Warehouse Robot Control Panel")
        self.root.geometry("450x550")
        self.root.configure(bg="#2d2d2d")

        title = tk.Label(self.root, text="Warehouse Operator Panel", font=("Arial", 16, "bold"), bg="#2d2d2d", fg="white")
        title.pack(pady=15)

        self.status_label = tk.Label(self.root, text="Status: Online & Ready", font=("Arial", 11, "bold"), bg="#2d2d2d", fg="#4CAF50")
        self.status_label.pack(pady=10)

        for point_name in self.points:
            btn = tk.Button(self.root, text=f"Dispatch to {point_name}", font=("Arial", 10), width=35, height=2, bg="#3d3d3d", fg="white", command=lambda name=point_name: self.run_thread(name))
            btn.pack(pady=4)

        mission_btn = tk.Button(self.root, text="Start Full Autonomous Mission", font=("Arial", 10, "bold"), width=35, height=2, bg="#4CAF50", fg="white", command=self.run_full_mission_thread)
        mission_btn.pack(pady=12)

        cancel_btn = tk.Button(self.root, text="EMERGENCY STOP (Cancel Goal)", font=("Arial", 10, "bold"), width=35, height=2, bg="#f44336", fg="white", command=self.cancel_goal)
        cancel_btn.pack(pady=4)

    def set_status(self, text, color="#4CAF50"):
        self.status_label.config(text=f"Status: {text}", fg=color)
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

        self.set_status(f"Navigating to {point_name}...", color="#FF9800")
        self.client.send_goal(goal)
        finished = self.client.wait_for_result(rospy.Duration(120))

        if not finished:
            self.client.cancel_goal()
            self.set_status(f"Timeout reaching {point_name}", color="#f44336")
            return False

        if self.client.get_state() == GoalStatus.SUCCEEDED:
            self.set_status(f"Arrived at {point_name}", color="#4CAF50")
            return True
        else:
            self.set_status(f"Failed to reach {point_name}", color="#f44336")
            return False

    def run_thread(self, point_name):
        threading.Thread(target=self.dispatch_logic, args=(point_name,), daemon=True).start()

    def dispatch_logic(self, point_name):
        # Auto-route out of narrow aisles if manually dispatched elsewhere
        if self.current_station == "Shelf A" and point_name not in ["Shelf A", "Shelf A Exit"]:
            if not self.send_goal("Shelf A Exit"): return
        elif self.current_station == "Shelf B" and point_name not in ["Shelf B", "Shelf B Exit"]:
            if not self.send_goal("Shelf B Exit"): return
        elif self.current_station == "Home" and point_name not in ["Home", "Home Approach"]:
            if not self.send_goal("Home Approach"): return
        elif self.current_station == "Drop-off" and point_name not in ["Drop-off", "Main Aisle"]:
            if not self.send_goal("Main Aisle"): return
            
        # Intercept incoming route to Home
        if point_name == "Home" and self.current_station != "Home Approach":
            if not self.send_goal("Home Approach"): return
            
        if self.send_goal(point_name):
            self.current_station = point_name

    def run_full_mission(self):
        self.set_status("Starting Full Autonomous Mission", color="#FF9800")
        for point in self.route:
            if not self.send_goal(point):
                self.set_status(f"Mission aborted at {point}", color="#f44336")
                return
            self.current_station = point
            rospy.sleep(2)
        self.set_status("Full Mission Completed Successfully!", color="#4CAF50")

    def run_full_mission_thread(self):
        threading.Thread(target=self.run_full_mission, daemon=True).start()

    def cancel_goal(self):
        self.client.cancel_goal()
        self.set_status("Movement Cancelled via E-STOP", color="#f44336")

    def start(self):
        self.root.protocol("WM_DELETE_WINDOW", lambda: (self.client.cancel_goal(), self.root.destroy()))
        self.root.mainloop()

if __name__ == "__main__":
    ui = WarehouseUI()
    ui.start()
