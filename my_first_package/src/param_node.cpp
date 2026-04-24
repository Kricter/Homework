#include <chrono>
#include <functional>
#include <string>
#include <rclcpp/rclcpp.hpp>

using namespace std::chrono_literals;

class MinimalParam : public rclcpp::Node {
public:
  MinimalParam() : Node("minimal_param_node") {
    // 1. 声明参数
    this->declare_parameter("my_config_param", "new_default_value");

    // 2. 创建定时器，每秒执行一次回调
    timer_ = this->create_wall_timer(
      1000ms, std::bind(&MinimalParam::timer_callback, this));
  }

  void timer_callback() {
    // 3. 实时获取参数值
    std::string my_param = this->get_parameter("my_config_param").as_string();
    RCLCPP_INFO(this->get_logger(), "C++ Node Value: %s", my_param.c_str());
  }

private:
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char ** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<MinimalParam>());
  rclcpp::shutdown();
  return 0;
}
