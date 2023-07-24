import string, math

#modifiers for reversing axis
def reverse(coorinate):
    if coordinate > 0:
        return -coordinate
    else:
        return coordinate



#range function can count up or down with number of steps for floats depending on start and stop value size
def range(start,stop,step):
    step = float(step)
    start = float(start)
    stop = float(stop)
    sequence = [start]
    #count down
    if start > stop:
        while start > stop:
            start = round(start-step,4)
            if start < stop:
                sequence.append(stop)
            else:
                sequence.append(start)
    #count up
    else:
        while start < stop:
            start = round(start+step,4)
            if start > stop:
                sequence.append(stop)
            else:
                sequence.append(start)
    return sequence

#makes g1 g code returns string
def g1(x,y,z,f):
    x = float(x)
    y = float(y)
    z = float(z)
    f = float(f)
    code = "g1 X" + str(round(x,4)) + " Y" + str(round(y,4)) + " Z" + str(round(z,4)) + " F" + str(round(f,4))+ "\n"
    return code

def switch_direction(current_direction,direction1,direction2):
    if current_direction == direction1:
        return direction2
    else:
        return direction1

#returns gcode to left or right of origin
def safe_spot(direction,tool_diam):
    if direction > 0:#go up, then move head to right of origin
        return "g1 z50 f1000\n g1 x" + str(tool_diam+6) + " y0 f1000\n"
    if direction == 0:#hold x and y pos, go up
        return "g1 z50 f1000\n"
    else:
        return "g1 z50 f1000\n g1 x" + str(-tool_diam-6) + " y0 f1000\n"



#facing function faces part. at the moment it starts in upper left hand corner at 0,0, and works to right bottom corner
def face(x,y,z,f,step_down,tool_diam, tool_overlap):
    x = float(x)
    y = float(y)
    z = float(z)
    f = float(f)
    tool_diam = float(tool_diam)
    step_down = float(step_down)
    tool_overlap = float(tool_overlap)
    xmin = 0.0
    xmax = x
    xpos = xmin
    ymin = 0.0
    ymax = y
    ystepdown = tool_diam
    #gcode for safe zone to lower head
    safe_space = "g1 x" + str(-6-tool_diam) + " y0 f1000 \n"

    #g code init raises head and positions to left of part, then lowers to correct position
    gcode = "g1 z10 f1000"
    gcode += "\n"
    gcode += "g1 x0 y0 z10 f1000"
    gcode += "\n"

    #outer loop z axis. stops when reaches z amount to remove
    for zpos in range(0,-z,step_down):
        gcode += "#start z step down\n"
        #move head down
        gcode += "g1 z" + str(zpos) + " f300"
        gcode += "\n"
        #move cutter towards user, so Y axis decreases ISSUE LAST 2 MOVES ARE DIAGONAL becouse line 77. ypos + ystepdown alwasy the same
        for ypos in range(ymin,ymax,ystepdown):
            gcode += g1(xpos,ypos,zpos,f)#move down cutter
            xpos = switch_direction(xpos,xmin,xmax)
            gcode += g1(xpos,ypos,zpos,f)

        gcode += "#end face\n"
        gcode += safe_space#once facing done move to safe space then lower head
        gcode += "g1 z" + str(zpos) + " f300"



    return gcode


#these functions are for cutting rounds

#gets tangent intercept to radius. calculates stepdown to get tangent to radius.
def get_circular_intercept(radius,vertical_intercept):
    y= vertical_intercept
    #if z touching top of arc, x axis is 0
    if vertical_intercept == radius:
        x = 0
    else:
        x = math.sqrt((radius*radius)-(vertical_intercept*vertical_intercept))
    return x#abs() maybe?

#this code cuts a radius using stepdowns for resolution of curve. Radius center axis is X or Y
def cut_radius(radius,z_start,z_stop,stepdown,x_length,tool_diam,mirror_y):#cuts radius facing toward user, with origin being center of radius, on right side of it
    radius = float(radius)
    z_stop = float(z_stop)
    z_start = float(z_start)
    x_length = float(x_length)
    tool_diam = float(tool_diam)
    empty_space = tool_diam+3
    head_park_coordinates = safe_spot(1,tool_diam)
    gcode = head_park_coordinates#start tool at right of origin in safe space

    for zpos in range(z_start,z_stop,stepdown):
        #get intercept point for y axis of machine in relation to z position
        ypos = get_circular_intercept(radius,zpos)
        #offset tool diameter
        ypos += tool_diam/2
        if mirror_y:
            ypos = -ypos
        #move head to right of part 3mm off edge at z level
        gcode += g1(empty_space,ypos,zpos,feedrate)
        #start cut
        gcode += g1(-x_length-tool_diam/2,ypos,zpos,feedrate)
        #move head back
        gcode += g1(empty_space,ypos,zpos,feedrate)
        #retract head to finish
    gcode += head_park_coordinates
    return gcode

