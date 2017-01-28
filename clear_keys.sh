#!/bin/bash
redis-cli -h 192.168.1.158 KEYS "sensor:*" | xargs redis-cli -h 192.168.1.158 DEL
