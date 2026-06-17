/**
 * Orbbec 相机帧捕获程序
 * 从 Orbbec 相机捕获 MJPG 帧，解码为 BGR，通过 stdout 输出原始像素数据。
 * 输出格式（每帧）：
 *   uint32_t width        (4 bytes, little-endian)
 *   uint32_t height       (4 bytes, little-endian)
 *   uint8_t  data[width*height*3]  (BGR pixels)
 */
#include "libobsensor/ObSensor.hpp"

// C API - 用于关闭 SDK 的 stdout 日志输出
#include "libobsensor/h/Context.h"

#include <opencv2/core.hpp>
#include <opencv2/imgcodecs.hpp>
#include <iostream>
#include <vector>
#include <cstdint>

int main() {
    // 关闭 Orbbec SDK 的 stdout 日志输出，避免污染二进制数据流
    ob_set_logger_to_console(OB_LOG_SEVERITY_OFF, nullptr);

    ob::Pipeline pipe;
    try {
        auto config = std::make_shared<ob::Config>();
        config->enableVideoStream(OB_STREAM_COLOR, 640, 480, 30, OB_FORMAT_MJPG);
        pipe.start(config);
    } catch (const std::exception& e) {
        std::cerr << "Pipeline 启动失败: " << e.what() << std::endl;
        return 1;
    }

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

        // 写宽高 + 像素数据到 stdout
        std::cout.write(reinterpret_cast<const char*>(&w), sizeof(w));
        std::cout.write(reinterpret_cast<const char*>(&h), sizeof(h));
        std::cout.write(reinterpret_cast<const char*>(bgr.data), w * h * 3);
        std::cout.flush();
    }

    return 0;
}