#cuts a pocket: boundry is a list of points forming boundry of pocket x and y are center of pocket
def cut_pocket(x,y,width,length,depth,stepdown,tool_diam,feedrate):
    x = float(x)
    y = float(y)
    width = float(width)
    length = float(length)
    depth = float(depth)
    stepdown = float(stepdown)
    tool_diam = float(tool_diam)
    feedrate = float(feedrate)
    zstart = 0.0

    ymax = y+width/2-tool_diam/2
    ymin = y-width/2+tool_diam/2
    xmax = x+length/2+tool_diam/2
    xmin = x-length/2-tool_diam/2
    xpos = xmin
    tool_overlap = .2#percentage tool overcuts old path
    milling_stepover = tool_diam*(1.0-tool_overlap)

    #move tool to safe spot, then over cutting point. finally plunge
    gcode = safe_spot(1,tool_diam)
    gcode += "g1 x" + str(xpos) + " y" + str(ymin) + " f1000"
    gcode += "g1 z" + str(stepdown) + " f200"

    for zpos in range(zstart,-depth,stepdown):
        for ypos in range(ymin,ymax,milling_stepover):
            #move cutter down
            gcode += g1(xpos,ypos,zpos,feedrate)
            xpos = switch_direction(xpos,xmin,xmax)
            #move cutter on x axis
            gcode += g1(xpos,ypos,zpos,feedrate)
    #move cutter to safe spot when done
    gcode += safe_spot(1,tool_diam)
    return gcode

#this function assumes the top center of the ramp is at 0,0    It cuts a slope using an endmill
def cut_slope(ramp_top_x,run,rise,ramp_width,stepdown,tool_diam,feedrate):
    ramp_top_x = float(ramp_top_x)
    run = float(run)
    rise = float(rise)
    ramp_width = float(ramp_width)
    stepdown = float(stepdown)
    tool_diam = float(tool_diam)
    feedrate = float(feedrate)
    ramp_top_z = 0.0
    ramp_bottom_z = ramp_top_z + rise
    m = rise/run
    tool_overlap = .2#percentage tool overcuts old path
    milling_stepover = tool_diam*(1.0-tool_overlap)

    #boundrys xmin = top of ramp, x max = bottom + room for tool to finish
    xmin = (ramp_top_z/m)+tool_diam/2#boundry for top of ramp.
    xmax = (ramp_bottom_z/m)+tool_diam#bottom of ramp. need full tool diameter to finish.
    ymin = -ramp_width/2
    ymax = ramp_width/2
    ypos = ymin

    gcode = safe_spot(1,tool_diam)
    gcode += "g1 x" + str(xmin) + " y" + str(ymin) + " f1000\n"

    for zpos in range(ramp_top_z,ramp_bottom_z,stepdown):
        xcontact = (zpos/m)+tool_diam/2#contact point at slope at z height
        #lower head
        gcode += "g1 z" + str(zpos) + " f300\n"
        for xpos in range(xcontact,xmax,milling_stepover):
            gcode += g1(xpos,ypos,zpos,feedrate)
            ypos = switch_direction(ypos,ymin,ymax)
            gcode += g1(xpos,ypos,zpos,feedrate)

    gcode += "g1 z60 f1000\n"
    gcode += safe_spot(1,tool_diam)

    return gcode


#tests below: uncomment for testing>>>>

#xcorner = input("enter radius center x coordinate: ")
#ycorner = input("enter radius center y coordinate: ")
#zdepth = input("enter depth of cut: ")
#zstart = input("enter start of radius: ")
#zstop = input("enter stop point of radius: ")
#stepdown = input("milling stepdown distance per cut: ")
#toolDiam = input("enter tool diameter in mm: ")
#feedrate = input("enter feed rate: ")
#toolOverlap = input("enter tool overlap: ")
#radius = input("enter radius of the round to cut: ")

#print(face(xcorner,ycorner,zdepth,feedrate,stepdown,toolDiam,toolOverlap))
#print(cut_radius(radius,zstart,zstop,stepdown,xcorner,toolDiam,False))
#cut_radius(radius, zstart,zstop,stepdown,xlength,tooldiam,mirrory?)

#print(cut_pocket(0,0,40,40,6,.2,6.35,300))

print(cut_slope(0.0,20,-10,30,.1,6.35,300))
