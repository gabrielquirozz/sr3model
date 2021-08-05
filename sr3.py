#Gabriel Quiroz
#19255
#02/08/2021
#Graficas
import struct
from Object import Obj

def char(c):
    #1 byte (char)
    return struct.pack('=c', c.encode('ascii'))

def word(w):
    #2 bytes (short)
    return struct.pack('=h', w)

def dword(d):
    #4 bytes (long)
    return struct.pack('=l', d)

def color(r, g, b):
    # Acepta valores de 0 a 1
    return bytes([ int(b * 255), int(g* 255), int(r* 255)])


color1 = color(0,0,0)
color2 = color(0,1,0)

#Funciones implementadas
class Renderer(object):
    #Glinit
    def __init__(self, width, height):
        self.punto_color = color2
        self.bitmap_color = color1
        self.glCreateWindow(width, height)
    #GlCreateWindow
    def glCreateWindow(self, width, height):
        self.width = width
        self.height = height
        self.glClear()
        self.glViewport(0,0, width, height)
    #GlViewPort
    def glViewport(self, x, y, width, height):
        self.vpX = int(x)
        self.vpY = int(y)
        self.vpWidth = int(width)
        self.vpHeight = int(height)

    #glClearColor
    def glClearColor(self, r, g, b):
        self.bitmap_color = color(r, g, b)
    #glClear
    def glClear(self):
        self.pixels = [[ self.bitmap_color for y in range(self.height)]
                       for x in range(self.width)]
    
    def glPoint(self, x, y, color = None):
        if x < self.vpX or x >= self.vpX + self.vpWidth or y < self.vpY or y >= self.vpY + self.vpHeight:
            return

        if (0 <= x < self.width) and (0 <= y < self.height):
            self.pixels[int(x)][int(y)] = color or self.punto_color

    def glColor(self, r, g, b):
        self.punto_color = color(r,g,b)
    
    def line(self, x0, y0, x1, y1):
      dy = abs(y1 - y0)
      dx = abs(x1 - x0)

      steep = dy > dx

      if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1

        dy = abs(y1 - y0)
        dx = abs(x1 - x0)

      offset = 0 * 2 * dx
      threshold = 0.5 * 2 * dx
      y = y0

      # y = mx + b
      points = []
      for x in range(x0, x1):
        if steep:
          points.append((y, x, self.punto_color))
        else:
          points.append((x, y, self.punto_color))

        offset += (dy/dx) * 2 * dx
        if offset >= threshold:
          y += 1 if y0 < y1 else -1
          threshold += 1 * 2 * dx

      for point in points:
          r.glPoint(*point)
          
    #glVertex
    def glVertex(self, x, y, color = None):
        x = int( (x + 1) * (self.vpWidth / 2) + self.vpX )
        y = int( (y + 1) * (self.vpHeight / 2) + self.vpY)


        if x < self.vpX or x >= self.vpX + self.vpWidth or y < self.vpY or y >= self.vpY + self.vpHeight:
            return

        if (0 <= x < self.width) and (0 <= y < self.height):
            self.pixels[int(x)][int(y)] = color or self.punto_color
            
    #glFinish
    def glFinish(self, filename):
        with open(filename, "wb") as file:
            # Header
            file.write(bytes('B'.encode('ascii')))
            file.write(bytes('M'.encode('ascii')))
            file.write(dword(14 + 40 + (self.width * self.height * 3)))
            file.write(dword(0))
            file.write(dword(14 + 40))

            # InfoHeader
            file.write(dword(40))
            file.write(dword(self.width))
            file.write(dword(self.height))
            file.write(word(1))
            file.write(word(24))
            file.write(dword(0))
            file.write(dword(self.width * self.height * 3))
            file.write(dword(0))
            file.write(dword(0))
            file.write(dword(0))
            file.write(dword(0))

            # Bitmap
            for y in range(self.height):
                for x in range(self.width):
                    file.write(self.pixels[x][y])
                    
    def glLine(self, v0x, v0y, v1x, v1y, color = None):

        x0 = int( (v0x + 1) * (self.vpWidth / 2) + self.vpX)
        x1 = int( (v1x + 1) * (self.vpWidth / 2) + self.vpX)
        y0 = int( (v0y + 1) * (self.vpHeight / 2) + self.vpY)
        y1 = int( (v1y + 1) * (self.vpHeight / 2) + self.vpY)

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)

        steep = dy > dx

        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1

        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)

        offset = 0
        limit = 0.5
        m = dy/dx
        y = y0

        for x in range(x0, x1 + 1):
            if steep:
                self.glPoint(y, x, color)
            else:
                self.glPoint(x, y, color)

            offset += m
            if offset >= limit:
                y += 1 if y0 < y1 else -1
                limit += 1
                
                
    def load(self, filename, translate, scale):
        model = Obj(filename)
        for face in model.faces:
            vcount = len(face)
            for j in range(vcount):
                f1 = face[j][0]
                f2 = face[(j + 1) % vcount][0]

                v1 = model.vertices[f1 - 1]
                v2 = model.vertices[f2 - 1]

                x1 = round((v1[0] + translate[0]) * scale[0])
                y1 = round((v1[1] + translate[1]) * scale[1])
                x2 = round((v2[0] + translate[0]) * scale[0])
                y2 = round((v2[1] + translate[1]) * scale[1])

                self.line(x1, y1, x2, y2)               


r = Renderer(1200, 1200)
r.load('./oot-link.obj', [0.1, 0.005], [5500,5500])
r.glFinish('gabriel.bmp')
print("Se ha creado el archivo 'gabriel.bmp'")
