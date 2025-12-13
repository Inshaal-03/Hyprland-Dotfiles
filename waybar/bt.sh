#!/usr/bin/env bash

BT_STATUS=$(upower -i /org/freedesktop/UPower/devices/headset_dev_DB_3E_52_DB_29_BC \
            | grep percentage | awk '{print $2}')

if [ "$BT_STATUS" = "0%" ]; then
    echo "{}"
else
    echo "{\"text\":\"$BT_STATUS 󰋋\",\"tooltip\":\"Connected\"}"
fi
