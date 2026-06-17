/**
 * Orbbec RGB-D 帧捕获程序
 * 输出格式：
 *   1) 初始化: 彩色内参(16B) + 深度内参(16B) = 共 32B
 *   2) 每帧:
 *      uint32_t w, uint32_t h, uint8_t[w*h*3] BGR,
 *      uint32_t dw, uint32_t dh, uint16_t[dw*dh] 深度(mm)
 */
#include "libobsensor/ObSensor.hpp"
#include "libobsensor/h/Context.h"
#include <opencv2/core.hpp>
#include <opencv2/imgcodecs.hpp>
#include <iostream>
#include <vector>
#include <cstdint>

int main() {
    ob_set_logger_to_console(OB_LOG_SEVERITY_OFF, nullptr);

    ob::Pipeline pipe;
    try {
        auto config = std::make_shared<ob::Config>();
        config->enableVideoStream(OB_STREAM_COLOR, 640, 480, 30, OB_FORMAT_MJPG);
        config->enableVideoStream(OB_STREAM_DEPTH, 640, 480, 30, OB_FORMAT_Y11);
        // D2C HW 对齐（深度对齐到彩色坐标系）
        config->setAlignMode(ALIGN_D2C_HW_MODE);
        pipe.start(config);

        // 获取相机内参（彩色 + 深度）
        OBCameraParam camParam = pipe.getCameraParam();

        // 输出彩色内参 (16B)
        float cfx = camParam.rgbIntrinsic.fx;
        float cfy = camParam.rgbIntrinsic.fy;
        float ccx = camParam.rgbIntrinsic.cx;
        float ccy = camParam.rgbIntrinsic.cy;
        std::cout.write(reinterpret_cast<const char*>(&cfx), sizeof(cfx));
        std::cout.write(reinterpret_cast<const char*>(&cfy), sizeof(cfy));
        std::cout.write(reinterpret_cast<const char*>(&ccx), sizeof(ccx));
        std::cout.write(reinterpret_cast<const char*>(&ccy), sizeof(ccy));

        // 输出深度内参 (16B)
        float dfx = camParam.depthIntrinsic.fx;
        float dfy = camParam.depthIntrinsic.fy;
        float dcx = camParam.depthIntrinsic.cx;
        float dcy = camParam.depthIntrinsic.cy;
        std::cout.write(reinterpret_cast<const char*>(&dfx), sizeof(dfx));
        std::cout.write(reinterpret_cast<const char*>(&dfy), sizeof(dfy));
        std::cout.write(reinterpret_cast<const char*>(&dcx), sizeof(dcx));
        std::cout.write(reinterpret_cast<const char*>(&dcy), sizeof(dcy));

        // 输出外参: 旋转矩阵(9 float) + 平移向量(3 float)
        // (从深度坐标系到彩色坐标系的变换)
        const float* rot = camParam.transform.rot;
        const float* trans = camParam.transform.trans;
        for (int i = 0; i < 9; i++) {
            std::cout.write(reinterpret_cast<const char*>(&rot[i]), sizeof(float));
        }
        for (int i = 0; i < 3; i++) {
            std::cout.write(reinterpret_cast<const char*>(&trans[i]), sizeof(float));
        }
        std::cout.flush();

        std::cerr << "[INFO] color: fx=" << cfx << " fy=" << cfy
                  << " cx=" << ccx << " cy=" << ccy << std::endl;
        std::cerr << "[INFO] depth: fx=" << dfx << " fy=" << dfy
                  << " cx=" << dcx << " cy=" << dcy << std::endl;

        while (true) {
            auto frameSet = pipe.waitForFrames(1000);
            if (frameSet == nullptr) continue;

            auto colorFrame = frameSet->colorFrame();
            if (!colorFrame || !colorFrame->data()) continue;

            uint64_t dataSize = colorFrame->dataSize();
            const uint8_t* rawData = static_cast<const uint8_t*>(colorFrame->data());
            std::vector<uint8_t> jpegBuffer(rawData, rawData + dataSize);
            cv::Mat bgr = cv::imdecode(jpegBuffer, cv::IMREAD_COLOR);
            if (bgr.empty()) continue;

            uint32_t w = bgr.cols;
            uint32_t h = bgr.rows;

            auto depthFrame = frameSet->depthFrame();
            if (!depthFrame || !depthFrame->data()) continue;

            uint32_t dw = depthFrame->width();
            uint32_t dh = depthFrame->height();
            uint64_t depthSize = depthFrame->dataSize();
            const uint16_t* depthData = static_cast<const uint16_t*>(depthFrame->data());
            uint32_t pixelCount = depthSize / sizeof(uint16_t);

            std::cout.write(reinterpret_cast<const char*>(&w), sizeof(w));
            std::cout.write(reinterpret_cast<const char*>(&h), sizeof(h));
            std::cout.write(reinterpret_cast<const char*>(bgr.data), w * h * 3);

            std::cout.write(reinterpret_cast<const char*>(&dw), sizeof(dw));
            std::cout.write(reinterpret_cast<const char*>(&dh), sizeof(dh));
            std::cout.write(reinterpret_cast<const char*>(depthData), pixelCount * sizeof(uint16_t));
            std::cout.flush();
        }
    } catch (const ob::Error& e) {
        std::cerr << "[ERROR] Orbbec SDK: " << e.getMessage() << std::endl;
        return 2;
    } catch (const std::exception& e) {
        std::cerr << "[ERROR] " << e.what() << std::endl;
        return 1;
    }
    return 0;
}
