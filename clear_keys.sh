#!/bin/bash
redis-cli -h 192.168.1.158 KEYS "sensor:$1:*" | xargs redis-cli -h 192.168.1.158 DEL
redis-cli -h 192.168.1.158 SREM "sensors" $1
redis-cli -h 192.168.1.158 HDEL "sensors:last_location" $1
redis-cli -h 192.168.1.158 HDEL "sensors:functions" $1
