#!/bin/bash

# Define profiles and their corresponding values for powerprofilesctl
declare -A profile_map
profile_map["󱐋  Performance"]="performance"
profile_map["  Balanced"]="balanced"
profile_map["  Power Saver"]="power-saver"

# Rofi theme
theme="~/dotfiles/rofi/power-profile.rasi"

# Show menu with icon + label
current_profile=$(powerprofilesctl get)
captalized_profile="${current_profile^}"
selected_profile=$(printf "%s\n" "${!profile_map[@]}" | rofi -i -dmenu -p "Power Profile" -theme "$theme" -mesg "Current Power Profile: $captalized_profile")

# Check if selection was made
if [ -n "$selected_profile" ]; then
  profile_value="${profile_map[$selected_profile]}"
  if powerprofilesctl set "$profile_value" 2>/dev/null; then
    notify-send "Power Profile" "Switched to $profile_value" --icon=dialog-information
  else
    notify-send "Error" "Failed to switch to $profile_value" --icon=dialog-error
  fi
else
  notify-send "Power Profile" "No profile selected" --icon=dialog-warning
fi
