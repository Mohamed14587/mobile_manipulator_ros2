#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/joint_state.hpp>
#include <trajectory_msgs/msg/joint_trajectory.hpp>
#include <trajectory_msgs/msg/joint_trajectory_point.hpp>
#include <builtin_interfaces/msg/duration.hpp>
#include <chrono>
#include <vector>

using namespace std::chrono_literals;
using std::placeholders::_1;

class SliderControl : public rclcpp::Node
{
public:
  SliderControl() : Node("slider_control")
  {
    // الاشتراك في التوبيك القادم من الـ GUI
    sub_ = create_subscription<sensor_msgs::msg::JointState>(
        "joint_commands", 10, std::bind(&SliderControl::sliderCallback, this, _1));
        
    // النشر على الكنترولر الخاص بـ Assem
    arm_pub_ = create_publisher<trajectory_msgs::msg::JointTrajectory>(
        "arm_controller/joint_trajectory", 10);
        
    RCLCPP_INFO(get_logger(), "Assem Slider Control Node (C++) started");
  }

private:
  rclcpp::Subscription<sensor_msgs::msg::JointState>::SharedPtr sub_;
  rclcpp::Publisher<trajectory_msgs::msg::JointTrajectory>::SharedPtr arm_pub_;

  void sliderCallback(const sensor_msgs::msg::JointState &msg) const
  {
    // التأكد من وجود بيانات للمفصلين (joint_1 و joint_2)
    if (msg.position.size() < 2) {
        return;
    }

    trajectory_msgs::msg::JointTrajectory arm_command;
    // أسماء المفاصل كما هي معرفة في الـ URDF الخاص بك
    arm_command.joint_names = {"joint_1", "joint_2"};

    trajectory_msgs::msg::JointTrajectoryPoint arm_goal;
    // أخذ أول قيمتين فقط من السلايدر
    arm_goal.positions = {msg.position.at(0), msg.position.at(1)};
    
    // إلزامي: تحديد زمن الوصول لضمان استجابة الكنترولر
    arm_goal.time_from_start.sec = 0;
    arm_goal.time_from_start.nanosec = 100000000; // 0.1 ثانية
    
    arm_command.points.push_back(arm_goal);
    arm_pub_->publish(arm_command);
  }
};

int main(int argc, char* argv[])
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<SliderControl>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}