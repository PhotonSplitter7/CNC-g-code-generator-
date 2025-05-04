import math

def generate_hole_coordinates(hole_diameter, num_holes, feed_rate=400):
    radius = hole_diameter  # diameter should actually be divided by 2 to get radius
    coordinates = []
    gcode_lines = []
    desmos_points = []

    for i in range(num_holes):
        angle = (2 * math.pi / num_holes) * i
        x = round(radius * math.cos(angle), 4)
        y = round(radius * math.sin(angle), 4)

        coord_str = f"hole {i+1}: [ x {x}, y {y} ]"
        gcode_str = f"g1 x{x} y{y} f{feed_rate}"
        desmos_points.append(f"({x}, {y})")

        coordinates.append(coord_str)
        gcode_lines.append(gcode_str)

    return coordinates, gcode_lines, desmos_points

def save_to_file(filename, str):
    with open(filename, 'w') as f:
        f.write(str)
        f.close()

def main():
    hole_diameter = float(input("Enter diameter of circular pattern: "))
    num_holes = int(input("Number of holes: "))
    hole_depth = float(input("Depth of holes to drill: ")) * -1
    #3mm peck distance 
    peck_distance = float(input("Peck distance: "))
    peck_speed = float(input("Peck speed: "))

    #string to hold full file
    str = ""


    coords, gcode, desmos = generate_hole_coordinates(hole_diameter, num_holes)  # divide diameter by 2 to get radius
    

    #print out sequence of drills 
    for drill_hole in gcode:
        #z pos
        z = 10.0
        #clear drill bit
        str += f"G1 Z{z} F1000\n"
        #move to drill point
        str +=  drill_hole + "\n"
        z = 1.0
        #drill
        str += f"G1 Z{z} F1000\n"
        while(z > hole_depth):
            
            z = z - peck_distance

            if z < (hole_depth):
                str += f"G1 Z{hole_depth} F{peck_speed}\n"
            else:
                #peck
                str += f"G1 Z{z} F{peck_speed}\n"
                #raise to top
                z = z + peck_distance
                str += f"G1 Z{z} F1000\n"
                z = z - peck_distance

    #save to file
    filename = input("Enter filename: ")
    save_to_file(f"{filename}.ngc", str)
        


if __name__ == "__main__":
    main()
