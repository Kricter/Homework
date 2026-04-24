cmake_minimum_required(VERSION 3.8)
project(my_first_package)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()
# 1. 声明依赖
find_package(rclcpp REQUIRED)

# 2. 编译 C++ 节点
add_executable(cpp_node src/hello_node.cpp)
ament_target_dependencies(cpp_node rclcpp)

# 3. 安装 C++ 节点到系统路径
install(TARGETS
  cpp_node
  DESTINATION lib/${PROJECT_NAME}
)

# 4. 安装 Python 节点到系统路径
install(PROGRAMS
  my_first_package/hello_node.py
  DESTINATION lib/${PROJECT_NAME}
)

find_package(std_msgs REQUIRED)

# C++ 发布者
add_executable(cpp_talker src/cpp_talker.cpp)
ament_target_dependencies(cpp_talker rclcpp std_msgs)

# 安装路径
install(TARGETS cpp_talker DESTINATION lib/${PROJECT_NAME})

install(PROGRAMS
  my_first_package/py_talker.py
  my_first_package/py_listener.py
  DESTINATION lib/${PROJECT_NAME}
)

# 1. 寻找依赖包
find_package(example_interfaces REQUIRED)

# 2. 定义可执行文件（指定源码路径）
add_executable(add_two_ints_server src/add_two_ints_server.cpp)

# 3. 链接依赖
ament_target_dependencies(add_two_ints_server rclcpp example_interfaces)

# 4. 安装到 install 目录，这样 ros2 run 才能找到它
install(TARGETS
  add_two_ints_server
  DESTINATION lib/${PROJECT_NAME}
)

add_executable(param_node_cpp src/param_node.cpp)
ament_target_dependencies(param_node_cpp rclcpp)

install(TARGETS
  param_node_cpp
  DESTINATION lib/${PROJECT_NAME}
)

# 1. 安装 launch 文件夹到 share 目录
install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

# 2. 安装 Python 脚本到 lib 目录 (关键！不然 launch 找不到可执行文件)
# 注意：路径要和你文件夹里实际的路径一致
install(PROGRAMS
  my_first_package/param_node.py
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY launch config
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  my_first_package/param_node.py
  my_first_package/turtle_controller.py
  my_first_package/my_teleop.py
  DESTINATION lib/${PROJECT_NAME}
)
ament_package()
