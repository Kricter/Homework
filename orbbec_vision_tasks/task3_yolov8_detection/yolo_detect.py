"""
YOLOv8n 实时目标检测 - 使用 Orbbec 相机
通过 orbbec_capture C++ 程序获取帧数据
"""
import cv2
import numpy as np
import struct
import subprocess
import time
import os
from ultralytics import YOLO

# Orbbec SDK 库路径
ORBBEC_LIB_DIR = os.path.expanduser(
    "~/下载/OrbbecSDK_C_C++_v1.10.27_20250925_0549823_linux_x64_release"
    "/OrbbecSDK_v1.10.27/SDK/lib"
)


def frame_generator(proc):
    """从 orbbec_capture stdout 读取帧"""
    while True:
        # 读宽高 (8 bytes)
        header = proc.stdout.read(8)
        if not header or len(header) < 8:
            break
        w, h = struct.unpack("<II", header)
        # 读像素数据
        raw = proc.stdout.read(w * h * 3)
        if not raw or len(raw) < w * h * 3:
            break
        yield np.frombuffer(raw, dtype=np.uint8).reshape(h, w, 3).copy()


def main():
    # 加载自定义模型
    MODEL_PATH = os.path.join(os.path.dirname(__file__),
        "custom_train/runs/detect/train-4/weights/best.pt")
    model = YOLO(MODEL_PATH)
    print(f"模型加载完成，设备: {model.device}")
    print(f"模型: {MODEL_PATH}")

    # 启动 C++ 捕获程序
    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = f"{ORBBEC_LIB_DIR}:{env.get('LD_LIBRARY_PATH', '')}"

    capture_path = os.path.join(os.path.dirname(__file__), "orbbec_capture")
    proc = subprocess.Popen(
        [capture_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    print("Orbbec 相机已启动")

    # 自定义模型: earphone_box
    # 置信度阈值 0.90（螺丝帽等误检被过滤）
    CONF_THRESHOLD = 0.90

    # 截图保存目录
    SAVE_DIR = os.path.join(os.path.dirname(__file__), "custom_train", "images", "train")
    os.makedirs(SAVE_DIR, exist_ok=True)
    saved_count = len([f for f in os.listdir(SAVE_DIR) if f.endswith(".jpg")])

    print(f"按 ESC 退出 | 按 空格 截图保存到 {SAVE_DIR}")

    try:
        for frame in frame_generator(proc):
            t_start = time.time()

            # YOLOv8 推理（带置信度过滤）
            results = model(frame, verbose=False, conf=CONF_THRESHOLD)[0]

            # 绘制检测框
            for box in results.boxes:
                conf = float(box.conf[0])

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                label = f"earphone_box {conf:.2f}"

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # FPS 和检测信息
            fps = 1.0 / (time.time() - t_start)
            cv2.putText(frame, f"FPS: {fps:.1f} | earphone_box", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            cv2.imshow("earphone_box Detection", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break
            elif key == ord('a'):  # A 键切换显示模式
                TARGET_CLASSES = None if TARGET_CLASSES is not None else [32]
                print(f"切换为: {'all classes' if TARGET_CLASSES is None else 'ball only'}")
            elif key == 32:  # 空格截图
                saved_count += 1
                filename = f"earphone_{saved_count:03d}.jpg"
                filepath = os.path.join(SAVE_DIR, filename)
                cv2.imwrite(filepath, frame)
                print(f"已保存: {filename}")

    except BrokenPipeError:
        print("捕获程序已断开")
    finally:
        proc.kill()
        proc.wait()
        cv2.destroyAllWindows()

    # 检查 stderr 是否有错误
    err = proc.stderr.read().decode()
    if err:
        print("捕获程序 stderr:", err)


if __name__ == "__main__":
    main()
