#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

def main(args=None):
    rclpy.init(args=args)                # 初始化 ROS 2
    node = Node("py_hello_node")         # 节点名：py_hello_node
    node.get_logger().info("Hello World from Python!") # 打印日志
    rclpy.shutdown()                     # 关闭

if __name__ == '__main__':
    main()