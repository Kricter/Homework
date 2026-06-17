"""
微调 YOLOv8n v2 - 自定义水瓶检测
V2: 解除冻结层 + 更多增强 + 更大 patience
"""
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

results = model.train(
    data="dataset.yaml",
    epochs=300,
    patience=50,                 # 50轮没提升才停止
    batch=16,                    # 利用RTX4060显存，加大batch
    imgsz=640,
    device="0",
    workers=4,
    lr0=0.005,                   # 初始学习率稍高（因为没有冻结层了）
    lrf=0.01,                    # 最终学习率
    augment=True,
    cos_lr=True,
    # 不再冻结层，让所有参数适应新任务
    # freeze=0,
    # 针对透明物体的增强
    hsv_h=0.05,                  # 色调变化
    hsv_s=0.7,                   # 饱和度变化（对透明瓶有帮助）
    hsv_v=0.4,                   # 明度变化
    scale=1.0,                   # 缩放
    fliplr=0.5,                  # 水平翻转
    mosaic=0.5,                  # 马赛克增强（减半防止小数据集过拟合）
    mixup=0.2,                   # 混合增强
    copy_paste=0.2,              # 复制粘贴增强（对单类检测有帮助）
    erasing=0.2,                 # 随机擦除（提高鲁棒性）
    verbose=True,
)

# 验证
metrics = model.val()
print(f"\n最终指标:")
print(f"  Precision:  {metrics.box.p:.3f}")
print(f"  Recall:     {metrics.box.r:.3f}")
print(f"  mAP50:      {metrics.box.map50:.3f}")
print(f"  mAP50-95:   {metrics.box.map:.3f}")

model.export(format="onnx", imgsz=640)
print(f"\n模型保存: runs/detect/train2/weights/best.pt")
