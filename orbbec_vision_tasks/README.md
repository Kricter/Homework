# Orbbec Astra Pro Plus 视觉任务合集

基于 Orbbec Astra Pro Plus 深度相机的五个视觉任务实现。

---

## 任务总览

| 任务 | 内容 | 关键技术 | 状态 |
|------|------|---------|------|
| TASK1 | 深度相机驱动部署 | Orbbec SDK, USB3 | ✅ |
| TASK2 | 二维码识别 | OpenCV QRCodeDetector + WeChatQRCode | ✅ |
| TASK3 | YOLOv8n 目标检测 | YOLOv8n, COCO 预训练 | ✅ |
| TASK4 | 自定义物体训练 | YOLOv8n 微调, 数据增强 | ✅ 93%+ |
| TASK5 | 深度信息 + 3D 坐标 | RGB-D, D2C, 相机内参 | ✅ |

---

## 目录结构

```
orbbec_vision_tasks/
├── task1_depth_driver/          # 深度相机驱动部署
│   └── list_profiles.cpp        #   枚举相机支持的分辨率/格式
│
├── task2_qr_code/               # 二维码识别
│   ├── qr_scanner.cpp           #   主程序（WeChatQRCode）
│   ├── CMakeLists.txt           #   编译配置
│   └── wechat_qrcode_models/    #   WeChatQRCode 模型文件
│
├── task3_yolov8_detection/      # YOLOv8n 目标检测
│   ├── yolo_detect.py           #   主程序（实时检测 + 截图）
│   └── orbbec_capture.cpp       #   C++ 桥接（Orbbec → stdout）
│
├── task4_custom_training/       # 自定义物体训练
│   ├── dataset/                 #   数据集配置
│   │   ├── dataset.yaml
│   │   ├── dataset_aug.yaml
│   │   └── classes.txt
│   ├── scripts/                 #   训练脚本
│   │   ├── train.py             #     v1 基础训练
│   │   ├── train_v2.py          #     v2 增强版
│   │   ├── train_v3.py          #     v3 离线增强版
│   │   ├── augment.py           #     离线数据增强
│   │   └── label_tool.py        #     交互打标工具
│   └── trained_model.pt         #   训练好的模型 (93%+)
│
├── task5_depth_coordinates/     # 深度信息 + 3D 坐标
│   ├── yolo_rgbd_detect.py      #   主程序（检测 + 坐标）
│   └── orbbec_rgbd_capture.cpp  #   C++ 桥接（RGB + 深度）
│
└── assets/                      # 共享资源
    └── yolov8n.pt               #   COCO 预训练权重
```

---

## 环境依赖

### 硬件
- Orbbec Astra Pro Plus 深度相机
- USB 3.0 线材（深度数据必须 USB3）
- NVIDIA GPU (RTX 4060 测试通过)

### 软件
| 依赖 | 版本 |
|------|------|
| Orbbec SDK | v1.10.27 |
| OpenCV | 4.5.4+ (C++), 4.13.0 (Python) |
| PyTorch | 2.6.0+ |
| CUDA | 12.4 |
| ultralytics | 8.4.61 |
| Python | 3.9 |

---

## 快速开始

### 编译 C++ 程序
```bash
# 设置 Orbbec SDK 路径
export ORBBEC_SDK="/path/to/OrbbecSDK_v1.10.27/SDK"
export LD_LIBRARY_PATH="${ORBBEC_SDK}/lib:$LD_LIBRARY_PATH"

# QR 扫描器
cd task2_qr_code
mkdir build && cd build
cmake .. && make -j

# RGB 捕获桥接
cd ../../task3_yolov8_detection
g++ -std=c++11 orbbec_capture.cpp \
    -I${ORBBEC_SDK}/include -L${ORBBEC_SDK}/lib \
    $(pkg-config --cflags --libs opencv4) -lOrbbecSDK -o orbbec_capture

# RGB-D 捕获桥接（需要 OpenCV imgcodecs）
cd ../../task5_depth_coordinates
g++ -std=c++11 orbbec_rgbd_capture.cpp \
    -I${ORBBEC_SDK}/include -L${ORBBEC_SDK}/lib \
    $(pkg-config --cflags --libs opencv4) -lOrbbecSDK -o orbbec_rgbd_capture
```

### 运行 Python 程序
```bash
# TASK3: YOLOv8n 实时检测（空格截图）
cd task3_yolov8_detection
python3 yolo_detect.py

# TASK5: RGB-D 检测 + 3D 坐标
cd ../task5_depth_coordinates
python3 yolo_rgbd_detect.py

# TASK4: 重新训练
cd ../task4_custom_training/scripts
python3 augment.py        # 数据增强
python3 train_v3.py       # 训练
```

---

## 各任务说明

### TASK1: 深度相机驱动
使用 Orbbec SDK v1.10.27 驱动 Astra Pro Plus。
关键：深度流须使用 USB 3.0 接口，否则无法获取深度数据。

### TASK2: 二维码识别
采用 WeChatQRCode（opencv_contrib 模块）替代内置 QRCodeDetector，
识别率远高于 OpenCV 4.5.4 自带的解码器（Ubuntu 包缺 quirc 依赖）。

### TASK3: YOLOv8n 目标检测
使用 COCO 预训练 YOLOv8n，检测 "sports ball" (class 32)。
通过 C++ 桥接程序读取 Orbbec 相机，pipe 到 Python 进行推理。

### TASK4: 自定义训练
以耳塞盒（earphone_box）为训练目标：
1. 拍摄 40 张照片 → 数据增强至 440 张
2. label_tool.py 交互打标
3. YOLOv8n 微调，最终置信度 93%+
4. 螺丝帽负样本被 0.70 阈值过滤

### TASK5: 深度 + 3D 坐标
D2C (Depth-to-Color) 硬件对齐，获取 640x480 对齐深度图。
通过相机内参计算 3D 坐标 (X, Y, Z)，单位米。
