#!/bin/bash
WALLPAPER=$(find ~/Wallpaper-Partition -type f \
    -regex '.*\.\(png\|jpg\|jpeg\|webp\)' \
    | vicinae dmenu -p 'Pick a Wallpaper')

if [[ -z "$WALLPAPER" ]]; then
    notify-send "No Wallpaper Selected"
    exit 1
fi

sww img $WALLPAPER
wal -i $WALLPAPER
FILENAME=$(basename "$WALLPAPER")
notify-send "Wallpaper Changed" "Wallpaper and colorscheme has been changed according to the $FILENAME Wallpaper."

