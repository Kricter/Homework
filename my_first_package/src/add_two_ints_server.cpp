#include "rclcpp/rclcpp.hpp"
#include "example_interfaces/srv/add_two_ints.hpp" // 引用自定义服务头文件

#include <memory>

class AddTwoIntsServer : public rclcpp::Node {
public:
    AddTwoIntsServer() : Node("add_two_ints_server") {
        // 创建服务，服务名为 "add_two_ints"，回调函数为 &AddTwoIntsServer::handle_add
        service_ = this->create_service<example_interfaces::srv::AddTwoInts>(
            "add_two_ints",
            std::bind(&AddTwoIntsServer::handle_add, this, std::placeholders::_1, std::placeholders::_2)
        );
        RCLCPP_INFO(this->get_logger(), "Ready to add two ints.");
    }

private:
    // 回调函数：处理客户端请求
    void handle_add(
        const std::shared_ptr<example_interfaces::srv::AddTwoInts::Request> request,
        std::shared_ptr<example_interfaces::srv::AddTwoInts::Response> response
    ) {
        response->sum = request->a + request->b; // 计算加法
        RCLCPP_INFO(this->get_logger(), "Incoming request\na: %ld, b: %ld", request->a, request->b);
        RCLCPP_INFO(this->get_logger(), "Sending back response: [%ld]", response->sum);
    }
    rclcpp::Service<example_interfaces::srv::AddTwoInts>::SharedPtr service_;
};

int main(int argc, char **argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<AddTwoIntsServer>());
    rclcpp::shutdown();
    return 0;
}
