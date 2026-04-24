import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # 获取YAML路径
    config = os.path.join(
        get_package_share_directory('my_first_package'),
        'config', 'turtle_config.yaml'
    )

    return LaunchDescription([
        # 启动海龟仿真器
        Node(package='turtlesim', executable='turtlesim_node', name='sim'),
        # 启动控制器，并加载YAML参数
        Node(
            package='my_first_package',
            executable='turtle_controller.py',
            parameters=[config],
            output='screen'
        )
    ])
