#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"
#include <chrono>

using namespace std::chrono_literals;

class Talker : public rclcpp::Node {
public:
    Talker() : Node("cpp_talker") {
        publisher_ = this->create_publisher<std_msgs::msg::String>("hello_topic", 10);
        // 100ms 触发一次，即 10Hz
        timer_ = this->create_wall_timer(100ms, std::bind(&Talker::timer_callback, this));
    }
private:
    void timer_callback() {
        auto msg = std_msgs::msg::String();
        msg.data = "helloworld";
        RCLCPP_INFO(this->get_logger(), "Publishing: '%s'", msg.data.c_str());
        publisher_->publish(msg);
    }
    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
};

int main(int argc, char **argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<Talker>());
    rclcpp::shutdown();
    return 0;
}