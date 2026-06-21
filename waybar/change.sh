#!/usr/bin/env bash

file_name="$HOME/Dotfiles/waybar/config.jsonc"
desktop_session="$XDG_CURRENT_DESKTOP"

if [[ "$desktop_session" == 'Hyprland' ]]; then
  include_file="$HOME/Dotfiles/waybar/hyprland.jsonc"
else
  include_file="$HOME/Dotfiles/waybar/kde.jsonc"
fi


cat >"$file_name"<<EOF
  {
    "include": [
      "$include_file"
    ]
  }
'
EOF

killall waybar
waybar
