import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # 1. 获取配置文件的路径（假设你的 config.yaml 在工作空间根目录，建议挪到包里）
    # 这里为了简单，我们直接指定你之前创建的路径
    config_path = os.path.expanduser('~/ros2_ws/config.yaml')

    return LaunchDescription([
        # 启动你的参数节点
        Node(
            package='my_first_package',
            executable='param_node.py', # 如果是运行 Python 脚本
            name='minimal_param_node',
            output='screen',
            # 2. 在 Launch 中加载外部 YAML 配置文件
            parameters=[config_path, 
                # 3. 你甚至可以在这里直接覆盖参数，这里的优先级最高！
                {'my_config_param': 'Value from Launch File'}
            ]
        )
    ])
