"""
YOLOv8n-seg 实时语义分割 - 桌面物体分割
使用 Orbbec 相机 + COCO 预训练分割模型
"""
import cv2
import numpy as np
import struct
import subprocess
import time
import os
from ultralytics import YOLO

ORBBEC_LIB_DIR = os.path.expanduser(
    "~/下载/OrbbecSDK_C_C++_v1.10.27_20250925_0549823_linux_x64_release"
    "/OrbbecSDK_v1.10.27/SDK/lib"
)

# 常见桌面物体的 COCO 类号
DESKTOP_CLASSES = {
    39: "bottle",
    41: "cup",
    47: "apple",
    49: "orange",
    56: "chair",
    62: "tv",
    63: "laptop",
    64: "mouse",
    65: "remote",
    67: "cell phone",
    73: "book",
    74: "clock",
    75: "vase",
    76: "scissors",
}


def frame_generator(proc):
    while True:
        header = proc.stdout.read(8)
        if not header or len(header) < 8:
            break
        w, h = struct.unpack("<II", header)
        raw = proc.stdout.read(w * h * 3)
        if not raw or len(raw) < w * h * 3:
            break
        yield np.frombuffer(raw, dtype=np.uint8).reshape(h, w, 3).copy()


def main():
    model_path = os.path.join(os.path.dirname(__file__), "..", "assets", "yolov8n-seg.pt")
    model = YOLO(model_path)
    print(f"模型加载完成，设备: {model.device}")

    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = f"{ORBBEC_LIB_DIR}:{env.get('LD_LIBRARY_PATH', '')}"

    capture_path = os.path.join(os.path.dirname(__file__), "orbbec_capture")
    if not os.path.exists(capture_path):
        capture_path = os.path.join(os.path.dirname(__file__), "..", "task3_yolov8_detection", "orbbec_capture")
    proc = subprocess.Popen([capture_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    print("Orbbec 相机已启动，ESC 退出")

    np.random.seed(42)
    colors = {c: tuple(np.random.randint(0, 255, 3).tolist()) for c in DESKTOP_CLASSES}

    try:
        for frame in frame_generator(proc):
            t_start = time.time()

            # YOLOv8-seg 推理
            results = model(frame, verbose=False, conf=0.3)[0]

            if results.masks is not None:
                for mask, box, cls_id in zip(results.masks.xy, results.boxes.xyxy, results.boxes.cls):
                    cls_id = int(cls_id)
                    conf = float(results.boxes.conf[list(results.boxes.cls).index(cls_id)] if len(results.boxes) > 1 else results.boxes.conf[0])

                    # 只在有对应 class 时才显示
                    if cls_id in DESKTOP_CLASSES:
                        # 画轮廓
                        contour = mask.astype(np.int32).reshape((-1, 1, 2))
                        cv2.polylines(frame, [contour], True, colors[cls_id], 2)

                        # 画半透明填充
                        overlay = frame.copy()
                        cv2.fillPoly(overlay, [contour], colors[cls_id])
                        frame = cv2.addWeighted(overlay, 0.3, frame, 0.7, 0)

                        # 标签
                        x1, y1, _, _ = map(int, box[:4])
                        label = f"{DESKTOP_CLASSES[cls_id]} {conf:.2f}"
                        cv2.putText(frame, label, (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors[cls_id], 2)

            fps = 1.0 / (time.time() - t_start)
            cv2.putText(frame, f"FPS: {fps:.1f} | YOLOv8n-seg", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            cv2.imshow("Desktop Segmentation", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break

    except BrokenPipeError:
        print("捕获程序已断开")
    finally:
        proc.kill()
        proc.wait()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
