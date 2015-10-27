# COVERTS STLs to PNGs by mapping XYZ coords onto RGB values

from stl import stl
import png
import math
import numpy as np


#filenam = "pill"
#fil = filenam + ".stl"


### The two data sets that we will convert to pixels
#print mesh.normals
#print mesh.normals[0][0]
#print mesh.vectors

#you can also read as one complete list with mesh.data

def getRGBfromI(RGBint):
	blue =  RGBint & 255
	green = (RGBint >> 8) & 255
	red =   (RGBint >> 16) & 255
	return red, green, blue


def remap(value, leftMin, leftMax, rightMin, rightMax): #like processing's map() function
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin
    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)
    # Convert the 0-1 range into a value in the right range.
    floatans = rightMin + (valueScaled * rightSpan) #as float
    intans = int(floatans) # as integer
    return intans #for our purposes we want an integer result (may deform mesh very slightly)


def getcartesianrange(vertarray): #give it the vertex array and calculate the min and max coords
	verts = []
	for vector in vertarray:
		for vert in vector:
			verts.append(vert)

	mymaxs = map(max, zip(*verts))
	mymax = max(mymaxs)
	mymins = map(min, zip(*verts))
	mymin = min(mymins)
	v1 = abs(mymax)
	v2 = abs(mymin)
	finalmax = max([v1,v2])
	return finalmax

def stl2png(infilename, outfilename):
    mesh = stl.StlMesh(infilename,calculate_normals=False) #do not calculate normals automatically

    ###------------ Converting Vertices -------------###
    origdist = getcartesianrange(mesh.vectors)
    print "origdist = " + str(origdist)

    vertcolrlist = [] # Put the colours in here

    #max integer for 24 bit  is 16777215
    whitepx = getRGBfromI(16777215)
    # max for 32bit is 2147483647, not using this anymore
    offwhitepx = getRGBfromI(16777214)
    blackpx = getRGBfromI(1)

    n = 0

    for vect in mesh.vectors: 
        ### get Normal ## NOT ACTUALLY NEEDED T
        # nxint = remap(mesh.normals[n][0],-1,1,2,16777213) 
        # nxcolrs = getRGBfromI(nxint)
        # nyint = remap(mesh.normals[n][1],-1,1,2,16777213)
        # nycolrs = getRGBfromI(nyint)
        # nzint = remap(mesh.normals[n][2],-1,1,2,16777213)
        # nzcolrs = getRGBfromI(nzint)
        # n+= 1
        # ncolrs = nxcolrs + nycolrs + nzcolrs + offwhitepx #single offwhite space
        #vertcolrlist.extend(ncolrs)

        #get xyz's for all three vertices
        for xyz in vect:
            # print xyz
            xint = remap(xyz[0],origdist*-1,origdist,2,16777213) #half way is 1073741823
            xcolrs = getRGBfromI(xint)
            yint = remap(xyz[1],origdist*-1,origdist,2,16777213)
            ycolrs = getRGBfromI(yint)
            zint = remap(xyz[2],origdist*-1,origdist,2,16777213)
            zcolrs = getRGBfromI(zint)
		
            colrs = xcolrs + ycolrs + zcolrs #+ whitepx # using a single whitespacer
            vertcolrlist.extend(colrs)

        #blackcolrs = blackpx + blackpx + blackpx + blackpx + blackpx  + blackpx # using a black spacer
        blackcolrs = blackpx  # using a single black spacer
        vertcolrlist.extend(blackcolrs)

#    print len(vertcolrlist)
    # vertcolrlist is now a totally flat list of RGB pixels
    # work out how many pixels wide/tall we want our image to be 
    num_pixels = len(vertcolrlist) / 3 # three for RGB
    width = int(math.sqrt(num_pixels))
    height = num_pixels / width 

#    print "num_pixels = " + str(num_pixels)
#    print "height = " + str(height)
#    print "width = " + str(width)

    ## maybe avoid multiples of 10 so that we don't get 'banding'
    #n % k == 0

    if width % 10 == 0:
#        print "this is a multiple of 10! "
        width -= 2

    # Somehow this is not working properly, catches error but doesnt solve it
    if(height * width) != num_pixels:
#        print 'WARNING'
        if(height * width) < num_pixels:
            while((height * width) < num_pixels):
                height += 1
            remainder = height*width - num_pixels
#            print "remainder = " + str(remainder)
            black0px = getRGBfromI(0)
            newpixels = (black0px * remainder) #remainder rendered as black pixels
            vertcolrlist.extend(newpixels)
#            print len(vertcolrlist)
#            print "new height = " + str(height)
#            print "new width = " + str(width)
#            print "remainder done"


    # now use numpy to reshape our 1D list into a 2D matrix
    a = np.array(vertcolrlist)
    b = np.reshape(a, (height, width * 3))  # three for RGB

    # pprint gives a nicely formatted output 
    import pprint
    #pprint.pprint(vertcolrlist)

    with open(outfilename, 'wb') as fp:
        w = png.Writer(width, height)
        w.write(fp, b)
