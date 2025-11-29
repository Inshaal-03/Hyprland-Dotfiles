#!/bin/bash
FOLDER=$(find ~/Code-Base-Drive -maxdepth 1 -type d  | vicinae dmenu -p "Pick Folder")
kitty -e nvim "$FOLDER"
