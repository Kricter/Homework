# TASK2: 二维码识别

## 编译
```bash
mkdir build && cd build
cmake .. && make -j
```

## 运行
```bash
export LD_LIBRARY_PATH=<OrbbecSDK>/lib:$LD_LIBRARY_PATH
cd build && ./qr_scanner
```

## 说明
- 使用 WeChatQRCode 识别（需要 4 个模型文件在 wechat_qrcode_models/ 目录）
- OpenCV 4.5.4 系统包自带的 QRCodeDetector 缺 quirc 解码器，无法解码
