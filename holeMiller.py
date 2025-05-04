

def millCircle(x, y, i, j, z, toolDiam, mtlToLeave, stepover, feedRate):
    gcodeOut = ""
    #g code variables: X=x coord endpt, Y=y coord endpt, I=y coord start offset from center, J=x coord start offset from center
    #print(f"G01 X{x} Y{y} Z{z} F{feedRate}")
    gcodeOut += f"G01 X{round(x, 3)} Y{round(y,3)} Z{round(z, 3)} F{round(feedRate, 3)}\n"
    #print(f"G02 X{x} Y{y} I{i} Z{z} J{j}")
    gcodeOut += f"G02 X{round(x, 3)} Y{round(y,3)} I{round(i, 3)} Z{round(z, 3)} J{round(j, 3)}\n"

    #loop to mill inwards until all cleared
    while(y > 0):
        y = y - (toolDiam + mtlToLeave - stepover)
        j = y * -1
    
        #print(f"G01 X{x} Y{y} Z{z} F{feedRate}")
        gcodeOut += f"G01 X{round(x, 3)} Y{round(y,3)} Z{round(z, 3)} F{round(feedRate, 3)}\n"
        #print(f"G02 X{x} Y{y} I{i} Z{z} J{j}")
        gcodeOut += f"G02 X{round(x,3)} Y{round(y, 3)} I{round(i, 3)} Z{round(z, 3)} J{round(j, 3)}\n"
    

    return gcodeOut


def save_to_file(filename, gcodeOut):
    with open(filename, 'w') as f:
        f.write(gcodeOut)
        f.close()



def main():
    print("***************Tools************** \n" \
    "1/16in = 1.5875mm\n"
    "1/8in = 3.175mm\n"
    "1/4in = 6.35mm\n" \
    "3/8in = 9.525\n" \
    "1/2in = 12.7mm\n" \
    "***********************************\n"
    "")

    holeDiam = float(input("Enter hole diameter: "))
    holeDepth = float(input("Depth of hole: ")) * -1
    stepdown = float(input("stepdown mm: "))
    toolDiam = float(input("Tool diameter: "))
    mtlToLeave = float(input("Material to leave (tolerance): "))
    feedRate = float(input("Feedrate: ")) 
    #stepover for pases
    stepover = 0.25

    #gcode string 
    gcodeOut = ""
    

    
    
    #calculate path vars 
    z = 0.0

    while(z > (holeDepth)):
        x = 0.0
        y = round((holeDiam/2) - (toolDiam/2) - mtlToLeave, 4)
        j = round(y * -1, 3)
        i = round(x, 3)

        gcodeOut += millCircle(x, y, i, j, z, toolDiam, mtlToLeave, stepover, feedRate)
        
        #move down a step until bottom reached
        z = z - stepdown
        if(z <= (holeDepth)):
            z = holeDepth 
            gcodeOut += millCircle(x, y, i, j, z, toolDiam, mtlToLeave, stepover, feedRate)

    #return end mill to home 
    gcodeOut += f"G1 X{0} Y{0} Z{10} F{1000}\n"

    #save as gcode file 
    filename = input("Enter file name: ")
    save_to_file(filename, gcodeOut)

if __name__ == "__main__":
    main()
