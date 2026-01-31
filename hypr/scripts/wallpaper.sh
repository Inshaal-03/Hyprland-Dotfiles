value=$(fd --full-path /home/inshaal/Wallpaper-Repository | vicinae dmenu -n "Wallpaper and Colorscheme Switcher" -p "Select a Wallpaper" -s "Wallpapers")
wal -i $value
