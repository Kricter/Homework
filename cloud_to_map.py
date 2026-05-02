import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
import sensor_msgs_py.point_cloud2 as pc2
import cv2
import numpy as np

class AntiGhostingMapNode(Node):
    def __init__(self):
        super().__init__('anti_ghosting_map_node')
        
        # 订阅话题
        self.subscription = self.create_subscription(
            PointCloud2,
            '/livox/lidar_PointCloud2', 
            self.listener_callback,
            10)
        
        # 初始化地图画布 
        self.map_canvas = np.zeros((600, 600, 3), dtype=np.uint8)
        self.get_logger().info('任务 4 节点启动：射线清理模式已开启。')

    def listener_callback(self, msg):
        # 提取点云
        points = pc2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True)
        
        # 机器人中心点 (300, 300)
        center = (300, 300)

        for p in points:
            x, y, z = p
            # 投影：1米=30像素
            u = int(x * 30 + 300)
            v = int(y * 30 + 300)

            if 0 <= u < 600 and 0 <= v < 600:
                # --- 任务 3：坡度/高度逻辑 ---
                if z < 0.15:
                    # 极低的点，可能是路或坡，用绿色标记
                    color = (0, 100, 0)
                elif 0.15 <= z < 1.2:
                    # 障碍物高度，用白色标记
                    color = (255, 255, 255)
                else:
                    # 太高的点跳过
                    continue

                # --- 任务 4：射线清理逻辑  ---
                # 在标记新点前，先从中心向该点画一条薄薄的黑线来擦除该路径上留下的物体残影
                cv2.line(self.map_canvas, center, (u, v), (0, 0, 0), 1)
                
                # 绘制当前检测到的真实点
                self.map_canvas[v, u] = color

        # 膨胀
        kernel = np.ones((2, 2), np.uint8)
        display_map = cv2.dilate(self.map_canvas, kernel, iterations=1)
        
        # 画出机器人位置
        cv2.circle(display_map, center, 4, (0, 0, 255), -1)
        # 画出前进方向
        cv2.line(display_map, center, (315, 300), (0, 0, 255), 2)

        cv2.imshow("Task 4: Anti-Ghosting Map", display_map)
        
        # 按 'c' 键手动清图
        if cv2.waitKey(1) & 0xFF == ord('c'):
            self.map_canvas.fill(0)

def main(args=None):
    rclpy.init(args=args)
    node = AntiGhostingMapNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
