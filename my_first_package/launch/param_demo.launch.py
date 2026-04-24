import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # 获取配置文件的路径
    config_path = os.path.expanduser('~/ros2_ws/config.yaml')

    return LaunchDescription([
        # 启动参数节点
        Node(
            package='my_first_package',
            executable='param_node.py', 
            name='minimal_param_node',
            output='screen',
            # 在 Launch 中加载外部 YAML 配置文件
            parameters=[config_path, 
                {'my_config_param': 'Value from Launch File'}
            ]
        )
    ])
