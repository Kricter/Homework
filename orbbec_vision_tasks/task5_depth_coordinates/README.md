# TASK5: 深度信息 + 3D 坐标

## 编译桥接程序
```bash
g++ -std=c++11 orbbec_rgbd_capture.cpp \
    -I<OrbbecSDK>/include -L<OrbbecSDK>/lib \
    $(pkg-config --cflags --libs opencv4) -lOrbbecSDK -o orbbec_rgbd_capture
```

## 运行
```bash
export LD_LIBRARY_PATH=<OrbbecSDK>/lib:$LD_LIBRARY_PATH
python3 yolo_rgbd_detect.py
```

## 原理
- D2C (Depth-to-Color) 硬件对齐，深度映射到彩色坐标系
- 使用彩色内参计算 3D 坐标
- 输出格式: `[earphone_box] (X, Y, Z)m conf=0.94`

## 坐标系
- X: 水平方向（右为正）
- Y: 垂直方向（下为正）
- Z: 深度方向（前为正），单位米
