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
                if line.startswith(('G0 F4800')) and ' Z0.3' in line:
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
    stay_copying = True
    
    while stay_copying:
        for file in os.listdir():
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
                        if line.endswith('Z' + str(current_layer_height) + '\n' ):
                            print(f'Layer {current_layer_height} detected! Start copying lines from file: {file}')
                            copy_line = True
                            with open(output_filename, 'a') as output_file:
                                output_file.write('; Start copying lines from file: ' + file + '\n')
                                # pause to change filament
                                output_file.write('; Pause to change filament\n')
                                output_file.write('M25\n')
                                output_file.write(line)
                                # set temperature
                                if color in temperatures:
                                    #output_file.write('M104 S' + str(temperatures[color]) + '\n')
                                    output_file.write('M109 S' + str(temperatures[color]) + '\n')
                                else:
                                    print('Color not found in temperatures:', color)
                                    print('Aborting...')
                                    sys.exit(1)
                                continue
                            
                        if copy_line:
                            if line.startswith(('G0', 'G1')):
                                if line.endswith('Z' + str(round(current_layer_height + layer_height_value, 2)) + '\n'):
                                    print('Next layer detected, stop of copying lines from file:', file)
                                    copy_line = False
                                    continue
                                with open(output_filename, 'a') as output_file:
                                    output_file.write(line)
                            else:
                                if line == 'M106 T-2 S0\n':
                                    print('End of file detected, stop of copying lines from file:', file)
                                    copy_line = False
                                    stay_copying = False
                                    break
        current_layer_height = round(current_layer_height + layer_height_value, 2)

if __name__ == "__main__": 
    output_filename = 'merged.gcode'
    
    # set temperatures for each color, because each color may have different suplier and may have different melting point
    # see the folder temperature_tower to find the best temperature for each color
    temperatures = {
        'black': 200,
        'white': 160,
        'red': 200,
        'blue': 200,
        'green': 200,
    }
 
    remove_merged_gcode(output_filename)
    start_copying_gcode(output_filename)
    process_gcode_files(output_filename)
    end_copying_gcode(output_filename)
    
    print('Done')
    sys.exit(0)