import pandas as pd
import numpy as np
import subprocess
import os
import shutil
from pdf2image import convert_from_path
from django.conf import settings
import math

def is_valid(x, y, x_min, x_max, y_min, y_max, width=None, length=None, radius=None):
    """
    Function to check if a given value is valid based on the layout grid

    Parameters:
    x (float): The x-coordinate of the object
    y (float): The y-coordinate of the object
    x_min (float): The minimum x-coordinate of the layout grid
    x_max (float): The maximum x-coordinate of the layout grid
    y_min (float): The minimum y-coordinate of the layout grid
    y_max (float): The maximum y-coordinate of the layout grid
    width (float): The width of the object
    length (float): The length of the object
    radius (float): The radius of the object

    Returns:
    boolean : True or False based on if the value is valid.
    If False, then a specific error message is returned.
    """
    if x < x_min or x > x_max:
        message = f"Invalid input for x-coordinate. Please enter a coordinate between {x_min} and {x_max}."
        return False, message
    
    if y < y_min or y > y_max:
        message = f"Invalid input for y-coordinate. Please enter a coordinate between {y_min} and {y_max}."
        return False, message
    
    if width and (width < 0):
        message = f"Invalid input for furniture width. Please enter a value greater than 0 and within range of layout grid."
        return False, message
    
    if length and (length < 0 or length > abs(y_max-y_min)):
        message = f"Invalid input for furniture length. Please enter a value greater than 0 and within range of layout grid."
        return False, message
    
    if radius and (radius < 0 or radius > abs(x_max-x_min) or radius > abs(y_max-y_min)):
        message = f"Invalid input for furniture radius. Please enter a value greater than 0 and within range of layout grid."
        return False, message
    
    message = "success"
    return True, message

