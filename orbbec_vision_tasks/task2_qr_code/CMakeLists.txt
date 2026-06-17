cmake_minimum_required(VERSION 3.10)
project(QRScanner)

set(CMAKE_CXX_STANDARD 11)

# OpenCV
find_package(OpenCV 4 REQUIRED COMPONENTS core highgui imgproc imgcodecs objdetect wechat_qrcode)
include_directories(${OpenCV_INCLUDE_DIRS})

# Orbbec SDK
set(ORBBEC_SDK_DIR "/home/kricter/下载/OrbbecSDK_C_C++_v1.10.27_20250925_0549823_linux_x64_release/OrbbecSDK_v1.10.27/SDK")
include_directories(${ORBBEC_SDK_DIR}/include)
link_directories(${ORBBEC_SDK_DIR}/lib)

add_executable(qr_scanner qr_scanner.cpp)
target_link_libraries(qr_scanner
    ${OpenCV_LIBS}
    OrbbecSDK
)
