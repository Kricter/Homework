"""
YOLOv8n 实时目标检测 + 深度信息 → 相机坐标系 3D 坐标
使用 Orbbec 相机的 RGB + 原始深度流
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


def depth_to_xyz(u, v, depth_mm, fx, fy, cx, cy):
    """将像素坐标 (u,v) + 深度值 (mm) 转为 3D 坐标 (m)"""
    if depth_mm <= 0:
        return None
    z = depth_mm / 1000.0
    x = (u - cx) * z / fx
    y = (v - cy) * z / fy
    return (x, y, z)


def find_depth(depth_map, cu, cv_, search_r=15):
    """在 (cu,cv_) 附近搜索有效深度值，取中位数"""
    h, w = depth_map.shape
    u0, u1 = max(0, cu - search_r), min(w, cu + search_r + 1)
    v0, v1 = max(0, cv_ - search_r), min(h, cv_ + search_r + 1)
    patch = depth_map[v0:v1, u0:u1]
    valid = patch[patch > 0]
    if len(valid) == 0:
        return 0.0
    return float(np.median(valid))


def frame_generator(proc):
    """从 orbbec_rgbd_capture stdout 读取帧"""
    # 彩色内参 (16B)
    raw = proc.stdout.read(16)
    cfx, cfy, ccx, ccy = struct.unpack("ffff", raw)
    # 深度内参 (16B)
    raw = proc.stdout.read(16)
    dfx, dfy, dcx, dcy = struct.unpack("ffff", raw)
    # 外参: 旋转9 + 平移3 (48B)
    raw = proc.stdout.read(48)
    rot = struct.unpack("9f", raw[:36])
    trans = struct.unpack("3f", raw[36:48])

    yield {
        "type": "intrinsics",
        "cfx": cfx, "cfy": cfy, "ccx": ccx, "ccy": ccy,
        "dfx": dfx, "dfy": dfy, "dcx": dcx, "dcy": dcy,
        "rot": rot, "trans": trans,
    }

    while True:
        header = proc.stdout.read(8)
        if not header or len(header) < 8:
            break
        w, h = struct.unpack("<II", header)
        rgb_raw = proc.stdout.read(w * h * 3)
        if not rgb_raw or len(rgb_raw) < w * h * 3:
            break
        rgb = np.frombuffer(rgb_raw, dtype=np.uint8).reshape(h, w, 3).copy()

        dheader = proc.stdout.read(8)
        if not dheader or len(dheader) < 8:
            break
        dw, dh = struct.unpack("<II", dheader)
        d_raw = proc.stdout.read(dw * dh * 2)
        if not d_raw or len(d_raw) < dw * dh * 2:
            break
        depth = np.frombuffer(d_raw, dtype=np.uint16).reshape(dh, dw).copy()

        yield {"type": "frame", "rgb": rgb, "depth": depth}


def main():
    MODEL_PATH = os.path.join(os.path.dirname(__file__),
        "custom_train/runs/detect/train-4/weights/best.pt")
    model = YOLO(MODEL_PATH)
    print(f"模型加载完成，设备: {model.device}")

    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = f"{ORBBEC_LIB_DIR}:{env.get('LD_LIBRARY_PATH', '')}"

    capture_path = os.path.join(os.path.dirname(__file__), "orbbec_rgbd_capture")
    proc = subprocess.Popen(
        [capture_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )

    CONF_THRESHOLD = 0.90  # 检测置信度阈值
    intrinsics = None

    print("按 ESC 退出")

    try:
        for item in frame_generator(proc):
            if item["type"] == "intrinsics":
                intrinsics = item
                print(f"彩色内参: fx={intrinsics['cfx']:.2f} fy={intrinsics['cfy']:.2f} "
                      f"cx={intrinsics['ccx']:.2f} cy={intrinsics['ccy']:.2f}")
                print(f"深度内参: fx={intrinsics['dfx']:.2f} fy={intrinsics['dfy']:.2f} "
                      f"cx={intrinsics['dcx']:.2f} cy={intrinsics['dcy']:.2f}")
                continue

            frame = item["rgb"]
            depth_map = item["depth"]

            # 使用深度内参
            dfx = intrinsics["dfx"]
            dfy = intrinsics["dfy"]
            dcx = intrinsics["dcx"]
            dcy = intrinsics["dcy"]

            t_start = time.time()

            results = model(frame, verbose=False, conf=CONF_THRESHOLD)[0]

            for box in results.boxes:
                conf = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                cu = (x1 + x2) // 2
                cv_ = (y1 + y2) // 2

                # 渐进式搜索深度：从小半径到大半径
                d_mm = 0.0
                for r in [10, 20, 30, 50]:
                    d = find_depth(depth_map, cu, cv_, search_r=r)
                    if d > 0:
                        d_mm = d
                        break
                # 如果中心区域无深度，尝试在 bbox 边缘（背景区域）搜索
                if d_mm == 0.0:
                    for ex, ey in [(x1, y1), (x2, y2), (x1, y2), (x2, y1),
                                   ((x1+x2)//2, y1), ((x1+x2)//2, y2),
                                   (x1, (y1+y2)//2), (x2, (y1+y2)//2)]:
                        d = find_depth(depth_map, ex, ey, search_r=15)
                        if d > 0:
                            d_mm = d
                            break
                xyz = depth_to_xyz(cu, cv_, d_mm, dfx, dfy, dcx, dcy)

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"earphone_box {conf:.2f}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                if xyz is not None:
                    x3d, y3d, z3d = xyz
                    cv2.putText(frame, f"({x3d:.2f}, {y3d:.2f}, {z3d:.2f})m",
                                (x1, y2 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                    print(f"[earphone_box] ({x3d:.3f}, {y3d:.3f}, {z3d:.3f})m  conf={conf:.2f}")
                else:
                    print(f"[earphone_box] 无有效深度  conf={conf:.2f}")

            fps = 1.0 / (time.time() - t_start)
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            cv2.imshow("earphone_box + Depth", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break

    except BrokenPipeError:
        print("捕获程序已断开")
    finally:
        proc.kill()
        proc.wait()
        cv2.destroyAllWindows()

    err = proc.stderr.read().decode()
    if err:
        print("stderr:", err)


if __name__ == "__main__":
    main()
