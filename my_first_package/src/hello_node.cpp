#include "rclcpp/rclcpp.hpp"

int main(int argc, char **argv) {
    rclcpp::init(argc, argv);           // 初始化
    // 创建节点：cpp_hello_node
    auto node = rclcpp::Node::make_shared("cpp_hello_node");

    RCLCPP_INFO(node->get_logger(), "Hello World from C++!");

    rclcpp::shutdown();                 // 关闭
    return 0;
}