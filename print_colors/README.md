# 3DPP - print_colors
## _The easy way to print 3D files with colors_

There are several ways to print in color, but each slicer uses different methods to generate the gcode files with the colors.

In my case, my QIDI printer came with a modified slicer (based on the Cura version), where some options from some tutorials were unavailable.

## How it works

- The script works by reading the gcode files in order, with the file 0-black.gcode as the initial and final file of the print, meaning it contains the initial and final parameters of the 3D printer;
- Within the script, there is an option to set the temperatures for the colors separately, due to filament manufacturers having different characteristics in their materials;
- You can use the tower_temperature.py script in this project to generate a temperature tower to identify the best temperature for your filament.

## How print with colors

- Import all STL files in Cura;
- Select all objects and right-click, choosing the option "Merge Models". At this point, all the pieces will be together and aligned. Right-click again on the piece and select the option "Ungroup Models";
- Slice the pieces separately, name the file in the format number-color.gcode, for example: 0-black.gcode, 1-blue.gcode, etc;
- Run the python3 program print_colors.py with the exported gcode files in the same directory. It will create a single file called merged.gcode.
- Copy the merged.gcode file to your printer. At each color change, it will emit 3 beeps and pause the printing, requesting the color change.

## Running

Save all gcode files in same directory, then run:

```sh
python3 print_colors.py
```


## License

MIT

**"Done is better than perfect."**
