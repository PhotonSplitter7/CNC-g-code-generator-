import math

def generate_hole_coordinates(hole_diameter, num_holes, z_height=3.5, feed_rate=400):
    radius = hole_diameter  # diameter should actually be divided by 2 to get radius
    coordinates = []
    gcode_lines = []
    desmos_points = []

    for i in range(num_holes):
        angle = (2 * math.pi / num_holes) * i
        x = round(radius * math.cos(angle), 4)
        y = round(radius * math.sin(angle), 4)
        z = z_height

        coord_str = f"hole {i+1}: [ x {x}, y {y}, z {z} ]"
        gcode_str = f"g1 x{x} y{y} z{z} f{feed_rate}"
        desmos_points.append(f"({x}, {y})")

        coordinates.append(coord_str)
        gcode_lines.append(gcode_str)

    return coordinates, gcode_lines, desmos_points

def save_to_file(filename, coordinates, gcode_lines):
    with open(filename, 'w') as f:
        for coord, gcode in zip(coordinates, gcode_lines):
            f.write(f"{coord} {gcode}\n")

def main():
    hole_diameter = float(input("Enter diameter of circular pattern: "))
    num_holes = int(input("Number of holes: "))

    coords, gcode, desmos = generate_hole_coordinates(hole_diameter, num_holes)  # divide diameter by 2 to get radius
    save_to_file("holePattern.txt", coords, gcode)

    print("\nDesmos-formatted points:")
    for point in desmos:
        print(point)

    print("\nData saved to 'holePattern.txt'.")

if __name__ == "__main__":
    main()
