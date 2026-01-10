#!/usr/bin/env python3
# SYS-MON MODULE
# Snapshot: 20
# Version: 1.90
# Status: Stable

import json
import psutil
import subprocess
import re
import os
import time
import shutil
import pickle
from collections import deque
import math

# ---------------------------------------------------
# USER CONFIGURATION
# ---------------------------------------------------
CONFIG = {
    # Hardware names (auto-detected if empty)
    "cpu_name": "",  # e.g., "AMD Ryzen 9 9900X" or leave empty for auto-detect
    "gpu_name": "",  # e.g., "Nvidia RTX 4080 Super" or leave empty for auto-detect
    
    # Memory modules (leave empty list for basic memory info only)
    "memory_modules": [
        # Example:
        # {"label": "DIMM1", "size": "16 GB", "speed": "3200 MHz", "temp": 42, "type": "DDR4", "rank": "Dual"},
        # {"label": "DIMM2", "size": "16 GB", "speed": "3200 MHz", "temp": 41, "type": "DDR4", "rank": "Dual"},
    ],
    
    # Custom storage drives to monitor
    # Format: (Display Name, Mount Point, Icon)
    "storage_drives": [
        ("System", "/", ""),  # SSD icon
        # Add your drives here, examples:
        # ("Games", "/mnt/Games", ""),
        # ("Media", "/mnt/Media", "󰋊"),  # HDD icon
        # ("Backup", "/mnt/BackupDrive", "󰋊"),
    ],
    
    # Theme config file path (leave empty to disable theme loading)
    "theme_path": "",  # e.g., "~/.config/omarchy/current/theme/alacritty.toml"
    
    # History file location
    "history_file": "/tmp/waybar_sysmon_history.pkl",
    
    # Tooltip width (number of data points in graphs)
    "tooltip_width": 70,
    
    # Click actions
    "left_click_command": ["btop"],  # Command to run on left click (in terminal)
    "right_click_command": ["/usr/bin/coolercontrol"],  # Command to run on right click
}

# ---------------------------------------------------
# ICONS
# ---------------------------------------------------
CPU_ICON_GENERAL = ""
GPU_ICON = ""
MEM_ICON = ""
SSD_ICON = ""
HDD_ICON = "󰋊"

# ---------------------------------------------------
# LOAD THEME COLORS
# ---------------------------------------------------
def load_theme_colors():
    """Load colors from theme file if specified, otherwise use defaults"""
    theme_path = CONFIG.get("theme_path", "")
    
    if theme_path:
        try:
            import tomllib
            import pathlib
            expanded_path = pathlib.Path(theme_path).expanduser()
            
            if expanded_path.exists():
                data = tomllib.loads(expanded_path.read_text())
                colors = data.get("colors", {})
                normal = colors.get("normal", {})
                bright = colors.get("bright", {})

                return {
                    "black": normal.get("black", "#000000"),
                    "red": normal.get("red", "#ff0000"),
                    "green": normal.get("green", "#00ff00"),
                    "yellow": normal.get("yellow", "#ffff00"),
                    "blue": normal.get("blue", "#0000ff"),
                    "magenta": normal.get("magenta", "#ff00ff"),
                    "cyan": normal.get("cyan", "#00ffff"),
                    "white": normal.get("white", "#ffffff"),
                    "bright_black": bright.get("black", "#555555"),
                    "bright_red": bright.get("red", "#ff5555"),
                    "bright_green": bright.get("green", "#55ff55"),
                    "bright_yellow": bright.get("yellow", "#ffff55"),
                    "bright_blue": bright.get("blue", "#5555ff"),
                    "bright_magenta": bright.get("magenta", "#ff55ff"),
                    "bright_cyan": bright.get("cyan", "#55ffff"),
                    "bright_white": bright.get("white", "#ffffff"),
                }
        except Exception:
            pass
    
    # Default colors
    return {
        "black": "#000000",
        "red": "#ff0000",
        "green": "#00ff00",
        "yellow": "#ffff00",
        "blue": "#0000ff",
        "magenta": "#ff00ff",
        "cyan": "#00ffff",
        "white": "#ffffff",
        "bright_black": "#555555",
        "bright_red": "#ff5555",
        "bright_green": "#55ff55",
        "bright_yellow": "#ffff55",
        "bright_blue": "#5555ff",
        "bright_magenta": "#ff55ff",
        "bright_cyan": "#55ffff",
        "bright_white": "#ffffff",
    }

