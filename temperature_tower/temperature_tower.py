# -*- coding: utf-8 -*-

# based on: https://notes.iopush.net/blog/2021/01-python-script-gcode-set-temperature/ (https://gist.github.com/Oliv4945/)
# list of all gcode commands in: https://marlinfw.org/docs/gcode/M109.html
# the best STL temperature tower: https://www.thingiverse.com/thing:3127899

# Usage: python3 temperature_tower.py Temperature_Tower.gcode 8 255 5
# 8: Tower steps in mm
# 255: First step temperature in degrees °C
# 5: Temperature steps in °C

import argparse
import os
import re

parser = argparse.ArgumentParser()
parser.add_argument("file", help="Input GCode file to be parserd", type=str)
parser.add_argument("tower_steps", help="Tower steps in mm", type=int)
parser.add_argument(
    "temperature", help="First step temperature in degrees °C", type=int
)
parser.add_argument("temperature_step", help="Temperature steps in °C", type=int)
args = parser.parse_args()

# parameters
file = args.file
tower_steps_mm = args.tower_steps
temperature_c = args.temperature
temperature_step_c = args.temperature_step

# Intenal var
tower_step = 1

with open(file, "r") as file_in:
    data_in = file_in.readlines()

with open(f"out_{file}", "w") as file_out:
    for line in data_in:
        # Capture all layer changes
        # From https://reprap.org/forum/read.php?156,645652,646984#msg-646984
        match = re.search(r"Z(\d+\.?\d*)", line)
        if match:
            height = match.group(1)
            # Add temperature change in case of multiple of tower_steps_mm
            # in a Qidi 3D printer, the first layer is at 0.3mm and the round number is 0.1mm
            if height == f"{tower_steps_mm*tower_step}.1":
                print(
                    f"Height {tower_steps_mm*tower_step} mm: temperature set to {temperature_c}°C"
                )
                # M104: Set Extruder Temperature
                file_out.write(f"M104 S{temperature_c}{os.linesep}")
                temperature_c -= temperature_step_c
                tower_step += 1
        file_out.write(line)
