#include "libobsensor/ObSensor.hpp"
#include "libobsensor/h/Context.h"
#include <iostream>

int main() {
    ob_set_logger_to_console(OB_LOG_SEVERITY_NONE, nullptr);

    ob::Context ctx;
    auto devList = ctx.queryDeviceList();
    if (devList->deviceCount() == 0) { std::cerr << "无设备" << std::endl; return 1; }

    auto device = devList->getDevice(0);
    auto sensorList = device->getSensorList();

    for (uint32_t i = 0; i < sensorList->count(); i++) {
        auto sensor = sensorList->getSensor(i);
        std::string sn;
        switch (sensor->type()) {
            case OB_SENSOR_COLOR: sn = "COLOR"; break;
            case OB_SENSOR_DEPTH: sn = "DEPTH"; break;
            case OB_SENSOR_IR:    sn = "IR"; break;
            default:              sn = "OTHER"; break;
        }
        std::cout << "=== " << sn << " ===" << std::endl;
        auto profiles = sensor->getStreamProfileList();
        for (uint32_t j = 0; j < profiles->count(); j++) {
            auto p = profiles->getProfile(j);
            // 所有 profile 都转成 VideoStreamProfile
            auto vp = p->as<ob::VideoStreamProfile>();
            std::cout << "  " << vp->width() << "x" << vp->height()
                      << " @ " << vp->fps() << "fps"
                      << " fmt=" << vp->format();
            if (sensor->type() == OB_SENSOR_COLOR) {
                std::cout << " (" << (vp->format() == OB_FORMAT_MJPG ? "MJPG" :
                                      vp->format() == OB_FORMAT_YUYV ? "YUYV" : std::to_string(vp->format())) << ")";
            }
            std::cout << std::endl;
        }
    }
    return 0;
}