COLORS = load_theme_colors()

# ---------------------------------------------------
# SECTION COLORS
# ---------------------------------------------------
SECTION_COLORS = {
    "CPU":     {"icon": COLORS["red"],    "text": COLORS["red"]},
    "GPU":     {"icon": COLORS["yellow"], "text": COLORS["yellow"]},
    "Memory":  {"icon": COLORS["green"],  "text": COLORS["green"]},
    "Storage": {"icon": COLORS["blue"],   "text": COLORS["blue"]},
}

# ---------------------------------------------------
# COLOR TABLE (GRADIENT)
# ---------------------------------------------------
COLOR_TABLE = [
    {"color": "#8caaee", "cpu_gpu_temp": (0, 35),  "cpu_power": (0.0, 30),   "gpu_power": (0.0, 50),   "mem_storage": (0.0, 10)},
    {"color": "#99d1db", "cpu_gpu_temp": (36, 45), "cpu_power": (31.0, 60),  "gpu_power": (51.0, 100), "mem_storage": (10.0, 20)},
    {"color": "#81c8be", "cpu_gpu_temp": (46, 54), "cpu_power": (61.0, 90),  "gpu_power": (101.0,200), "mem_storage": (20.0, 40)},
    {"color": "#e5c890", "cpu_gpu_temp": (55, 65), "cpu_power": (91.0, 120), "gpu_power": (201.0,300), "mem_storage": (40.0, 60)},
    {"color": "#ef9f76", "cpu_gpu_temp": (66, 75), "cpu_power": (121.0,150), "gpu_power": (301.0,400), "mem_storage": (60.0, 80)},
    {"color": "#ea999c", "cpu_gpu_temp": (76, 85), "cpu_power": (151.0,180), "gpu_power": (401.0,450), "mem_storage": (80.0, 90)},
    {"color": "#e78284", "cpu_gpu_temp": (86, 999), "cpu_power": (181.0,999), "gpu_power": (451.0,999), "mem_storage": (90.0,100)}
]

def get_color(value, metric_type):
    if value is None:
        return "#ffffff"
    try:
        value = float(value)
    except:
        return "#ffffff"
    for entry in COLOR_TABLE:
        low, high = entry[metric_type] if metric_type in entry else (0, 0)
        if low <= value <= high:
            return entry["color"]
    return COLOR_TABLE[-1]["color"]

# ---------------------------------------------------
# HISTORY MANAGEMENT
# ---------------------------------------------------
TOOLTIP_WIDTH = CONFIG["tooltip_width"]
HISTORY_FILE = CONFIG["history_file"]

def load_history():
    try:
        with open(HISTORY_FILE, 'rb') as f:
            return pickle.load(f)
    except:
        return {
            'cpu': deque(maxlen=TOOLTIP_WIDTH), 
            'gpu': deque(maxlen=TOOLTIP_WIDTH),
            'mem': deque(maxlen=TOOLTIP_WIDTH),
            'per_core': {}
        }

def save_history(cpu_hist, gpu_hist, mem_hist, core_hist):
    try:
        with open(HISTORY_FILE, 'wb') as f:
            pickle.dump({'cpu': cpu_hist, 'gpu': gpu_hist, 'mem': mem_hist, 'per_core': core_hist}, f)
    except:
        pass

