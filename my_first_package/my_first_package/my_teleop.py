#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_srvs.srv import SetBool
import sys, tty, termios

class MyTeleop(Node):
    def __init__(self):
        super().__init__('my_teleop')
        self.pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.client = self.create_client(SetBool, 'switch_mode')
        
        # 初始速度状态
        self.linear_v = 0.0
        self.angular_w = 0.0
        
        print("---------------------------")
        print("W: 加速 | S: 减速/后退")
        print("A: 左转 | D: 右转")
        print("Space: 紧急停止")
        print("1: 正弦模式 | 0: 往返模式")
        print("Q: 退出")
        print("---------------------------")

    def call_mode(self, val):
        req = SetBool.Request()
        req.data = val
        self.client.call_async(req)

    def run(self):
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while rclpy.ok():
                ch = sys.stdin.read(1)
                msg = Twist()
                
                # 前后控制：累加式
                if ch == 'w':
                    self.linear_v += 0.5
                elif ch == 's':
                    self.linear_v -= 0.5
                # 左右转向
                elif ch == 'a':
                    self.angular_w += 0.5
                elif ch == 'd':
                    self.angular_w -= 0.5
                # 空格停车
                elif ch == ' ':
                    self.linear_v = 0.0
                    self.angular_w = 0.0
                # 模式切换
                elif ch == '1':
                    self.call_mode(True)
                elif ch == '0':
                    self.call_mode(False)
                elif ch == 'q':
                    break

                msg.linear.x = self.linear_v
                msg.angular.z = self.angular_w
                self.pub.publish(msg)
                
                # 打印当前速度状态（可选）
                # print(f"\r当前速度: 线速度={self.linear_v}, 角速度={self.angular_w}", end="")
                
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

def main():
    rclpy.init()
    MyTeleop().run()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
