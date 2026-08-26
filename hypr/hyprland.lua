local colors = dofile(os.getenv("HOME") .. "/.cache/wal/hyprland-colors.lua")
-- Monitor
hl.monitor({
	output = "eDP-1",
	mode = "1920x1200@60",
	position = "0x0",
	scale = 1,
})
-- Autostart
hl.on("hyprland.start", function()
	hl.exec_cmd("hyprpaper & waybar & nm-applet & swaync & blueman-applet")
	hl.exec_cmd("swayosd-server")
	hl.exec_cmd("clipse -listen")
	hl.exec_cmd("/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1")
end)
-- Enviroment Var
hl.env("XCURSOR_SIZE", "32")
hl.env("XCURSOR_THEME", "Bibata-Modern-Ice")
hl.env("QT_QPA_PLATFORMTHEME", "qt6ct")
hl.env("XDG_MENU_PREFIX", "arch-")
-- Look and Feel Section
hl.config({
	general = {
		gaps_in = 2,
		gaps_out = 4,
		border_size = 3,
		resize_on_border = false,
		allow_tearing = false,
		layout = "scrolling",
		col = {
			active_border = colors.color4,
			inactive_border = colors.color3,
		},
	},

	decoration = {
		rounding = 14,
		active_opacity = 1.0,
		inactive_opacity = 0.8,
		blur = {
			enabled = true,
			size = 8,
			passes = 1,
		},

		shadow = {
			enabled = false,
		},
	},

	animations = {
		enabled = true,
	},
	misc = {
		force_default_wallpaper = 0,
		disable_hyprland_logo = true,
	},
})

-- Default curves and animations, see https://wiki.hypr.land/Configuring/Advanced-and-Cool/Animations/
hl.curve("easeOutQuint", { type = "bezier", points = { { 0.23, 1 }, { 0.32, 1 } } })
hl.curve("easeInOutCubic", { type = "bezier", points = { { 0.65, 0.05 }, { 0.36, 1 } } })
hl.curve("linear", { type = "bezier", points = { { 0, 0 }, { 1, 1 } } })
hl.curve("almostLinear", { type = "bezier", points = { { 0.5, 0.5 }, { 0.75, 1 } } })
hl.curve("quick", { type = "bezier", points = { { 0.15, 0 }, { 0.1, 1 } } })

-- Default springs
hl.curve("easy", { type = "spring", mass = 1, stiffness = 71.2633, dampening = 15.8273644 })

hl.animation({ leaf = "global", enabled = true, speed = 10, bezier = "default" })
hl.animation({ leaf = "border", enabled = true, speed = 9.39, bezier = "easeOutQuint" })
hl.animation({ leaf = "windows", enabled = true, speed = 4.79, spring = "easy" })
hl.animation({ leaf = "windowsIn", enabled = true, speed = 9.1, spring = "easy", style = "popin 87%" })
hl.animation({ leaf = "windowsOut", enabled = true, speed = 9.49, bezier = "linear", style = "popin 87%" })
hl.animation({ leaf = "fadeIn", enabled = true, speed = 1.73, bezier = "almostLinear" })
hl.animation({ leaf = "fadeOut", enabled = true, speed = 1.46, bezier = "almostLinear" })
hl.animation({ leaf = "fade", enabled = true, speed = 3.03, bezier = "quick" })
hl.animation({ leaf = "layers", enabled = true, speed = 3.81, bezier = "easeOutQuint" })
hl.animation({ leaf = "layersIn", enabled = true, speed = 4, bezier = "easeOutQuint", style = "fade" })
hl.animation({ leaf = "layersOut", enabled = true, speed = 1.5, bezier = "linear", style = "fade" })
hl.animation({ leaf = "fadeLayersIn", enabled = true, speed = 1.79, bezier = "almostLinear" })
hl.animation({ leaf = "fadeLayersOut", enabled = true, speed = 1.39, bezier = "almostLinear" })
hl.animation({ leaf = "workspaces", enabled = true, speed = 1.94, bezier = "almostLinear", style = "fade" })
hl.animation({ leaf = "workspacesIn", enabled = true, speed = 1.21, bezier = "almostLinear", style = "fade" })
hl.animation({ leaf = "workspacesOut", enabled = true, speed = 1.94, bezier = "almostLinear", style = "fade" })
hl.animation({ leaf = "zoomFactor", enabled = true, speed = 7, bezier = "quick" })

