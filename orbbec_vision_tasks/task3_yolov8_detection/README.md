# TASK3: YOLOv8n 目标检测

## 编译桥接程序
```bash
g++ -std=c++11 orbbec_capture.cpp \
    -I<OrbbecSDK>/include -L<OrbbecSDK>/lib \
    $(pkg-config --cflags --libs opencv4) -lOrbbecSDK -o orbbec_capture
```

## 运行
```bash
export LD_LIBRARY_PATH=<OrbbecSDK>/lib:$LD_LIBRARY_PATH
python3 yolo_detect.py
```

## 操作
- ESC: 退出
- 空格: 截图保存到 custom_train/images/train/
