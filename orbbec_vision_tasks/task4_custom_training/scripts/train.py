"""
微调 YOLOv8n - 自定义水瓶检测
"""
from ultralytics import YOLO

# 从 COCO 预训练权重开始微调
model = YOLO("yolov8n.pt")

results = model.train(
    data="dataset.yaml",
    epochs=100,                 # 训练轮数
    patience=20,                # 20轮没提升就提前停止
    batch=8,                    # 批次大小
    imgsz=640,                  # 输入图片尺寸
    device="0",                 # 使用 GPU 训练
    workers=2,
    lr0=0.001,                  # 学习率
    augment=True,               # 启用数据增强
    cos_lr=True,                # 余弦退火学习率
    freeze=10,                  # 冻结前10层（加速训练，保留COCO特征）
    verbose=True,
)

# 验证模型
metrics = model.val()
print(f"mAP50: {metrics.box.map50:.3f}")
print(f"mAP50-95: {metrics.box.map:.3f}")

# 导出模型
model.export(format="onnx", imgsz=640)
print("训练完成，模型已导出: runs/detect/train/weights/best.pt")
