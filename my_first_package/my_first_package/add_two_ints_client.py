#!/usr/bin/env python3
import sys
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts # 引用自定义服务

class AddTwoIntsClient(Node):
    def __init__(self):
        super().__init__('add_two_ints_client')
        # 创建客户端
        self.client = self.create_client(AddTwoInts, 'add_two_ints')
        
        # 等待服务可用
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
        
        self.req = AddTwoInts.Request()

    def send_request(self, a, b):
        self.req.a = a
        self.req.b = b
        # 发送异步请求
        self.future = self.client.call_async(self.req)
        # 挂起节点直到未来（Future）完成
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()

def main(args=None):
    rclpy.init(args=args)
    if len(sys.argv) < 3:
        print("Usage: ros2 run my_first_package add_two_ints_client.py <a_int> <b_int>")
        return 1
        
    client = AddTwoIntsClient()
    
    # 捕获终端输入的参数
    a = int(sys.argv[1])
    b = int(sys.argv[2])
    
    response = client.send_request(a, b)
    if response is not None:
        client.get_logger().info(
            f'Result of add_two_ints: {a} + {b} = {response.sum}'
        )
    else:
        client.get_logger().error('Service call failed')
        
    client.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