hl.config({
	input = {
		kb_layout = "us",
		kb_variant = "",
		kb_model = "",
		kb_rules = "",
		kb_options = "ctrl:swapcaps",
		touchpad = {
			natural_scroll = true,
		},
	},
})

hl.gesture({
	fingers = 3,
	direction = "horizontal",
	action = "workspace",
})
-- Binds
local mainMod = "SUPER"
local scriptLocation = "~/Dotfiles/hypr/scripts/"

hl.bind(mainMod .. " + Q", hl.dsp.window.close())
hl.bind(mainMod .. " + RETURN", hl.dsp.exec_cmd("kitty"))
hl.bind(mainMod .. " + E", hl.dsp.exec_cmd("dolphin"))
hl.bind(mainMod .. " + D", hl.dsp.exec_cmd("rofi -show drun"))
hl.bind(mainMod .. " + F", hl.dsp.window.fullscreen({ mode = "fullscreen", action = "toggle" }))
hl.bind(mainMod .. " + V", hl.dsp.window.float({ action = "toggle" }))
hl.bind(mainMod .. " + SHIFT + F", hl.dsp.window.fullscreen({ mode = "maximized", action = "toggle" }))

hl.bind(mainMod .. " + S", hl.dsp.exec_cmd(scriptLocation .. "screenshot"))
hl.bind(mainMod .. " + P", hl.dsp.exec_cmd(scriptLocation .. "powermenu"))
hl.bind(mainMod .. " + U", hl.dsp.exec_cmd(scriptLocation .. "utils"))
hl.bind(mainMod .. " + W", hl.dsp.exec_cmd(scriptLocation .. "wch"))

hl.bind(mainMod .. " + H", hl.dsp.focus({ direction = "left" }))
hl.bind(mainMod .. " + J", hl.dsp.focus({ direction = "down" }))
hl.bind(mainMod .. " + K", hl.dsp.focus({ direction = "up" }))
hl.bind(mainMod .. " + L", hl.dsp.focus({ direction = "right" }))

for i = 0, 9 do
	hl.bind(mainMod .. " + " .. i, hl.dsp.focus({ workspace = i }))
	hl.bind(mainMod .. " + SHIFT + " .. i, hl.dsp.window.move({ workspace = i }))
end

hl.bind("XF86AudioRaiseVolume", hl.dsp.exec_cmd("swayosd-client --output-volume 10 --max-volume 200"))
hl.bind("XF86AudioLowerVolume", hl.dsp.exec_cmd("swayosd-client --output-volume -10 --max-volume 200"))
hl.bind("XF86AudioMute", hl.dsp.exec_cmd("swayosd-client --output-volume mute-toggle"))
hl.bind("XF86AudioMicMute", hl.dsp.exec_cmd("swayosd-client --input-volume mute-toggle"))
hl.bind("XF86MonBrightnessUp", hl.dsp.exec_cmd("swayosd-client --brightness +10"))
hl.bind("XF86MonBrightnessDown", hl.dsp.exec_cmd("swayosd-client --brightness -10"))

hl.window_rule({
	name = "Rule for nwg-look",
	match = {
		class = "nwg-look",
		title = "nwg-look",
	},
	float = 1,
	center = 1,
})

hl.window_rule({
	name = "Center Local Send App",
	match = {
		class = "localsend",
	},
	float = 1,
	center = 1,
	size = "1200 700",
})

hl.window_rule({
	name = "Center Utilities",
	match = {
		class = "utils",
	},
	float = 1,
	center = 1,
	size = "1000 700",
})

hl.window_rule({
	name = "Centering qt-sudo",
	match = {
		class = "qt-sudo",
	},
	float = 1,
	center = 1,
	size = "900 700",
})

hl.window_rule({
	name = "Hiding setup black screen",
	match = {
		title = "Setup",
		class = "steam_app_default",
	},
	float = 1,
	border_size = 0,
	size = "1 1",
})

hl.window_rule({
	name = "Opening Zen Browser on Workspace 1",
	match = {
		class = "zen",
	},
	workspace = 1,
})

hl.window_rule({
	name = "No border for fitgirl setup screen",
	match = {
		title = "Select Setup Language",
		class = "steam_app_default",
	},
	float = 1,
	center = 1,
	border_size = 0,
})
