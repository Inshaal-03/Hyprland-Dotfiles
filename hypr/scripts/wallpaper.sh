#!/bin/bash
WALLPAPER=$(find ~/Wallpaper-Partition -type f \
    -regex '.*\.\(png\|jpg\|jpeg\|webp\)' \
    | vicinae dmenu -p 'Pick a Wallpaper')

if [[ -z "$WALLPAPER" ]]; then
    exit 1
fi

sww img $WALLPAPER
wal -i $WALLPAPER
FILENAME=$(basename "$WALLPAPER")

