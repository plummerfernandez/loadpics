#!/usr/bin/env python
#coding:utf-8
# Purpose: Import PNG files and Export 3D objects, build of faces with 3 vertices, as ASCII or Binary STL file.
# License: MIT License
import png
import struct
import math
import numpy as np
import pprint


filenam = "pp"
fil = filenam + ".png"

ASCII_FACET = """facet normal 0 0 0
outer loop
vertex {face[0][0]:.4f} {face[0][1]:.4f} {face[0][2]:.4f}
vertex {face[1][0]:.4f} {face[1][1]:.4f} {face[1][2]:.4f}
vertex {face[2][0]:.4f} {face[2][1]:.4f} {face[2][2]:.4f}
endloop
endfacet
"""

BINARY_HEADER ="80sI"
BINARY_FACET = "12fH"

class ASCII_STL_Writer(object):
    """ Export 3D objects build of 3 or 4 vertices as ASCII STL file.
    """
    def __init__(self, stream):
        self.fp = stream
        self._write_header()

    def _write_header(self):
        self.fp.write("solid python\n")

    def close(self):
        self.fp.write("endsolid python\n")

    def _write(self, face):
        self.fp.write(ASCII_FACET.format(face=face))

    def _split(self, face):
        p1, p2, p3, p4 = face
        return (p1, p2, p3), (p3, p4, p1)

    def add_face(self, face):
        """ Add one face with 3 or 4 vertices. """
        if len(face) == 4:
            face1, face2 = self._split(face)
            self._write(face1)
            self._write(face2)
        elif len(face) == 3:
            self._write(face)
        else:
            raise ValueError('only 3 or 4 vertices for each face')

    def add_faces(self, faces):
        """ Add many faces. """
        for face in faces:
            self.add_face(face)

class Binary_STL_Writer(ASCII_STL_Writer):
    """ Export 3D objects build of 3 or 4 vertices as binary STL file.
    """
    def __init__(self, stream):
        self.counter = 0
        super(Binary_STL_Writer, self).__init__(stream)

    def close(self):
        self._write_header()

    def _write_header(self):
        self.fp.seek(0)
        self.fp.write(struct.pack(BINARY_HEADER, b'Python Binary STL Writer', self.counter))

    def _write(self, face):
        self.counter += 1
        data = [
            0., 0., 0.,
            face[0][0], face[0][1], face[0][2],
            face[1][0], face[1][1], face[1][2],
            face[2][0], face[2][1], face[2][2],
            0
        ]
        self.fp.write(struct.pack(BINARY_FACET, *data))


def example():
    def get_cube():
        # cube corner points
        s = 3.
        p1 = (0, 0, 0)
        p2 = (0, 0, s)
        p3 = (0, s, 0)
        p4 = (0, s, s)
        p5 = (s, 0, 0)
        p6 = (s, 0, s)
        p7 = (s, s, 0)
        p8 = (s, s, s)

        # define the 6 cube faces
        # faces just lists of 3 or 4 vertices
        return [
            [p1, p5, p7, p3],
            [p1, p5, p6, p2],
            [p5, p7, p8, p6],
            [p7, p8, p4, p3],
            [p1, p3, p4, p2],
            [p2, p6, p8, p4],
        ]

    with open('cube.stl', 'wb') as fp:
        writer = Binary_STL_Writer(fp)
        writer.add_faces(get_cube())
        writer.close()

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

def getRGBfromI(RGBint):
    blue =  RGBint & 255
    green = (RGBint >> 8) & 255
    red =   (RGBint >> 16) & 255
    return red, green, blue

def getIfromRGB(rgb):
    red, green, blue = rgb
    RGBint = (red<<16) + (green<<8) + blue
    return RGBint

def readPNG(filz):
    #r=png.Reader(file=urllib.urlopen('http://www.schaik.com/pngsuite/basn0g02.png'))
    r=png.Reader(filename=filz)
    tups = r.read()
    print tups

    height = tups[0]
    l=list(tups[2])

    allpx = []
    for x in range(0, height+10):
        try:
            allpx.extend(l[x])
        except:
            print "list out of range"

    print "done adding all in one row"

    return allpx


def processColorPixels(colors):

    x = 0
    allverts = [[] for i in range(len(colors))]
    for px in colors:
        #Get integer
        i = getIfromRGB(px)
        #if a black pixel used to end image remainder
        if(i ==0):
            #this is the end, get out of here
            print "getting out"
            return allverts
        #if any colour except the spacers or enders
        if(i!= 1):
            allverts[x].append(i)
        # if off-black pixel spacer
        if(i==1):
            x += 1
            #print "making x = " + str(x)
    # Get out normally without black pixel ending
    print "out without touching black pixels"
    return allverts

def tripletuplefy(ninevertarray):
    totalarray = []
    for everynine in ninevertarray:
        
        if everynine != []:
            vert1 = everynine[0],everynine[1],everynine[2]
            vert2 = everynine[3],everynine[4],everynine[5]
            vert3 = everynine[6],everynine[7],everynine[8]
            #print vert1
            vector = []
            vector.append(vert1)
            vector.append(vert2)
            vector.append(vert3)
            #print vector
            totalarray.append(vector)
    return totalarray



def reformatToColors(pxls):
    a = np.array(pxls)
    b = np.reshape(a, (len(pxls)/3, 3))  
    return b

def png2stl(infilename, outfilename):
    px = readPNG(fil) 
    colrlist = reformatToColors(px)
    vertarray = processColorPixels(colrlist)
    #pprint.pprint(vertarray)
    totalarray = tripletuplefy(vertarray)
    with open(outfilename, 'wb') as fp:
        writer = Binary_STL_Writer(fp)
        writer.add_faces(totalarray)
        writer.close()



if __name__ == '__main__':
    ##sequence
    px = readPNG(fil) 
    colrlist = reformatToColors(px)
    vertarray = processColorPixels(colrlist)
    #pprint.pprint(vertarray)
    totalarray = tripletuplefy(vertarray)
    #pprint.pprint(totalarray)

    with open(filenam+'-remade.stl', 'wb') as fp:
        writer = Binary_STL_Writer(fp)
        writer.add_faces(totalarray)
        writer.close()


    # ####  TEST
    # i1 = 16777215 
    # colr1 = getRGBfromI(i1)
    # print colr1
    # i2 =getIfromRGB(colr1)
    # print i1, i2
