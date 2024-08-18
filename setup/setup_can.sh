#!/bin/bash

# Check if the CAN interface is already up
if ! /sbin/ip link show can0 | grep -q "state UP"; then
    # If not, set it up
    /sbin/ip link set can0 up type can bitrate 500000
fi