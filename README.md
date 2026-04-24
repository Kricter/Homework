📄 README.md 

# ROS 2 小海龟智能化控制实验

本项目实现了对 `turtlesim` 小海龟的高级自动化控制。核心亮点在于实现了**精准的 180° 原路返航逻辑**，并通过服务接口支持运动模式的动态切换。

## 🛠️ 环境准备

本项目依赖 ROS 2 标准服务接口 `std_srvs`。若未安装请执行：
```bash
sudo apt update
sudo apt install ros-$ROS_DISTRO-std-srvs
```

## 🚀 核心功能与操作指南

### 1. 编译项目 (关键步骤)
修改代码或配置文件后，必须回到工作空间根目录进行编译，否则修改不会生效：
```bash
cd ~/ros2_ws
colcon build --packages-select my_first_package
```

### 2. 启动仿真主程序
主程序启动后将自动从 YAML 加载速度参数，并默认进入 **精准往返模式**：
```bash
# 每一个新打开的终端都必须执行 source
source install/setup.bash
ros2 launch my_first_package homework.launch.py
```
* **模式 0 (默认状态)**：海龟保持直行。当探测到墙壁边界时，海龟将**原地旋转 180°**，随后根据记录的里程**原路返回**。回到出发点后，海龟将**自动进入静止状态**。

### 3. 运行自定义遥控器
打开**第二个终端**，执行以下命令开启人工干预模式：
```bash
cd ~/ros2_ws
source install/setup.bash
ros2 run my_first_package my_teleop.py
```

## 🎮 遥控器按键映射表

| 按键 | 功能说明 |
| :--- | :--- |
| **W / S** | **线速度控制**：增加或减小前进/后退速度（累加式，按一次加一次速） |
| **A / D** | **角速度控制**：控制海龟左转或右转 |
| **Space (空格)** | **紧急刹车**：瞬间停止所有运动指令 |
| **数字键 1** | **进入花活模式**：海龟将循环执行“正弦波”与“方波”轨迹（每 10 秒自动轮换一次） |
| **数字键 0** | **重置往返模式**：清空里程记录，重新开始“出发-掉头-返航-停止”流程 |
| **Q** | **退出**：关闭遥控节点 |

## ⚠️ 开发与运行避坑指南

1.  **环境变量 (Source)**：这是 ROS 2 最容易出错的地方。记住：**新开终端必 source**。如果没有执行 `source install/setup.bash`，系统将无法识别 `my_first_package`。
2.  **原地静止现象**：如果运行后海龟不动，通常是因为它处于“精准返航”结束后的 `STOP` 状态。此时只需在遥控器按 `W` 或按 `1` 切换模式即可使其重新运动。
3.  **参数实时性**：修改 `config/turtle_config.yaml` 后，必须重新执行 `colcon build` 才能将新的参数同步到运行环境中。

---

### 📂 项目目录说明
* **turtle_controller.py**: 算法核心。包含状态机逻辑（FORWARD -> TURN180 -> BACKWARD -> STOP）。
* **my_teleop.py**: 交互核心。实现键盘监听与 `SetBool` 服务调用。
* **homework.launch.py**: 节点管理器。负责同时拉起海龟仿真器、控制器并加载参数。