# ---------------------------------------------------
# SPARKLINE GENERATOR
# ---------------------------------------------------
def create_colored_sparkline(values, width=TOOLTIP_WIDTH, cpu_mode=False):
    """
    Two-line stacked sparkline with controlled scaling.
    If cpu_mode=True, values are scaled so 50% = max height
    If cpu_mode=False (GPU), 100% = max height
    """
    if not values or len(values) < 2:
        line = "▁" * width
        return f"{line}\n{line}", None, None, None

    blocks = ['▁','▂','▃','▄','▅','▆','▇','█']

    vals_list = list(values)
    if len(vals_list) < width:
        vals_list = [0] * (width - len(vals_list)) + vals_list
    else:
        vals_list = vals_list[-width:]

    valid_vals = [v for v in vals_list if v is not None]
    if not valid_vals:
        line = "▁" * width
        return f"{line}\n{line}", None, None, None

    min_val = min(valid_vals)
    max_val = max(valid_vals)
    avg_val = sum(valid_vals) / len(valid_vals)

    scale_to_100 = 50.0 if cpu_mode else 100.0

    line_top = []
    line_bottom = []

    def get_sparkline_color(v):
        return COLORS["white"]

    for v in vals_list:
        if v is None:
            v = 0

        normalized = (v / scale_to_100) * 100.0
        normalized = min(normalized, 100.0)
        
        scaled = int((normalized / 100.0) * 16)
        scaled = max(1, min(scaled, 16))

        if scaled <= 8:
            bottom_level = scaled
            top_level = 0
        else:
            bottom_level = 8
            top_level = scaled - 8

        line_bottom.append(f"<span foreground='{get_sparkline_color(v)}'>{blocks[bottom_level - 1]}</span>")
        line_top.append(f"<span foreground='{get_sparkline_color(v)}'>{blocks[top_level - 1] if top_level > 0 else ' '}</span>")

    sparkline = ''.join(line_top) + "\n" + ''.join(line_bottom)
    return sparkline, min_val, avg_val, max_val

# ---------------------------------------------------
# AUTO-DETECT HARDWARE
# ---------------------------------------------------
def get_cpu_name():
    """Auto-detect CPU name"""
    if CONFIG.get("cpu_name"):
        return CONFIG["cpu_name"]
    
    try:
        with open("/proc/cpuinfo", "r") as f:
            for line in f:
                if "model name" in line:
                    return line.split(":")[1].strip()
    except:
        pass
    return "Unknown CPU"

def get_gpu_name():
    """Auto-detect GPU name"""
    if CONFIG.get("gpu_name"):
        return CONFIG["gpu_name"]
    
    try:
        output = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            text=True
        )
        return output.strip()
    except:
        pass
    return "Unknown GPU"

# ---------------------------------------------------
# Load history
# ---------------------------------------------------
history = load_history()
cpu_history = history.get('cpu', deque(maxlen=TOOLTIP_WIDTH))
gpu_history = history.get('gpu', deque(maxlen=TOOLTIP_WIDTH))
mem_history = history.get('mem', deque(maxlen=TOOLTIP_WIDTH))
per_core_history = history.get('per_core', {})

# ---------------------------------------------------
# CPU INFO
# ---------------------------------------------------
max_cpu_temp = 0
cpu_name = get_cpu_name()
current_freq = max_freq = 0

try:
    temps = psutil.sensors_temperatures() or {}
    k10 = temps.get("coretemp", [])
    for t in k10:
        if hasattr(t, "label") and t.label and t.label.lower() == "tctl":
            max_cpu_temp = int(t.current)
except:
    pass

try:
    cpu_info = psutil.cpu_freq(percpu=False)
    if cpu_info:
        current_freq = cpu_info.current or 0
        max_freq = cpu_info.max or 0
except:
    pass

# ---------------------------------------------------
# CPU POWER
# ---------------------------------------------------
cpu_power = 0.0
rapl_package_path = "/sys/class/powercap/intel-rapl:0/energy_uj"

try:
    with open(rapl_package_path, "r") as f:
        energy1 = int(f.read().strip())
    time.sleep(0.5)
    with open(rapl_package_path, "r") as f:
        energy2 = int(f.read().strip())
    
    delta_energy = energy2 - energy1
    
    if delta_energy < 0:
        try:
            with open("/sys/class/powercap/intel-rapl:0/max_energy_range_uj", "r") as f:
                max_energy = int(f.read().strip())
            delta_energy = (max_energy + energy2) - energy1
        except:
            delta_energy = (2**32 + energy2) - energy1
    
    cpu_power = (delta_energy / 1_000_000) / 0.5
    
    if cpu_power < 0 or cpu_power > 250:
        cpu_power = 0.0
        
except Exception:
    cpu_power = 0.0

