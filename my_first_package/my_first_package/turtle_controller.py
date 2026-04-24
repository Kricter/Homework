#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from std_srvs.srv import SetBool  # 换成绝对稳妥的接口
import math

class TurtleMaster(Node):
    def __init__(self):
        super().__init__('turtle_controller')
        self.declare_parameter('linear_speed', 2.0)
        
        self.pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.sub = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        self.srv = self.create_service(SetBool, 'switch_mode', self.mode_callback)
        
        self.pose = None
        self.special_mode = False 
        self.sub_state = "FORWARD"
        self.distance_traveled = 0.0
        self.target_yaw = 0.0
        self.start_time = self.get_clock().now()
        
        self.create_timer(0.05, self.control_loop)

    def pose_callback(self, msg):
        if self.pose is not None and not self.special_mode:
            dist = math.sqrt((msg.x - self.pose.x)**2 + (msg.y - self.pose.y)**2)
            if self.sub_state == "FORWARD":
                self.distance_traveled += dist
            elif self.sub_state == "BACKWARD":
                self.distance_traveled -= dist
        self.pose = msg

    def mode_callback(self, request, response):
        self.special_mode = request.data
        self.start_time = self.get_clock().now()
        self.sub_state = "FORWARD"
        self.distance_traveled = 0.0
        response.success = True
        response.message = "模式已切换"
        return response

    def control_loop(self):
        if self.pose is None: return
        msg = Twist()
        v = self.get_parameter('linear_speed').value
        t = (self.get_clock().now() - self.start_time).nanoseconds / 1e9

        # --- 模式 A：特殊花活 (True) ---
        if self.special_mode:
            if (int(t) // 10) % 2 == 0: # 前10秒正弦波
                msg.linear.x = v
                msg.angular.z = 3 * math.sin(t * 3.0)
            else: # 后10秒方波
                cycle = t % 1.0
                if cycle < 3.0: msg.linear.x = v
                else: msg.angular.z = 1.571

        # --- 模式 B：精准往返并停止 (False) ---
        else:
            if self.sub_state == "FORWARD":
                if self.pose.x < 1.5 or self.pose.x > 9.5 or self.pose.y < 1.5 or self.pose.y > 9.5:
                    self.target_yaw = self.pose.theta + math.pi
                    while self.target_yaw > math.pi: self.target_yaw -= 2*math.pi
                    while self.target_yaw < -math.pi: self.target_yaw += 2*math.pi
                    self.sub_state = "TURN180"
                else:
                    msg.linear.x = v
            elif self.sub_state == "TURN180":
                diff = self.target_yaw - self.pose.theta
                while diff > math.pi: diff -= 2*math.pi
                while diff < -math.pi: diff += 2*math.pi
                if abs(diff) > 0.02:
                    msg.angular.z = 2.0 if diff > 0 else -2.0
                else:
                    self.sub_state = "BACKWARD"
            elif self.sub_state == "BACKWARD":
                if self.distance_traveled > 0.05:
                    msg.linear.x = v
                else:
                    self.sub_state = "STOP"
            elif self.sub_state == "STOP":
                msg.linear.x = 0.0
                msg.angular.z = 0.0

        self.pub.publish(msg)

def main():
    rclpy.init()
    rclpy.spin(TurtleMaster())
    rclpy.shutdown()

if __name__ == '__main__':
    main()
