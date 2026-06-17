"""
离线数据增强 - 将 40 张训练图片扩充到 440 张
自动调整 YOLO 标签的 bbox 坐标
"""
import os
import cv2
import numpy as np
import random
import glob
import albumentations as A

BASE = os.path.dirname(os.path.abspath(__file__))
TRAIN_IMG = os.path.join(BASE, "images/train")
TRAIN_LBL = os.path.join(BASE, "labels/train")

AUG_IMG = os.path.join(BASE, "images/aug_train")
AUG_LBL = os.path.join(BASE, "labels/aug_train")

os.makedirs(AUG_IMG, exist_ok=True)
os.makedirs(AUG_LBL, exist_ok=True)

# 先把原图复制到增强目录
for f in glob.glob(os.path.join(TRAIN_IMG, "*.jpg")):
    base = os.path.basename(f)
    lbl = os.path.join(TRAIN_LBL, base.replace(".jpg", ".txt"))
    if os.path.exists(lbl):
        os.system(f"cp '{f}' '{AUG_IMG}/{base}'")
        os.system(f"cp '{lbl}' '{AUG_LBL}/{base.replace('.jpg', '.txt')}'")

originals = sorted(glob.glob(os.path.join(TRAIN_IMG, "*.jpg")))
print(f"原图数量: {len(originals)}")

# ===== 增强流水线 =====
# 针对透明物体的增强策略：
# - 旋转+透视（模拟不同角度）
# - 亮度/对比度变化（模拟不同光照）
# - 高斯噪声+模糊（模拟摄像头噪声）
# - 随机色调/饱和度变化

aug_pipeline = A.Compose([
    A.Rotate(limit=30, p=0.8, border_mode=cv2.BORDER_CONSTANT),
    A.Perspective(scale=(0.03, 0.08), fit_output=True, p=0.4),
    A.RandomBrightnessContrast(brightness_limit=0.3, contrast_limit=0.3, p=0.8),
    A.HueSaturationValue(hue_shift_limit=10, sat_shift_limit=30, val_shift_limit=20, p=0.6),
    A.GaussNoise(var_limit=(5, 30), p=0.4),
    A.GaussianBlur(blur_limit=(3, 5), p=0.3),
    A.RandomGamma(gamma_limit=(80, 120), p=0.4),
    A.CLAHE(clip_limit=2, tile_grid_size=(8, 8), p=0.3),
], bbox_params=A.BboxParams(
    format="yolo",
    min_visibility=0.3,   # bbox可见区域低于30%则丢弃
    label_fields=["class_labels"],
))

idx = 0
for img_path in originals:
    base = os.path.basename(img_path)
    stem = os.path.splitext(base)[0]
    lbl_path = os.path.join(TRAIN_LBL, stem + ".txt")

    if not os.path.exists(lbl_path):
        continue

    # 读取图片
    image = cv2.imread(img_path)
    if image is None:
        continue
    h, w = image.shape[:2]

    # 读取 YOLO 标签
    with open(lbl_path) as f:
        lines = f.read().strip().splitlines()

    bboxes = []
    class_labels = []
    for line in lines:
        parts = line.strip().split()
        if len(parts) == 5:
            cls_id = int(parts[0])
            xc, yc, bw, bh = map(float, parts[1:])
            bboxes.append([xc, yc, bw, bh])
            class_labels.append(cls_id)

    if not bboxes:
        continue

    # 每张原图生成 10 张增强图
    for aug_idx in range(10):
        try:
            augmented = aug_pipeline(image=image, bboxes=bboxes, class_labels=class_labels)
            aug_img = augmented["image"]
            aug_bboxes = augmented["bboxes"]
            aug_classes = augmented["class_labels"]
        except Exception as e:
            continue

        if len(aug_bboxes) == 0:
            continue

        # 保存增强图片
        aug_name = f"{stem}_aug{aug_idx:02d}.jpg"
        aug_img_path = os.path.join(AUG_IMG, aug_name)
        cv2.imwrite(aug_img_path, aug_img)

        # 保存增强标签
        aug_lbl_path = os.path.join(AUG_LBL, aug_name.replace(".jpg", ".txt"))
        with open(aug_lbl_path, "w") as f:
            for cls_id, bbox in zip(aug_classes, aug_bboxes):
                xc, yc, bw, bh = bbox
                f.write(f"{cls_id} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}\n")

        idx += 1

total = len(originals) + idx
print(f"增强后: 原图 {len(originals)} + 增强 {idx} = {total} 张训练图片")
print(f"增强图片保存在: {AUG_IMG}")