cpu_percent = psutil.cpu_percent(interval=0.1)
cpu_history.append(cpu_percent)

# ---------------------------------------------------
# GPU INFO
# ---------------------------------------------------
gpu_percent = 0
gpu_temp = 0
gpu_power = 0.0
gpu_name = get_gpu_name()
gpu_freq_current = 0
gpu_freq_max = 0

try:
    output = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=utilization.gpu,temperature.gpu,power.draw,clocks.gr,clocks.max.sm", 
         "--format=csv,noheader,nounits"],
        text=True
    )
    match = re.search(r"(\d+)\s*,\s*(\d+)\s*,\s*([\d\.]+)\s*,\s*(\d+)\s*,\s*(\d+)", output)
    if match:
        gpu_percent = int(match.group(1))
        gpu_temp = int(match.group(2))
        gpu_power = float(match.group(3))
        gpu_freq_current = int(match.group(4))
        gpu_freq_max = int(match.group(5))
except:
    pass

gpu_history.append(gpu_percent)

# ---------------------------------------------------
# MEMORY INFO
# ---------------------------------------------------
mem = psutil.virtual_memory()
mem_used_gb = mem.used / (1024**3)
mem_total_gb = mem.total / (1024**3)
mem_percent = mem.percent
mem_available_gb = mem.available / (1024**3)
mem_cached_gb = mem.cached / (1024**3) if hasattr(mem, 'cached') else 0
mem_buffers_gb = mem.buffers / (1024**3) if hasattr(mem, 'buffers') else 0

mem_history.append(mem_percent)

memory_modules = CONFIG.get("memory_modules", [])

# ---------------------------------------------------
# STORAGE INFO
# ---------------------------------------------------
storage_entries = []

for name, mountpoint, icon in CONFIG["storage_drives"]:
    try:
        usage = psutil.disk_usage(mountpoint)
        used_percent = int(usage.percent)
        total_tb = usage.total / (1024**4)
        used_tb = usage.used / (1024**4)
    except Exception:
        continue

    storage_entries.append(
        (icon, name, mountpoint, used_tb, total_tb, used_percent)
    )

total_used_tb = sum(e[3] for e in storage_entries)
total_tb = sum(e[4] for e in storage_entries)
total_percent = int((total_used_tb / total_tb) * 100) if total_tb else 0

# ---------------------------------------------------
# BAR TEXT
# ---------------------------------------------------

text = (
    f"| {CPU_ICON_GENERAL} <span foreground='{get_color(max_cpu_temp,'cpu_gpu_temp')}'>{max_cpu_temp}°C</span>  "
    f"{GPU_ICON} <span foreground='{get_color(gpu_temp,'cpu_gpu_temp')}'>{gpu_temp}°C</span>  "
    f"{MEM_ICON} <span foreground='{get_color(mem_percent,'mem_storage')}'>{mem_percent}%</span> |"
)

# ---------------------------------------------------
# TOOLTIP BUILDING
# ---------------------------------------------------
tooltip_lines = []

# --- CPU ---
tooltip_lines.append(
    f"<span foreground='{SECTION_COLORS['CPU']['icon']}'>{CPU_ICON_GENERAL}</span> "
    f"<span foreground='{SECTION_COLORS['CPU']['text']}'>CPU</span> - {cpu_name}:"
)

cpu_rows = [
    ("", f"Frequency: <span foreground='{get_color(current_freq/max_freq*100, 'cpu_power')}'>{current_freq:.0f} MHz</span> / {max_freq:.0f} MHz"),
    ("", f"Temperature: <span foreground='{get_color(max_cpu_temp,'cpu_gpu_temp')}'>{max_cpu_temp}°C</span>"),
    ("", f"Power: <span foreground='{get_color(cpu_power,'cpu_power')}'>{cpu_power:.1f} W</span>"),
    ("", f"Utilization: <span foreground='{get_color(cpu_percent,'cpu_power')}'>{cpu_percent:.0f}%</span>")
]

cpu_line_texts = [f"{icon} | {text}" for icon, text in cpu_rows]
storage_line_lengths = [len(f"{entry[0]} | {entry[1]} {entry[4]}TB") for entry in storage_entries]

