#!/bin/bash
WALLPAPER=$(find ~/Wallpaper-Partition -type f \
    -regex '.*\.\(png\|jpg\|jpeg\|webp\)' \
    | vicinae dmenu -p 'Pick a Wallpaper')

sww img $WALLPAPER
wal -i $WALLPAPER
notify-send "Wallpaper Changed" "Wallpaper and colorscheme has been changed according to the $WALLPAPER Wallpaper."

