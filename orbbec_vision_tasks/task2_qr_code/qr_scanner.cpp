#include "libobsensor/ObSensor.hpp"
#include <opencv2/opencv.hpp>
#include <opencv2/wechat_qrcode.hpp>
#include <iostream>
#include <sys/stat.h>

// 检查模型文件是否存在
static bool file_exists(const std::string& path) {
    struct stat st;
    return stat(path.c_str(), &st) == 0;
}

int main() {
    // === 模型文件路径 ===
    std::string model_dir = "./wechat_qrcode_models/";
    std::string detect_prototxt = model_dir + "detect.prototxt";
    std::string detect_caffemodel = model_dir + "detect.caffemodel";
    std::string sr_prototxt = model_dir + "sr.prototxt";
    std::string sr_caffemodel = model_dir + "sr.caffemodel";

    // 检查模型文件完整性
    if (!file_exists(detect_prototxt) || !file_exists(detect_caffemodel) ||
        !file_exists(sr_prototxt) || !file_exists(sr_caffemodel)) {
        std::cerr << "错误: WeChatQRCode 模型文件缺失!" << std::endl;
        std::cerr << "请运行: cd wechat_qrcode_models && wget https://github.com/WeChatCV/opencv_3rdparty/raw/wechat_qrcode/{detect.prototxt,detect.caffemodel,sr.prototxt,sr.caffemodel}" << std::endl;
        return -1;
    }

    // === 初始化 Orbbec 相机 ===
    ob::Pipeline pipe;
    try {
        auto config = std::make_shared<ob::Config>();
        config->setColorStreamFormat(OB_FORMAT_MJPG);
        config->setColorStreamResolution(640, 480);
        pipe.start(config);
    } catch (const std::exception& e) {
        std::cerr << "Pipeline 启动失败: " << e.what() << std::endl;
        return -1;
    }

    // === 初始化 WeChatQRCode ===
    // 使用模型文件路径构造，比 QRCodeDetector 识别率更高
    cv::Ptr<cv::wechat_qrcode::WeChatQRCode> detector;
    try {
        detector = cv::makePtr<cv::wechat_qrcode::WeChatQRCode>(
            detect_prototxt, detect_caffemodel,
            sr_prototxt, sr_caffemodel
        );
        std::cout << "WeChatQRCode 初始化成功" << std::endl;
    } catch (const std::exception& e) {
        std::cerr << "WeChatQRCode 初始化失败: " << e.what() << std::endl;
        return -1;
    }

    std::cout << "程序已启动，按 ESC 键退出。" << std::endl;

    while (true) {
        auto frameSet = pipe.waitForFrames(1000);
        if (frameSet == nullptr) {
            std::cerr << "获取帧超时" << std::endl;
            continue;
        }

        auto colorFrame = frameSet->colorFrame();
        if (!colorFrame || !colorFrame->data()) {
            std::cerr << "colorFrame 为空" << std::endl;
            continue;
        }

        uint64_t dataSize = colorFrame->dataSize();
        const uint8_t* rawData = static_cast<const uint8_t*>(colorFrame->data());

        // === MJPG 解码 ===
        std::vector<uint8_t> jpegBuffer(rawData, rawData + dataSize);
        cv::Mat colorMat = cv::imdecode(jpegBuffer, cv::IMREAD_COLOR);

        if (colorMat.empty()) {
            std::cerr << "imdecode 解码失败" << std::endl;
            continue;
        }

        // === WeChatQRCode 检测 ===
        try {
            // detectAndDecode 返回检测到的所有二维码内容
            std::vector<std::string> results = detector->detectAndDecode(colorMat);

            for (const auto& data : results) {
                if (!data.empty()) {
                    std::cout << "检测到二维码: " << data << std::endl;
                    cv::putText(colorMat, data, cv::Point(20, 50),
                                cv::FONT_HERSHEY_SIMPLEX, 1,
                                cv::Scalar(0, 255, 0), 2);
                }
            }
        } catch (const cv::Exception& e) {
            std::cerr << "QR 检测异常: " << e.what() << std::endl;
        }

        cv::imshow("QRCode Scanner", colorMat);

        int key = cv::waitKey(30);
        if (key == 27) break;
    }

    return 0;
}