max_line_len = max(
    max(len(re.sub(r'<.*?>','',line)) for line in cpu_line_texts),
    max(storage_line_lengths) if storage_line_lengths else 0,
    TOOLTIP_WIDTH
)

cpu_hline = "─" * max_line_len
tooltip_lines.append(cpu_hline)
for icon, text_row in cpu_rows:
    tooltip_lines.append(f"{icon} | {text_row}")

# Per-core CPU visualization
per_core = psutil.cpu_percent(interval=0.1, percpu=True)

decay_factor = 0.95
for i, usage in enumerate(per_core):
    if i not in per_core_history:
        per_core_history[i] = usage
    else:
        per_core_history[i] = (per_core_history[i] * decay_factor) + (usage * (1 - decay_factor))

def get_core_color(usage):
    if usage < 20:
        return "#81c8be"
    elif usage < 40:
        return "#a6d189"
    elif usage < 60:
        return "#e5c890"
    elif usage < 80:
        return "#ef9f76"
    elif usage < 95:
        return "#ea999c"
    else:
        return "#e78284"

# Build CPU die visualization
cpu_viz_width = 25
center_padding = " " * ((max_line_len - cpu_viz_width) // 2)

substrate_color = get_color(max_cpu_temp, 'cpu_gpu_temp')

tooltip_lines.append(f"{center_padding}  ╔═══════════════════╗")
tooltip_lines.append(f"{center_padding}─ ║<span foreground='{substrate_color}'>▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓</span>║ ─")

cores_per_row = 4
num_rows = (len(per_core) + cores_per_row - 1) // cores_per_row

for row in range(num_rows):
    row_parts = [f"─ ║<span foreground='{substrate_color}'>▓▓</span>"]
    
    for col in range(cores_per_row):
        core_idx = col * num_rows + row
        if core_idx < len(per_core):
            usage = per_core[core_idx]
            color = get_core_color(usage)
            row_parts.append(f"<span foreground='{color}'>[█]</span>")
        else:
            row_parts.append("   ")
        
        if col < cores_per_row - 1:
            row_parts.append(" ")
    
    row_parts.append(f"<span foreground='{substrate_color}'>▓▓</span>║ ─")
    tooltip_lines.append(f"{center_padding}{''.join(row_parts)}")

tooltip_lines.append(f"{center_padding}─ ║<span foreground='{substrate_color}'>▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓</span>║ ─")
tooltip_lines.append(f"{center_padding}  ╚═══════════════════╝")

# Most active cores
tooltip_lines.append("Most Active Cores (average load last 10 min):")

core_avgs = [(i, per_core_history[i]) for i in sorted(per_core_history.keys())]
core_avgs.sort(key=lambda x: x[1], reverse=True)
top_4 = core_avgs[:4]

def get_low_usage_color(usage):
    if usage >= 20:
        return COLORS['red']
    if usage < 10:
        return COLORS['blue'] if usage < 5 else COLORS['cyan']
    else:
        return COLORS['cyan'] if usage < 15 else COLORS['yellow']

active_parts = []
for core_num, avg_usage in top_4:
    color = get_low_usage_color(avg_usage)
    active_parts.append(f"󰍛 {core_num+1}: <span foreground='{color}'>{avg_usage:.1f}%</span>")

tooltip_lines.append(" | ".join(active_parts))

# --- GPU ---
tooltip_lines.append("")
tooltip_lines.append(
    f"<span foreground='{SECTION_COLORS['GPU']['icon']}'>{GPU_ICON}</span> "
    f"<span foreground='{SECTION_COLORS['GPU']['text']}'>GPU</span> - {gpu_name}:"
)

gpu_rows = [
    # ("", f"Frequency: <span foreground='{get_color(gpu_freq_current/gpu_freq_max*100, 'gpu_power')}'>{gpu_freq_current} MHz</span> / {gpu_freq_max} MHz"),
    ("", f"Temperature: <span foreground='{get_color(gpu_temp,'cpu_gpu_temp')}'>{gpu_temp}°C</span>"),
    ("", f"Power: <span foreground='{get_color(gpu_power,'gpu_power')}'>{gpu_power:.1f} W</span>"),
    ("", f"Utilization: <span foreground='{get_color(gpu_percent,'gpu_power')}'>{gpu_percent}%</span>")
]

gpu_hline = "─" * max_line_len
tooltip_lines.append(gpu_hline)
for icon, text_row in gpu_rows:
    tooltip_lines.append(f"{icon} | {text_row}")

if len(gpu_history) >= 2:
    sparkline, min_val, avg_val, max_val = create_colored_sparkline(gpu_history, width=max_line_len)
    tooltip_lines.append(f"{sparkline}")
    if min_val is not None:
        stats_text = f"<span size='11000'>min <span foreground='{get_color(min_val,'gpu_power')}'>{min_val:.0f}%</span> avg <span foreground='{get_color(avg_val,'cpu_power')}'>{avg_val:.0f}%</span> max <span foreground='{get_color(max_val,'gpu_power')}'>{max_val:.0f}%</span></span>"
        plain_text_len = len("min 00% avg 00% max 00%")
        padding = int(max_line_len - (plain_text_len * 0.78))
        tooltip_lines.append(" " * padding + stats_text)

# --- MEMORY ---
tooltip_lines.append("")
tooltip_lines.append(
    f"<span foreground='{SECTION_COLORS['Memory']['icon']}'>{MEM_ICON}</span> "
    f"<span foreground='{SECTION_COLORS['Memory']['text']}'>Memory</span>:"
)

mem_table_width = max_line_len
mem_hline = "─" * mem_table_width
tooltip_lines.append(mem_hline)

usage_line = f"󰘚 | Usage: {mem_used_gb:.1f} / {mem_total_gb:.1f} GB (<span foreground='{get_color(mem_percent,'mem_storage')}'>{mem_percent}%</span>)"
tooltip_lines.append(usage_line)

stats_line = f"󰉉 | Cached: {mem_cached_gb:.1f} GB | Buffers: {mem_buffers_gb:.1f} GB"
tooltip_lines.append(stats_line)

if memory_modules:
    usage_dash_line = "-" * mem_table_width
    tooltip_lines.append(usage_dash_line)

    icon_col = []
    label_col = []
    size_col = []
    speed_col = []
    type_col = []
    rank_col = []
    temp_col = []

    for mod in memory_modules:
        icon_col.append(MEM_ICON)
        label_col.append(mod["label"])
        size_col.append(mod["size"])
        speed_col.append(mod["speed"])
        type_col.append(mod.get("type", "DDR4"))
        rank_col.append(mod.get("rank", "Dual"))
        temp_col.append(f"<span foreground='{get_color(mod['temp'],'cpu_gpu_temp')}'>{mod['temp']}°C</span>")

    max_label_len = max(len(l) for l in label_col)
    max_size_len = max(len(s) for s in size_col)
    max_speed_len = max(len(sp) for sp in speed_col)
    max_type_len = max(len(t) for t in type_col)
    max_rank_len = max(len(r) for r in rank_col)

    for i in range(len(memory_modules)):
        line = (
            f"{icon_col[i]} | "
            f"{label_col[i]:<{max_label_len}} | "
            f"{size_col[i]:<{max_size_len}} | "
            f"{type_col[i]:<{max_type_len}} | "
            f"{speed_col[i]:<{max_speed_len}} | "
            f"{rank_col[i]:<{max_rank_len}} | "
            f"{temp_col[i]:>4}"
        )
        tooltip_lines.append(line)

# Memory breakdown bar
tooltip_lines.append("")

free_gb = mem_total_gb - mem_used_gb
used_pct = (mem_used_gb / mem_total_gb) * 100
cached_pct = (mem_cached_gb / mem_total_gb) * 100
buffers_pct = (mem_buffers_gb / mem_total_gb) * 100
free_pct = (free_gb / mem_total_gb) * 100

used_blocks = int((used_pct / 100) * max_line_len)
cached_blocks = int((cached_pct / 100) * max_line_len)
buffers_blocks = int((buffers_pct / 100) * max_line_len)
free_blocks = max_line_len - used_blocks - cached_blocks - buffers_blocks

bar = ""
bar += f"<span foreground='{COLORS['red']}'>{'█' * used_blocks}</span>"
bar += f"<span foreground='{COLORS['yellow']}'>{'█' * cached_blocks}</span>"
bar += f"<span foreground='{COLORS['cyan']}'>{'█' * buffers_blocks}</span>"
bar += f"<span foreground='{COLORS['bright_black']}'>{'░' * free_blocks}</span>"

tooltip_lines.append(bar)
tooltip_lines.append("")

legend = (
    f"<span size='11000'>"
    f"<span foreground='{COLORS['red']}'>█</span> Used {used_pct:.1f}%  "
    f"<span foreground='{COLORS['yellow']}'>█</span> Cached {cached_pct:.1f}%  "
    f"<span foreground='{COLORS['cyan']}'>█</span> Buffers {buffers_pct:.1f}%  "
    f"<span foreground='{COLORS['bright_black']}'>░</span> Free {free_pct:.1f}%"
    f"</span>"
)
tooltip_lines.append(legend)
tooltip_lines.append(mem_hline)

# --- STORAGE ---
if storage_entries:
    tooltip_lines.append("")
    storage_header_text = f"{SSD_ICON} Storage"
    tooltip_lines.append(f"<span foreground='{SECTION_COLORS['Storage']['text']}'>{storage_header_text}</span>:")

    def format_tb(value_tb):
        return f"{math.ceil(value_tb * 10) / 10:.1f}TB"

    name_width = max(len(label) for _, label, *_ in storage_entries)
    size_width = max(len(format_tb(e[4])) for e in storage_entries)
    used_width = max(len(format_tb(e[3])) for e in storage_entries)
    percent_width = max(len(f"{int(e[5])}%") if e[5] is not None else 3 for e in storage_entries)

    storage_hline = "─" * max(max_line_len, name_width + size_width + used_width + percent_width + 10)
    storage_dash = "-" * max(max_line_len, name_width + size_width + used_width + percent_width + 10)
    tooltip_lines.append(storage_hline)

    total_used_tb_rounded = math.ceil(total_used_tb * 10) / 10
    total_tb_rounded = math.ceil(total_tb * 10) / 10
    usage_line = f" | Usage: {total_used_tb_rounded:.1f} / {total_tb_rounded:.1f} TB (<span foreground='{get_color(total_percent,'mem_storage')}'>{total_percent}%</span>)"
    tooltip_lines.append(usage_line)
    tooltip_lines.append(storage_dash)

    for icon, label, mount, used_tb, total_tb_drive, used_percent in storage_entries:
        total_tb_str = format_tb(total_tb_drive)
        used_tb_str = format_tb(used_tb)
        percent_color = get_color(used_percent, "mem_storage") if used_percent is not None else "#ffffff"
        percent_str = f"<span foreground='{percent_color}'>{int(used_percent)}%</span>" if used_percent is not None else "N/A"
        line = (
            f"{icon} | "
            f"{label:<{name_width}} "
            f"{total_tb_str:>{size_width}} | "
            f"{used_tb_str:>{used_width}} "
            f"({percent_str:>{percent_width+len(percent_str)-len(re.sub(r'<.*?>','',percent_str))}})"
        )
        tooltip_lines.append(line)

    tooltip_lines.append(storage_hline)

# --- FOOTER ---
tooltip_lines.append("")
tooltip_lines.append("🖱️ LMB: Btop | 🖱️ RMB: C-Control")

tooltip = "\n".join(tooltip_lines)
tooltip = f"<span size='14000'>{tooltip}</span>"

# Save history for next run
save_history(cpu_history, gpu_history, mem_history, per_core_history)

TERMINAL = os.environ.get("TERMINAL") or shutil.which("alacritty") or shutil.which("kitty") or shutil.which("gnome-terminal") or "xterm"

click_type = os.environ.get("WAYBAR_CLICK_TYPE")

if click_type == "left":
    subprocess.Popen([TERMINAL, "-e"] + CONFIG["left_click_command"])
elif click_type == "right":
    subprocess.Popen(CONFIG["right_click_command"])

output = {
    "text": text,
    "tooltip": tooltip,
    "markup": "pango",
    "click-events": True
}

print(json.dumps(output))
