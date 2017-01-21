cmake_minimum_required (VERSION 3.5.1)
project ("SmartHome Server")

find_path(MQTT_INCLUDES mqtt/async_client.h)
find_library(MQTTPP_LIB mqttpp)
find_library(MQTT_LIB paho-mqtt3a)

set(SOURCE_FILES main.cpp)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -Wall")

include_directories(${MQTT_INCLUDES})
add_executable(server ${SOURCE_FILES})
target_link_libraries(server ${MQTTPP_LIB} ${MQTT_LIB})
