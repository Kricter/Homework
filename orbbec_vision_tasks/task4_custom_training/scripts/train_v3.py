"""
YOLOv8n 训练 v3 - 使用增强后的 440 张图片
"""
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

results = model.train(
    data="dataset_aug.yaml",
    epochs=200,
    patience=30,
    batch=32,                    # 440张图，batch可以大一些
    imgsz=640,
    device="0",
    workers=4,
    lr0=0.001,
    lrf=0.01,
    cos_lr=True,
    # 不再冻结
    # 轻量在线增强 (增强数据本身已经变异过了)
    hsv_h=0.015,
    hsv_s=0.3,
    hsv_v=0.2,
    fliplr=0.5,
    scale=0.3,
    verbose=True,
    close_mosaic=10,
)

metrics = model.val()
print(f"\n最终指标:")
print(f"  Precision:  {metrics.box.p:.3f}")
print(f"  Recall:     {metrics.box.r:.3f}")
print(f"  mAP50:      {metrics.box.map50:.3f}")
print(f"  mAP50-95:   {metrics.box.map:.3f}")

model.export(format="onnx", imgsz=640)
print(f"\n模型保存: runs/detect/train3/weights/best.pt")