def conversion(file, layout_style, labels):
    """
    Function to convert previously generated layouts with new formatting from "Edit Layout" page.

    Parameters:
    file (Excel): The excel file associated with the layout.
    layout_style (list): The new layout style from the "Edit Layout" page.
    labels (list) : The positioning of layout elements labels.

    Returns:
    boolean : True or False based on if the conversion was succesful. If False, then a specific error message is returned.
    """
    # Read Excel data 
    excel_data = pd.read_excel(os.path.join(settings.MEDIA_ROOT, 'imported_files', file))

    # drop empty rows
    excel_data = excel_data.dropna(how='all')
    excel_data.reset_index(drop=True, inplace=True)
    # print(excel_data)
  
    # Convert first row and first column to lowercase
    excel_data.columns = excel_data.columns.str.lower()
    excel_data['type'] = excel_data['type'].str.lower()

    # print("CALLING CONVERSION CODE:", file)
    
    # Define LaTeX template
    latex_walls_template = "\\draw[wall, line width={width}pt, color={color}] ({x1},{y1}) -- ({x2},{y2});\n".format(width='{}',color=layout_style.wall_color, x1='{:.2f}',y1='{:.2f}',x2='{:.2f}',y2='{:.2f}')  # Wall color is not changing on edit layout page
   
    # Define LaTeX template for furniture
    latex_rectangle_furniture_template = "\\furnitureR[height={h1}, width={w1}, rotate={r1}]({a1}, {a2});\n".format(h1='{}',w1='{}', r1='{}', a1='{}',a2='{}')
    latex_circle_furniture_template = "\\furnitureC[radius={a1}]({a2}, {a3});\n".format(a1='{}', a2='{}', a3='{}')
    latex_furniture_label_template = "\\node[furniture-label, text={color}, scale={s1}] at ({a1},{a2}) {a3};\n".format(color=layout_style.furniture_color, s1='{}', a1='{}', a2='{}', a3='{{{}}}')

    # Define LaTeX template for windows
    latex_windows_template = "\\draw[window,line width={width}pt, color={color}] ({x1},{y1}) -- ({x2},{y2});\n".format(width='{}', color=layout_style.window_color, x1='{:.2f}',y1='{:.2f}',x2='{:.2f}',y2='{:.2f}')

    # Define LaTeX template for sensors
    latex_sensor_template = "\\node[sensor, color={color}, scale={s0}, inner sep={width}mm](sensor) at ({s1},{s2}) {{{s3}}};\n".format(s0 = '{}',color=layout_style.sensor_label_color,s1='{}',s2='{}',s3='{}', width = '{width}')
    latex_sensor_label_template = "\\node[sensor-label,yshift=3pt,above,text={color},scale={s0}] at ({x1},{y1}) {a1};\n".format(s0 = '{s0}',color=layout_style.sensor_label_color,x1='{s1:.2f}',y1='{s2:.2f}',a1='{{{s3} \\\\ ({s1:.2f}, {s2:.2f})}}')
    latex_sensor_label_edit_template = "\\node[sensor-label,{shift},{location},scale={s0},text={color}] at ({x1},{y1}) {a1};\n".format(shift='{}',location='{}',s0='{s0}',color=layout_style.sensor_label_color,x1='{s1:.2f}',y1='{s2:.2f}',a1='{{{s3} \\\\ ({s1:.2f}, {s2:.2f})}}')

    # Define LaTeX template for cameras
    latex_camera_template = "\\camera[color={color},rotate={c1}, inner sep={width}mm]({c2},{c3});\n".format(s0 = '{}',color=layout_style.camera_label_color, c1='{}',c2='{}',c3='{}', width = '{width}')
    latex_camera_label_template = "\\node[camera-label,yshift=3pt,above,text={color}, scale={s0}] at ({c1},{c2}) {c3};\n".format(s0 = '{}',color=layout_style.camera_label_color,c1='{}',c2='{}',c3='{{{}}}')
    latex_camera_label_edit_template = "\\node[camera-label,{shift},{location},scale={scale},text={color}] at ({c1},{c2}) {c3};\n".format(shift='{}',location='{}',scale='{}',color=layout_style.camera_label_color,c1='{}',c2='{}',c3='{{{}}}')

    # Define LaTeX template for calibration locations
    latex_calibration_template = "\\node[location, color={color}, scale={s0}, inner sep={width}mm]({l1}) at ({l2},{l3}) {{{l4}}};\n".format(s0 = '{}',color=layout_style.calibration_color,l1='{}',l2='{}',l3='{}',l4='{}', width = '{width}')
    latex_calibration_label_template = "\\node[location-label,yshift=3pt,above, text={color}, scale={s0}] at ({l1}) {l2};\n".format(s0 = '{}',color=layout_style.calibration_color,l1='{}',l2='{{{}}}')
    latex_calibration_label_edit_template = "\\node[location-label,{shift},{location}, scale={scale}, text={color}] at ({l1}) {l2};\n".format(shift='{}',location='{}',scale='{}',color=layout_style.calibration_color,l1='{}',l2='{{{}}}')
    
    # Define LaTeX template for doors
    latex_door_template = "\\draw[door, rotate around={a}, line width={width}pt, color={color}] ({x1},{y1}) -- ++({x2},{y2});\n".format(a='{{{d1:.2f}:({d2:.2f},{d3:.2f})}}', width='{door_width:.2f}',color=layout_style.door_color, x1='{d2:.2f}',y1='{d3:.2f}', x2='{d4:.2f}',y2='{d5:.2f}')
    
    # Define LaTeX template for room navigation
    latex_room_nav_template = (f"\\draw[nav-arrow,color={layout_style.navigation_arrow_color},{{{{Stealth[scale={{scale}}]}}}}-] ({{r1}},{{r2}}) -- ++({{r3}},{{r4}}) node[{{r5}}, fill=white] {{{{{{r6}}}}}};\n")
    latex_room_nav_no_desc = (f"\\draw[nav-arrow,color={layout_style.navigation_arrow_color},{{{{Stealth[scale={{scale}}]}}}}-] ({{r1}},{{r2}}) -- ++({{r3}},{{r4}});\n")

    # Define LaTeX template for furniture styling
    latex_furniture_styling = """
    \\def\\furnitureR[height=#1, width=#2, rotate=#3](#4, #5){{%
	% Draws a rectangular furniture piece centered on provided coordinates in a Tikz picture
	% \\furnitureR[height=<value>, width=<value>, rotate=<degrees>](<x>, <y>)
	\\draw[line width={width}pt, color={color}, rotate around={{#3:(#4,#5)}}] (#4-#2/2, #5-#1/2) rectangle (#4+#2/2, #5+#1/2)  
    }}

    \\def\\furnitureC[radius=#1](#2, #3){{%
	    % Draws a circular furniture piece centered on provided coordinates in a Tikz picture
	    % \\furnitureC[radius=<value>](<x>, <y>)
	    \\draw[line width={width}pt, color={color}] (#2, #3) circle (#1)
    }}

    """.format(width=max(layout_style.furniture_width, 0.5), color=layout_style.furniture_color)

    # Get data for X and Y axes
    # check that 'X axis' exists in data
    if (excel_data['type'] == 'x axis').any():
        x_axis_data = excel_data[excel_data['type'] == 'x axis'].iloc[0]
    
    else:
        message = f"Invalid input. No data found for X axis."
        return {'success': False, 'message': message}
    
    # check the Y Axis exists in data
    if (excel_data['type'] == 'y axis').any():
        y_axis_data = excel_data[excel_data['type'] == 'y axis'].iloc[0]
    
    else:
        message = f"Invalid input. No data found for Y axis."
        return {'success': False, 'message': message}

    # Get minimum and maximum values for X axis
    x_step = x_axis_data['step']
    y_step = y_axis_data['step']

    x_min = x_step*math.floor(x_axis_data['min']/x_step) if x_axis_data['min'] < 0 else x_step*math.ceil(x_axis_data['min']/x_step)
    x_max = x_step*math.floor(x_axis_data['max']/x_step) if x_axis_data['max'] < 0 else x_step*math.ceil(x_axis_data['max']/x_step)
    
    if not is_numeric(x_min) or not is_numeric(x_max):
        message = f"Invalid input types for X axis min/max values. Please enter real numbers."
        return {'success': False, 'message': message}
    
    y_min = y_step*math.floor(y_axis_data['min']/y_step) if y_axis_data['min'] < 0 else y_step*math.ceil(y_axis_data['min']/y_step)
    y_max = y_step*math.floor(y_axis_data['max']/y_step) if y_axis_data['max'] < 0 else y_step*math.ceil(y_axis_data['max']/y_step)
    
    if not is_numeric(y_min) or not is_numeric(y_max):
        message = f"Invalid input types for Y axis min/max values. Please enter real numbers."
        return {'success': False, 'message': message}
    
    # Check furniture bounds and extend layout if needed
    furniture_data = excel_data[excel_data['type'] == 'furniture']
    for _, row in furniture_data.iterrows():
        
        if row['furniture_type'].lower() == 'rectangle':
            # x bounds
            if row['x'] - row['width']/2 < x_min:
                # math floor
                x_min = x_step * math.floor((row['x'] - row['width']/2)/x_step)
            if row['x'] + row['width']/2 > x_max:
                x_max = x_step * math.ceil((row['x'] + row['width']/2)/x_step)
                
            # y bounds    
            if row['y'] - row['length']/2 < y_min:
                y_min = y_step * math.floor((row['y'] - row['length']/2)/y_step)
            if row['y'] + row['length']/2 > y_max:
                y_max = y_step * math.ceil((row['y'] + row['length']/2)/y_step)
                
        elif row['furniture_type'].lower() == 'circle':
            # Check x bounds
            if row['x'] - row['radius'] < x_min:
                x_min = x_step * math.floor((row['x'] - row['radius'])/x_step)
            if row['x'] + row['radius'] > x_max:
                x_max = x_step * math.ceil((row['x'] + row['radius'])/x_step)
                
            # Check y bounds
            if row['y'] - row['radius'] < y_min:
                y_min = y_step * math.floor((row['y'] - row['radius'])/y_step)
            if row['y'] + row['radius'] > y_max:
                y_max = y_step * math.ceil((row['y'] + row['radius'])/y_step)

    x_step = 0 if x_min == x_max else x_step
    y_step = 0 if y_min == y_max else y_step

    x_values = "{0}" if x_step == 0 else "{{{a1},{a2},...,{a3}}}".format(a1=x_min, a2=x_min+x_step, a3=x_max)
    y_values = "{0}" if y_step == 0 else "{{{a6},{a7},...,{a8}}}".format(a6=y_min, a7=y_min+y_step, a8=y_max)
    
    latex_gridline_template = """
        %% GRID - X
        \\foreach \\i in {x_values}{{
            \\draw[grid-line] (\\i,{a4}) -- (\\i,{a5});
            \\tikzmath{{int \\value; \\value = \\i;}}; 
            \\node[gray, below] at (\i,{a4}) {{\\SI{{\\value}}{{\\inch}}}};
        }}

        %% GRID - Y
        \\foreach \\i in {y_values}{{
            \\draw[grid-line] ({a9},\\i) -- ({a10},\\i);
            \\tikzmath{{int \\value; \\value = \\i;}};
            \\node[gray, left] at ({a9},\i) {{\\SI{{\\value}}{{\\inch}}}};
        }}
    """.format(a4=y_min-5, a5=y_max+5, a9=x_min-5, a10=x_max+5, x_values=x_values, y_values=y_values)

    # Iterate through rows and generate LaTeX code for walls and furniture
    latex_exterior = ""
    latex_furniture = ""
    latex_cameras = ""
    latex_sensors = ""
    latex_calibrations = ""
    latex_room_nav = ""

    # Declaring variables to hold metadata
    latex_date = ""
    latex_room_name = ""
    latex_neighborhood = ""
    latex_building = ""
    latex_orientation = layout_style.orientation

    # Defining allowed values for data validation
    WALL = 'wall'
    WINDOW = 'window'
    DOOR = 'door'
    FURNITURE = 'furniture'

    # Toggle wall and window pairs to draw line segments separately
    toggle_pair = False

    # Parse through uploaded Excel file
    for index, row in excel_data.iterrows():
        descriptor = row['descriptor']
        row_type = row['type']
        
        # Prevent parsing lines that don't contain data
        if row_type in ['x axis', 'y axis']:
            continue
        
        if pd.isna(descriptor) or pd.isna(row_type):
            continue
        
        # if is_numeric(descriptor) or is_numeric(row_type):
        #     continue

        elif row_type.lower() in [WALL, WINDOW] and index <= len(excel_data) - 1:
            x1 = row['x']
            y1 = row['y']
            width = row['width']
            toggle_pair = not toggle_pair

            if toggle_pair:

                if pd.isna(width) or width <= 0.0:
                    width = layout_style.wall_width if row_type.lower() == WALL else layout_style.window_width
                            
                length = row['length']

                data_valid, message = is_valid(x1, y1, x_min, x_max, y_min, y_max, width, length)
                
                if not data_valid:
                    return {'success': False, 'message': message}
                
                if index == len(excel_data) - 1 or not excel_data.iloc[index + 1]['type'] in [WALL, WINDOW]:
                    # If the next row is not exterior
                    x2 = x1  # Set x2 to the same as x1
                    y2 = y1  # Set y2 to the same as y1
                
                else:
                    # If the next row is another exterior
                    x2 = excel_data.at[index + 1, 'x']
                    y2 = excel_data.at[index + 1, 'y']
                
                latex_exterior += latex_walls_template.format(width, x1, y1, x2, y2) if row_type.lower() == WALL else latex_windows_template.format(width, x1, y1, x2, y2)
            
        elif row_type.lower() == DOOR and index <= len(excel_data) - 1:
            x = row['x']
            y = row['y']
            door_angle = row['rotation']
            door_width = row['width'] 
            
            if pd.isna(door_width) or door_width <= 0.0:
                door_width = layout_style.door_width
            
            if (not is_numeric(door_angle)) or door_angle < -360 or door_angle > 360:
                message = f"Invalid input type for door rotation in row {index+2}. Please enter a number between 0 - 360."
                return {'success': False, 'message': message}
            
            data_valid, message = is_valid(x, y, x_min, x_max, y_min, y_max, width=door_width)
            
            if not data_valid:
                return {'success': False, 'message': message}

            door_xy = row['room_navigation_direction'] if not pd.isna(row['room_navigation_direction']) else 'left'
            radians = math.radians(door_angle)
            cos_theta = math.cos(radians)
            sin_theta = math.sin(radians)

            # check direction of door_xy
            if type(door_xy) in [str]:
                door_xy = door_xy.lower()
                
                if not is_numeric(row['length']):
                    message = f"Invalid input type for length in row {index+2}. Please enter a real number."
                    return {'success': False, 'message': message}
                
                if(door_xy == 'left' and x - row['length']*cos_theta >= x_min and y - row['length']*sin_theta >= y_min):
                    door_x = -row['length']
                    door_y = 0
                
                elif(door_xy == 'right' and x + row['length']*cos_theta <= x_max and y + row['length']*sin_theta <= y_max):
                    door_x = row['length']
                    door_y = 0
                
                elif(door_xy == 'up' and y + row['length']*sin_theta <= y_max) and x + row['length']*cos_theta <= x_max:
                    door_x = 0
                    door_y = row['length']
                
                elif(door_xy == 'down' and y - row['length']*sin_theta >= y_min and x - row['length']*cos_theta >= x_min):
                    door_x = 0
                    door_y = -row['length']
                
                else:
                    message = f"Invalid input type for door direction in row {index+2}."
                    print(message)  
                    return {'success': False, 'message': message}
            
            else:
                message = f"Invalid input type for door direction in row {index+2}. Please enter either left, right, down, or up."
                return {'success': False, 'message': message}
            
            latex_exterior += latex_door_template.format(d1=door_angle, d2=x, d3=y, d4=door_x, d5=door_y, door_width=door_width)

        elif row_type == FURNITURE and row['furniture_type'].lower() == 'rectangle':
            width = row['width']
            length = row['length']
            rotation = row['rotation']
            x = row['x']
            y = row['y']
            scale = row['scale']
            
            if pd.isna(scale):
                scale = 1.0

            data_valid, message = is_valid(x, y, x_min, x_max, y_min, y_max, width, length)
            
            if not data_valid:
                return {'success': False, 'message': message}
            
            if x - width/2 < x_min or x + width/2 > x_max or y - length/2 < y_min or y + length/2 > y_max:
                message = f"Invalid input for rectangle furniture in line {index+2}. Please ensure the rectangle fits within the layout grid."
                return {'success': False, 'message': message}
            
            latex_furniture += latex_rectangle_furniture_template.format(length, width, rotation, x, y)
            latex_furniture += latex_furniture_label_template.format(scale, x, y, descriptor) if descriptor != ' ' else ''

        elif row_type == FURNITURE and row['furniture_type'].lower() == 'circle':
            radius = row['radius']
            x = row['x']
            y = row['y']
            scale = row['scale']
            
            if pd.isna(scale):
                scale = 1.0

            data_valid, message = is_valid(x, y, x_min, x_max, y_min, y_max, radius=radius)
            
            if not data_valid:
                return {'success': False, 'message': message}
            
            if x - radius < x_min or x + radius > x_max or y - radius < y_min or y + radius > y_max:
                message = f"Invalid input for circle furniture in line {index+2}. Please ensure the circle fits within the layout grid."
                return {'success': False, 'message': message}
            
            latex_furniture += latex_circle_furniture_template.format(radius, x, y)
            latex_furniture += latex_furniture_label_template.format(scale, x, y, descriptor) if descriptor != ' ' else ''

        elif row_type == FURNITURE and row['furniture_type'].lower() not in ['rectangle', 'circle']:
            message = f"Invalid value for furniture_type in row {index+2}. Please enter either 'rectangle' or 'circle'."
            print(message)
            return {'success': False, 'message': message}
        
        elif row_type == 'sensor':
            x = row['x']
            y = row['y']
            scale = row['scale']
            width = row['width']

            if pd.isna(scale):
                scale = 1.0
            
            if pd.isna(width) or pd.isnull(width) or width <= 0.0:
                width = 0.5
            
            data_valid, message = is_valid(x, y, x_min, x_max, y_min, y_max)
            
            if not data_valid:
                return {'success': False, 'message': message}

            latex_sensors += latex_sensor_template.format(scale, x, y, width=width)

            for label in labels:

                if label.name == row['descriptor'] and label.location == 'below':
                    latex_sensors += latex_sensor_label_edit_template.format('yshift=-5pt',label.location, s0=scale, s1=x, s2=y, s3=descriptor) if descriptor != ' ' else ''

                elif label.name == row['descriptor'] and label.location == 'left':
                    latex_sensors += latex_sensor_label_edit_template.format('xshift=-5pt',label.location, s0=scale, s1=x, s2=y, s3=descriptor) if descriptor != ' ' else ''

                elif label.name == row['descriptor'] and label.location == 'right':
                    latex_sensors += latex_sensor_label_edit_template.format('xshift=5pt',label.location, s0=scale, s1=x, s2=y, s3=descriptor) if descriptor != ' ' else ''

                elif label.name == row['descriptor']:
                    latex_sensors += latex_sensor_label_template.format(s0=scale,s1=x, s2=y, s3=descriptor) if descriptor != ' ' else ''
        
        elif row_type == 'camera':
            x = row['x']
            y = row['y']
            rotation = row['rotation']
            scale = row['scale']
            width = row['width']

            if pd.isna(width) or pd.isnull(width) or width <= 0.0:
                width = 0.5

            if pd.isna(scale):
                scale = 1.0
            
            if (is_numeric(rotation) and (rotation < 0 or rotation > 360)) or not is_numeric(rotation):
                message = f"Invalid input type for camera rotation in line {index+2}. Please enter a real number between 0-360."
                return {'success': False, 'message': message}
            
            data_valid, message = is_valid(x, y, x_min, x_max, y_min, y_max)
            
            if not data_valid:
                return {'success': False, 'message': message}

            latex_cameras += latex_camera_template.format(rotation, x, y, width=scale/2)

            for label in labels:

                if label.name == row['descriptor'] and label.location == 'below':
                    latex_cameras += latex_camera_label_edit_template.format('yshift=-8pt',label.location,scale,x,y,descriptor) if descriptor != ' ' else ''

                elif label.name == row['descriptor'] and label.location == 'left':
                    latex_cameras += latex_camera_label_edit_template.format('xshift=-4pt',label.location,scale,x,y,descriptor) if descriptor != ' ' else ''

                elif label.name == row['descriptor'] and label.location == 'right':
                    latex_cameras += latex_camera_label_edit_template.format('xshift=4pt',label.location,scale,x,y,descriptor) if descriptor != ' ' else ''

                elif label.name == row['descriptor']:
                    latex_cameras += latex_camera_label_template.format(scale,x,y,descriptor) if descriptor != ' ' else ''

        
        elif row_type == 'calibration':
            x = row['x']
            y = row['y']
            scale = row['scale']
            width = row['width']

            if pd.isna(width) or pd.isnull(width) or width <= 0.0:
                width = 0.5

            if pd.isna(scale):
                scale = 1.0
            
            data_valid, message = is_valid(x, y, x_min, x_max, y_min, y_max)
            
            if not data_valid:
                return {'success': False, 'message': message}
            
            latex_calibrations += latex_calibration_template.format(scale, descriptor, x, y, width=width)

            if descriptor != ' ':

                for label in labels:

                    if label.name == row['descriptor'] and label.location == 'below':
                        latex_calibrations += latex_calibration_label_edit_template.format('yshift=-6pt',label.location,scale,descriptor,descriptor) if descriptor != ' ' else ''

                    elif label.name == row['descriptor'] and label.location == 'left':
                        latex_calibrations += latex_calibration_label_edit_template.format('xshift=-6pt',label.location,scale,descriptor,descriptor) if descriptor != ' ' else ''

                    elif label.name == row['descriptor'] and label.location == 'right':
                        latex_calibrations += latex_calibration_label_edit_template.format('xshift=6pt',label.location,scale,descriptor,descriptor) if descriptor != ' ' else ''

                    elif label.name == row['descriptor']:
                        latex_calibrations += latex_calibration_label_template.format(scale,descriptor,descriptor) if descriptor != ' ' else ''
        
        elif row_type == 'room navigation':
            x = row['x']
            y = row['y']
            room_navigation_direction = row['room_navigation_direction'] if not pd.isna(row['room_navigation_direction']) else 'right'
            scale = row['scale']
            rotation = row['rotation']
            
            if row['length'] == 0 or pd.isna(row['length']):
                length = 12

            else:
                length = row['length']

            if rotation == 0 or pd.isna(rotation):
                rotation = 0

            if pd.isna(scale):
                scale = 1.0
            
            data_valid, message = is_valid(x, y, x_min, x_max, y_min, y_max)
            
            if not data_valid:
                return {'success': False, 'message': message}
            
            if room_navigation_direction not in ['left', 'right', 'up', 'down']:
                message = f"Invalid input type for room_navigation_direction in line {index+2}. Please enter either left, right, down, or up."
                return {'success': False, 'message': message}
            
            radians = math.radians(rotation)
            cos_theta = math.cos(radians)
            sin_theta = math.sin(radians)

            if room_navigation_direction == 'left':
                arrow_x = length * cos_theta
                arrow_y = length * sin_theta
                node_location = 'right'
            
            elif room_navigation_direction == 'right':
                arrow_x = -length * cos_theta
                arrow_y = -length * sin_theta
                node_location = 'left'
            
            elif room_navigation_direction == 'down':
                arrow_x = -length * sin_theta
                arrow_y = length * cos_theta
                node_location = 'above'
            
            elif room_navigation_direction == 'up':
                arrow_x = length * sin_theta
                arrow_y = -length * cos_theta
                node_location = 'below'
            
            else:
                message = f"Invalid input type for room navigation direction in row {index+2}. {room_navigation_direction}"
                print(message)  
                return {'success': False, 'message': message}
            
            if descriptor != ' ':
                latex_room_nav += latex_room_nav_template.format(scale=scale, r1=x, r2=y, r3=arrow_x, r4=arrow_y, r5=node_location, r6=descriptor)

            else:
                latex_room_nav += latex_room_nav_no_desc.format(scale=scale, r1=x, r2=y, r3=arrow_x, r4=arrow_y, r5=node_location)

        elif row_type == 'date':
            latex_date = descriptor
        
        elif row_type == 'room name':
            latex_room_name = descriptor
        
        elif row_type == 'neighborhood':
            latex_neighborhood = descriptor
        
        elif row_type == 'building':
            latex_building = descriptor
        
        elif row_type == 'orientation':
            orientation = layout_style.orientation
            
            if orientation not in ['portrait', 'landscape']:
                message = f"Invalid input type for orientation in line {index+2}. Please enter either 'portrait' or 'orientation'."
                return {'success': False, 'message': message}
            
            latex_orientation = orientation
    
    latex_scale = "1/{denom}".format(denom='{}')
    x_y_scale = "1"
    max_coord = max(x_max, y_max)
    min_coord = min(x_min, y_min)
    abs_max = abs(max_coord)
    gap = x_axis_data['step']
    
    if abs(min_coord) > abs(max_coord):
        abs_max = abs(min_coord)

    latex_paper_size = "papersize={{24in, 36in}}" if layout_style.orientation == "landscape" else "legalpaper"        
    scale_ranges = [
        (552, "1"),
        (1104, "0.5"),
        (2208, "0.25"),
        (4416, "0.125"),
        (8832, "0.0625"),
        # Pattern continues - each range doubles the previous max and halves the scale
    ]
    
    # Find appropriate scale range
    x_y_scale = "0.03125"  # Default for very large numbers
    for max_val, scale in scale_ranges:
        if abs_max <= max_val:
            x_y_scale = scale
            break
    
    # Calculate outer bound
    if (x_max > 0 and x_min < 0) or (y_max > 0 and y_min < 0):
        outer_bound = ((max_coord - min_coord) / gap) * gap 

    else:
        outer_bound = (math.ceil(abs_max / gap) if abs_max > 0 else math.floor(abs_max / gap)) * gap
    
    # Base multipliers for different paper sizes
    if latex_paper_size == "papersize={{24in, 36in}}":  # landscape
        base_multiplier = 0.5 if gap == 24 else 0.75
        min_denom = 0.2
        denom_addon = 0.2
    else:  # legal
        base_multiplier = 1.4 if gap == 24 else 2.1
        min_denom = 0.75
        denom_addon = 0.6 if x_step == 24 else 0.9
    
    # Scale the multiplier based on the x_y_scale
    scale_factor = float(x_y_scale)
    adjusted_multiplier = base_multiplier * scale_factor
    
    # Calculate denominator
    denom = (outer_bound / gap) * adjusted_multiplier
    
    if denom == 0:
        denom = min_denom * scale_factor
    else:
        denom += denom_addon * scale_factor
    
    latex_scale = f"1/{denom}"


    # Complete LaTeX code with autopopulated walls
    complete_latex_code = f"""
    %!TeX program = lualatex
    \\documentclass[12pt]{{article}}

    \\usepackage[hmargin=0.5in, tmargin=0.75in, bmargin=0.9in]{{geometry}}
    \\geometry{{{latex_paper_size}, {latex_orientation}}}
   
    \\usepackage{{graphicx}}  % graphic controls
    \\usepackage{{float}}  % positioning controls
    \\usepackage{{lastpage}}  % last page number finder
    \\usepackage{{makecell}}  % helpers for multilined table cells

    % header/footer
    \\usepackage{{fancyhdr}}
    \\pagestyle{{fancy}}

    \\lhead{{{latex_date}}}
    \\chead{{}}
    \\rhead{{\\footnotesize \\thepage \\ {{\\color{{gray}} of \\pageref{{LastPage}}}}}}

    \\cfoot{{}}
    \\rfoot{{\\textbf{{\\LARGE {latex_room_name}}}\\\\\\vspace{{3pt}}{{\\large\\color{{gray}}NIH STTR Phase II}}}}

    \\renewcommand{{\\headrulewidth}}{{0.25pt}}
    \\renewcommand{{\\footrulewidth}}{{0.25pt}}

    % drawing things
    \\usepackage{{tikz}}
    \\usetikzlibrary{{math, calc, shapes, arrows.meta}}

    \\tikzstyle{{grid-line}} = [gray, very thin]
    \\tikzstyle{{wall}} = [line width=2pt, line cap=round]
    \\tikzstyle{{window}} = [line width=1pt, line cap=round]
    \\tikzstyle{{door}} = [line width=1pt]
    \\tikzstyle{{furniture}} = [draw, line width=0.5pt, transform shape]
    \\tikzstyle{{furniture-label}} = [fill=white, align=center]
    \\tikzstyle{{sensor}} = [circle, draw, color=teal, fill=teal, inner sep=0.5mm]
    \\tikzstyle{{sensor-label}} = [above, yshift=2pt, fill=white, align=center, text=teal]
    \\tikzstyle{{location}} = [diamond, draw, color=violet, fill=violet, inner sep=0.5mm]
    \\tikzstyle{{location-label}} = [above, yshift=3pt, fill=white, text=violet]
    \\tikzstyle{{walking-path}} = [densely dashed, line width=0.25mm, -{{Stealth[length=4mm, width=2mm]}}]
    \\tikzstyle{{nav-arrow}} = [line width=0.25mm, {{Stealth[length=4mm, width=2mm]}}-, green!60!black]
    
    {latex_furniture_styling}

    \\def\camera[#1](#2,#3){{
	    \\node[circle, draw, color=blue!75!black, fill=blue!75!black, inner sep=0in, minimum size=0.1in, anchor=center, #1] at (#2,#3) {{}};
	    \\node[isosceles triangle, draw, color=blue!75!black, fill=blue!75!black, inner sep=0in, minimum size=0.1in, isosceles triangle apex angle=75, anchor=east, #1] at (#2,#3) {{}}
     }}

    \\tikzstyle{{camera-label}} = [fill=white, align=center, text=blue!75!black, above, yshift=8pt]

    % units
    \\usepackage{{siunitx}}
    \\sisetup{{per-mode = symbol}}

    \\let\\DeclareUSUnit\\DeclareSIUnit
    \\let\\US\\SI
    \\let\\us\\si
    \\DeclareUSUnit\\inch{{in}}
    \\DeclareUSUnit\\feet{{ft}}
    \\DeclareUSUnit\\foot{{ft}}
    \\DeclareUSUnit\\pound{{lb}}
    \\DeclareUSUnit\\slug{{slug}}

    % paragraph settings
    \\setlength{{\\parindent}}{{0em}}
    \\raggedright

    \\begin{{document}}
    \\vspace*{{\\stretch{1}}}  % Push figure down
    \\begin{{figure}}[H]
        \\centering

        \\begin{{tikzpicture}}[scale={latex_scale},  % use this to reduce or enlargen the image on paper
                               x={x_y_scale}cm,
                               y={x_y_scale}cm,
                               rotate=0]  % use this to rotate orientation by degrees on paper

    {latex_gridline_template}

    % Exterior walls
    {latex_exterior}

    % Furniture
    {latex_furniture}

    % Cameras
    {latex_cameras}

    % Sensors
    {latex_sensors}
    
    % Calibrations
    {latex_calibrations}

    % Room Navigation
    {latex_room_nav}

    
    \\end{{tikzpicture}}
    \\end{{figure}}
    \\vspace*{{\\stretch{1}}}  % Push figure up
    
    \\vspace*{{\\fill}}  % fills the area between the table and layout with whitespace, forcing the table to the bottom of the page.
    \\begin{{table}}[H]
	\\begin{{tabular}}{{l l}}
		\\makecell[lt]{{
			\\textbf{{Location:}}\\\\
     		{latex_neighborhood} Neighborhood \\\\
 		    {latex_building} Bldg, Still Hopes\\\\
           	1 Still Hopes Drive\\\\
           	West Columbia, SC 29033\\\\\\\\
        }}   	
        &	
		\\makecell[tp{{5in}}]{{
		\\textbf{{Notes:}}\\\\
		\\vspace{{-8mm}}  % reduce whitespace created by itemize above list
		\\begin{{itemize}}
			\\setlength\\itemsep{{-3mm}}  % reduce whitespace created by itemize between lines
			\\item Measurements are to the nearest \SI{{0.25}}{{\inch}}
			\\item The furniture locations are approximate.
			\\item Laptop and data acquisition system is located beside the table.
			\\item Cameras are located on the ceiling.
		\\end{{itemize}}
		}}	
			
	\\end{{tabular}}
	\\vspace{{-8mm}} % reduce whitespace after table
\\end{{table}}

    \\end{{document}}
    """
    # Print or save LaTeX code
    print(complete_latex_code)

    # Save LaTeX code to a .tex file
    tex_file_path = 'output.tex'
    
    with open(tex_file_path, 'w') as f:
        f.write(complete_latex_code)

    # Run the LaTeX compiler (lualatex) to generate the PDF
    process = subprocess.run(['lualatex', tex_file_path])

    # Check if the compilation was successful
    if process.returncode == 0:
        print("PDF generated successfully.") # Specify the destination folder

        pdf_destination_folder = os.path.join(settings.MEDIA_ROOT, 'conversion_output', 'output.pdf')
        tex_destination_folder = os.path.join(settings.MEDIA_ROOT, 'conversion_output', 'output.tex')
        aux_destination_folder = os.path.join(settings.MEDIA_ROOT, 'conversion_output', 'output.aux')
        log_destination_folder = os.path.join(settings.MEDIA_ROOT, 'conversion_output', 'output.log')
        
        # Move the generated PDF to the destination folder
        try:
            shutil.move('output.pdf', pdf_destination_folder)
            shutil.move('output.tex', tex_destination_folder)
            shutil.move('output.aux', aux_destination_folder)
            shutil.move('output.log', log_destination_folder)
        
        except Exception as e:
            print(f"Error moving files: {e}")
        
        # Delete current output.png and replace with updated one
        output_path = os.path.join(settings.MEDIA_ROOT, 'conversion_output', 'output.png')
        png = convert_from_path(pdf_destination_folder)
        
        for i, image in enumerate(png):
            image.save(f'{output_path}', 'PNG')
        
        return {'success': True, 'message': ''}

    else:
        print("Error during PDF generation. Check the LaTeX log for details.")
        return {'success': False, 'message': 'Error occurred during PDF generation.'}

def is_numeric(value):
    """
    Check if a value is numeric and not NaN
    """
    if pd.isna(value):
        return False
        
    try:
        float_val = float(value)
        return not math.isnan(float_val)
    except (ValueError, TypeError):
        return False