"""
交互打标工具 - 鼠标画框自动保存 YOLO 格式
操作: 鼠标拖动画框 | N=下一张 | U=撤销 | Q=退出
"""
import cv2
import os
import glob

IMG_DIR = "images/train"
LBL_DIR = "labels/train"
CLASS_NAME = "earphone_box"  # 类别名

os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(LBL_DIR, exist_ok=True)

images = sorted(glob.glob(os.path.join(IMG_DIR, "*.jpg")))
if not images:
    print(f"没有图片在 {IMG_DIR}/")
    exit()

print(f"共 {len(images)} 张图片，开始打标")
print("操作: [鼠标拖动画框] [N=下一张] [U=撤销] [Q=退出]")

idx = 0
while idx < len(images):
    img_path = images[idx]
    base = os.path.basename(img_path)
    stem = os.path.splitext(base)[0]
    lbl_path = os.path.join(LBL_DIR, stem + ".txt")

    img = cv2.imread(img_path)
    if img is None:
        idx += 1
        continue
    h, w = img.shape[:2]

    # 检查是否已有标签
    bboxes = []
    if os.path.exists(lbl_path):
        with open(lbl_path) as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 5:
                    xc, yc, bw, bh = map(float, parts[1:])
                    # 转回像素坐标
                    x1 = int((xc - bw/2) * w)
                    y1 = int((yc - bh/2) * h)
                    x2 = int((xc + bw/2) * w)
                    y2 = int((yc + bh/2) * h)
                    bboxes.append([x1, y1, x2, y2])

    drawing = False
    ix, iy = -1, -1
    temp_box = None

    def mouse_callback(event, x, y, flags, param):
        nonlocal ix, iy, drawing, temp_box
        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            ix, iy = x, y
        elif event == cv2.EVENT_MOUSEMOVE and drawing:
            temp_box = (ix, iy, x, y)
        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            x1, y1 = min(ix, x), min(iy, y)
            x2, y2 = max(ix, x), max(iy, y)
            if x2 - x1 > 10 and y2 - y1 > 10:
                bboxes.append([x1, y1, x2, y2])
                print(f"  [{stem}] 添加框 ({x1},{y1})-({x2},{y2})")
            temp_box = None

    cv2.namedWindow(f"Label: {base}")
    cv2.setMouseCallback(f"Label: {base}", mouse_callback)

    while True:
        display = img.copy()
        for bbox in bboxes:
            cv2.rectangle(display, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)

        if temp_box:
            x1, y1, x2, y2 = temp_box
            cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 255), 1)

        info = f"[{idx+1}/{len(images)}] {base} 框数:{len(bboxes)}"
        cv2.putText(display, info, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.imshow(f"Label: {base}", display)

        key = cv2.waitKey(10) & 0xFF
        if key == ord('n') or key == 13:  # N 或 Enter → 保存并下一张
            # 保存 YOLO 格式标签
            with open(lbl_path, "w") as f:
                for bbox in bboxes:
                    x1, y1, x2, y2 = bbox
                    xc = ((x1 + x2) / 2) / w
                    yc = ((y1 + y2) / 2) / h
                    bw_ = (x2 - x1) / w
                    bh_ = (y2 - y1) / h
                    f.write(f"0 {xc:.6f} {yc:.6f} {bw_:.6f} {bh_:.6f}\n")
            print(f"  已保存: {lbl_path}")
            idx += 1
            break
        elif key == ord('u'):  # U → 撤销最后一个框
            if bboxes:
                bboxes.pop()
                print(f"  撤销一个框，剩余 {len(bboxes)}")
        elif key == ord('q') or key == 27:  # Q 或 ESC → 退出
            idx = len(images)
            break

    cv2.destroyWindow(f"Label: {base}")

print("打标完成！")
