# This script is used to merge gcode files from different colors to print a multicolor object
# Created by: Jairo Lenfers - 2024-02-17
# Last update: 2024-02-17
#
# Save all gcode files in the same folder and run this script
# The gcode files should be named with the following pattern: number-color.gcode, e.g. 0-black.gcode
# The start and the end of the merged gcode file will be get from the file 0-black.gcode because it's the last color to be printed
# Eg of the name of files:
# 0-black.gcode, 1-white.gcode, 2-red.gcode, etc

import os
import sys

# remove merged.gcode if exists
def remove_merged_gcode(output_filename):
    try:
        print('Removing merged.gcode if exists...')
        os.remove(output_filename)
    except FileNotFoundError:
        pass

# check if file 0-black.gcode exists and get first lines of gcode, then write to new file merged.gcode
# stop copy lines at line: "G0 F4800 X137.863 Y77.695 Z0.3" with X and Y variable values
def start_copying_gcode(output_filename):
    print('Start creating merged.gcode with first lines...')
    try:
        with open('0-black.gcode', 'r') as f:
            for line in f:
                # other method to detect if layer height is changed
                #if line.startswith(('G0 F4800')) and ' Z0.3' in line:
                if line == ';LAYER:0\n':
                    break
                else:
                    with open(output_filename, 'a') as output_file:
                        output_file.write(line)
    except FileNotFoundError:
        print('File 0-black.gcode not found')
        sys.exit(1)

def end_copying_gcode(output_filename):
    print('End creating merged.gcode with last lines...')
    try:
        with open('0-black.gcode', 'r') as f:
            start_copying = False
            for line in f:
                if line == 'M106 T-2 S0\n':
                    start_copying = True
                if start_copying:
                    with open(output_filename, 'a') as output_file:
                        output_file.write(line)

    except FileNotFoundError:
        print('File 0-black.gcode not found')
        sys.exit(1)
        
def process_gcode_files(output_filename):
    # set variables
    # for use to check if layer height is consistent in all gcode files
    layer_height_value = 0
    # for use to processing current layer height
    current_layer_height = 0.3
    current_layer_number = int(0)
    stay_copying = True
    last_color = ''
    # create a dictionary to store the last E value for each color
    e_values = {}
    
    while stay_copying:
        # use sorted with reverse=True to use others colors first and black last
        for file in sorted(os.listdir(), reverse=True):
            if file.endswith('.gcode'):
                # processing only gcode files with start with number
                if not file[0].isdigit():
                    continue
                print(f"Processing file: {file}")
                # ex filename: 0-black.gcode
                # get number and color from filename
                try:
                    number, color = file.split('-')
                    color = color.split('.')[0]
                    #print(number, color)
                except ValueError:
                    print('Invalid filename:', file)
                    print('Filename should be in the format: number-color.gcode, e.g. 0-black.gcode')
                    print('Aborting...')
                    sys.exit(1)
                
                # get value ";Layer height: 0.16" from gcode
                with open(file, 'r') as f:
                    for line in f:
                        if ';Layer height:' in line:
                            layer_height = float(line.split(':')[1])
                            # check if layer height is consistent in all gcode files
                            if layer_height_value == 0:
                                print('Layer height:', layer_height)
                                layer_height_value = layer_height
                            if layer_height != layer_height_value:
                                print('Layer height is not consistent in file:', file)
                                print('Expected:', layer_height_value)
                                print('Aborting...')
                                sys.exit(1)

                copy_line = False
                with open(file, 'r') as f:
                    for line in f:
                        #print(line)
                        # other method to detect if layer height is changed
                        #if line.endswith('Z' + str(current_layer_height) + '\n' ):
                        if line == ';LAYER:' + str(current_layer_number) + '\n':
                            print(f'Layer {current_layer_number} detected! Start copying lines from file: {file}')
                            copy_line = True
                            # only put commands to change filament when color it's different from the last color
                            if color != last_color:
                                last_color = color
                                with open(output_filename, 'a') as output_file:
                                    output_file.write('; Start copying lines from file: ' + file + '\n')
                                    # first disable cooler, because it's not working with Qidi 3D printer
                                    output_file.write('M107 ; Turn off fan\n')
                                    # set temperature
                                    if color in temperatures:
                                        output_file.write('M104 S' + str(temperatures[color]) + '\n')
                                    else:
                                        print('Color not found in temperatures:', color)
                                        print('Aborting...')
                                        sys.exit(1)                                
                                    # pause to change filament
                                    output_file.write('; Pause to change filament\n')
                                    output_file.write('M300 I9000 ;Buzzer sounds\n')
                                    output_file.write('M25 ; Pause print to change filament\n')
                                    # wait for temperature
                                    if color in temperatures:
                                        output_file.write('M109 S' + str(temperatures[color]) + '\n')
                                    # if layer is the first, set E value to 0
                                    if current_layer_number == 0:
                                        output_file.write('G92 E0\n')
                                    else:
                                        # set last E value for this color
                                        if color in e_values:
                                            output_file.write('G92 E' + e_values[color] + '\n')
                                    # copy line to new file
                                    output_file.write(line)
                                    continue
                            
                        if copy_line:
                            # detect the last E value to use in the next file
                            if line.startswith(('G0', 'G1')) and ' E' in line:
                                e_value = line.split(' E')[1].split(' ')[0]
                                # insert E value in dictionary with actual color to use in the next file
                                e_values[color] = e_value
                                # other method to detect if layer height is changed
                                # if line.endswith('Z' + str(round(current_layer_height + layer_height_value, 2)) + '\n'):
                                #     print('Next layer detected, stop of copying lines from file:', file)
                                #     copy_line = False
                                #     continue
                            if line == ';LAYER:' + str(current_layer_number + 1) + '\n':
                                print('Next layer detected, stop of copying lines from file:', file)
                                copy_line = False
                                continue
                            # detect end of file on each color
                            if 'M106 T-2 S0\n' in line:
                                copy_line = False
                                # only stop script when black color has this line - back color is the last color to be printed
                                if color == 'black':
                                    print('End of file detected, stop of copying lines from file:', file)
                                    stay_copying = False
                                    break
                                continue
                            with open(output_filename, 'a') as output_file:
                                output_file.write(line)
        # other method to detect if layer height is changed                               
        #current_layer_height = round(current_layer_height + layer_height_value, 2)
        current_layer_number += 1

if __name__ == "__main__": 
    output_filename = 'merged.gcode'
    
    # set temperatures for each color, because each color may have different suplier and may have different melting point
    # see the folder temperature_tower to find the best temperature for each color
    temperatures = {
        'black': 210,
        'white': 160,
        'red': 210,
        'blue': 210,
        'green': 210,
    }
 
    remove_merged_gcode(output_filename)
    start_copying_gcode(output_filename)
    process_gcode_files(output_filename)
    end_copying_gcode(output_filename)
    
    print('Done')
    sys.exit(0)