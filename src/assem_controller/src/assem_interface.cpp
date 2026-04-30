#include "assem_controller/assem_interface.hpp"
#include <hardware_interface/types/hardware_interface_type_values.hpp>
#include <pluginlib/class_list_macros.hpp>
#include <cmath>

namespace assem_controller
{

std::string compensateZeros(const int value)
{
  if(value < 10) return "00";
  if(value < 100) return "0";
  return "";
}
  
AssemInterface::AssemInterface() {}

AssemInterface::~AssemInterface()
{
  if (arduino_.IsOpen()) {
    try { arduino_.Close(); }
    catch (...) {
      RCLCPP_FATAL(rclcpp::get_logger("AssemInterface"), "Failed to close port");
    }
  }
}

CallbackReturn AssemInterface::on_init(const hardware_interface::HardwareInfo &hardware_info)
{
  if (hardware_interface::SystemInterface::on_init(hardware_info) != CallbackReturn::SUCCESS) {
    return CallbackReturn::FAILURE;
  }

  try {
    port_ = info_.hardware_parameters.at("port");
  } catch (const std::out_of_range &e) {
    RCLCPP_FATAL(rclcpp::get_logger("AssemInterface"), "No Serial Port provided!");
    return CallbackReturn::FAILURE;
  }

  // ضبط المصفوفات لتناسب مفصلي الروبوت (joint_1, joint_2)
  position_commands_.assign(info_.joints.size(), 0.0);
  position_states_.assign(info_.joints.size(), 0.0);
  prev_position_commands_.assign(info_.joints.size(), 0.0);

  return CallbackReturn::SUCCESS;
}

std::vector<hardware_interface::StateInterface> AssemInterface::export_state_interfaces()
{
  std::vector<hardware_interface::StateInterface> state_interfaces;
  for (size_t i = 0; i < info_.joints.size(); i++) {
    state_interfaces.emplace_back(hardware_interface::StateInterface(
        info_.joints[i].name, hardware_interface::HW_IF_POSITION, &position_states_[i]));
  }
  return state_interfaces;
}

std::vector<hardware_interface::CommandInterface> AssemInterface::export_command_interfaces()
{
  std::vector<hardware_interface::CommandInterface> command_interfaces;
  for (size_t i = 0; i < info_.joints.size(); i++) {
    command_interfaces.emplace_back(hardware_interface::CommandInterface(
        info_.joints[i].name, hardware_interface::HW_IF_POSITION, &position_commands_[i]));
  }
  return command_interfaces;
}

CallbackReturn AssemInterface::on_activate(const rclcpp_lifecycle::State & /*previous_state*/)
{
  RCLCPP_INFO(rclcpp::get_logger("AssemInterface"), "Activating Hardware...");
  try {
    arduino_.Open(port_);
    arduino_.SetBaudRate(LibSerial::BaudRate::BAUD_115200);
  } catch (...) {
    RCLCPP_FATAL(rclcpp::get_logger("AssemInterface"), "Serial Connection Failed!");
    return CallbackReturn::FAILURE;
  }
  return CallbackReturn::SUCCESS;
}

CallbackReturn AssemInterface::on_deactivate(const rclcpp_lifecycle::State & /*previous_state*/)
{
  if (arduino_.IsOpen()) arduino_.Close();
  return CallbackReturn::SUCCESS;
}

hardware_interface::return_type AssemInterface::read(const rclcpp::Time & /*time*/, const rclcpp::Duration & /*period*/)
{
  position_states_ = position_commands_; // Open loop
  return hardware_interface::return_type::OK;
}

hardware_interface::return_type AssemInterface::write(const rclcpp::Time & /*time*/, const rclcpp::Duration & /*period*/)
{
  if (position_commands_ == prev_position_commands_) return hardware_interface::return_type::OK;

  std::string msg = "";
  // Joint 1
  int j1 = static_cast<int>((position_commands_.at(0) * 180.0 / M_PI) + 90.0);
  msg += "b" + compensateZeros(j1) + std::to_string(j1) + ",";
  
  // Joint 2
  int j2 = static_cast<int>((position_commands_.at(1) * 180.0 / M_PI) + 90.0);
  msg += "s" + compensateZeros(j2) + std::to_string(j2) + "\n";

  try {
    arduino_.Write(msg);
    prev_position_commands_ = position_commands_;
  } catch (...) {
    return hardware_interface::return_type::ERROR;
  }
  return hardware_interface::return_type::OK;
}
} 

PLUGINLIB_EXPORT_CLASS(assem_controller::AssemInterface, hardware_interface::SystemInterface)