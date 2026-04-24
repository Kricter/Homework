#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

class MinimalParam(Node):
    def __init__(self):
        super().__init__('minimal_param_node')
        # 声明参数
        self.declare_parameter('my_config_param', 'default_value')
        
        # 创建定时器，每 1.0 秒调用一次下面的 self.timer_callback
        self.timer = self.create_timer(1.0, self.timer_callback)

    def timer_callback(self):
        # 每次执行都要实时 get 一下参数值
        my_param = self.get_parameter('my_config_param').get_parameter_value().string_value
        
        self.get_logger().info('Value: %s' % my_param)

def main():
    rclpy.init()
    node = MinimalParam()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
