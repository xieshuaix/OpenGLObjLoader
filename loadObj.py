import pygame
from OpenGL.GL import *
import os.path

# Default material name and data (properties) for cases where no .mtl file exists or .obj file references materials not
# listed in .obj file.
defaultMaterialName = "lightBlue"
defaultMaterialData = "newmtl %s\nKd 0.5 0.75 1.0\nillumn 1" % defaultMaterialName


def MTL(filename):
    # Load .mtl file
    contents = {}
    mtl = None
    i = 1
    # Try opening .mtl, if it does not exist, create one listing the default material and then try once again
    while i <= 2:
        # If .mtl exists, load it.
        if os.path.isfile(filename):
            for line in open(filename, "r"):
                if line.startswith('#'): continue
                values = line.split()
                if not values: continue
                if values[0] == 'newmtl':
                    mtl = contents[values[1]] = {}  # Initialize mtl for storing contents for different materials
                elif mtl is None:
                    raise ValueError, "mtl file doesn't start with newmtl stmt"
                elif values[0] == 'map_Kd':
                    # load the texture referred to by this declaration
                    mtl[values[0]] = values[1]
                    surf = pygame.image.load(mtl['map_Kd'])  # .tga file is loaded here
                    image = pygame.image.tostring(surf, 'RGBA', 1)
                    ix, iy = surf.get_rect().size
                    texid = mtl['texture_Kd'] = glGenTextures(1)
                    glBindTexture(GL_TEXTURE_2D, texid)
                    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,
                                    GL_LINEAR)
                    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER,
                                    GL_LINEAR)
                    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ix, iy, 0, GL_RGBA,
                                 GL_UNSIGNED_BYTE, image)
                else:
                    try:
                        # This stored every other numbers in the .mtl file
                        # This fails sometimes for unknown reasons, pass in such case
                        mtl[values[0]] = map(float, values[1:])
                    except:
                        pass
            return contents
            break
        # If .mtl does not exist, create one, listing default material: lightBlue and its properties.
        else:
            f = open(filename,"w+")
            f.write(defaultMaterialData)
            f.close()
            if i == 2:
                raise Exception("No mtl file, failed to create one.")
        i += 1


class OBJ:
    # Load .obj file
    def __init__(self, filename, swapyz=False):
        """Loads a Wavefront OBJ file. """
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.faces = []

        material = None
        for line in open(filename, "r"):
            if line.startswith('#'): continue
            values = line.split()
            if not values: continue
            if values[0] == 'v':
                v = map(float, values[1:4])
                if swapyz:
                    v = v[0], v[2], v[1]
                self.vertices.append(v)
            elif values[0] == 'vn':
                v = map(float, values[1:4])
                if swapyz:
                    v = v[0], v[2], v[1]
                self.normals.append(v)
            elif values[0] == 'vt':
                self.texcoords.append(map(float, values[1:3]))
            elif values[0] in ('usemtl', 'usemat'):
                material = values[1]
            elif values[0] == 'mtllib':
                # .mtl file loaded here, self.mtl now contains properties of all materials that will be used.
                self.mtl = MTL(values[1])
            elif values[0] == 'f':
                face = []
                texcoords = []
                norms = []
                for v in values[1:]:
                    w = v.split('/')
                    face.append(int(w[0]))
                    if len(w) >= 2 and len(w[1]) > 0:
                        texcoords.append(int(w[1]))
                    else:
                        texcoords.append(0)
                    if len(w) >= 3 and len(w[2]) > 0:
                        norms.append(int(w[2]))
                    else:
                        norms.append(0)
                # This stores all properties of a face into faces.
                self.faces.append((face, norms, texcoords, material))

        self.gl_list = glGenLists(1)
        glNewList(self.gl_list, GL_COMPILE)
        glEnable(GL_TEXTURE_2D)
        glFrontFace(GL_CCW)
        for face in self.faces:
            vertices, normals, texture_coords, material = face

            # if the material specified for this face in .obj file is listed in .mtl file (self.mtl),
            # then load its properties.
            # Note you cannot use hasattr(self.mtl, material), you have to use material in self.mtl, because
            # self.mtl is a dictionary and material is its key instead of an attribute.
            if material in self.mtl:
                mtl = self.mtl[material]  # This retrieve all properties of the material for this face.
            # If the material specified for this face in .obj file is not listed in .mtl file (self.mtl),
            # then use default material: lightBlue.
            else:
                mtl = self.mtl[defaultMaterialName]

            if 'texture_Kd' in mtl:
                # use diffuse texmap
                glBindTexture(GL_TEXTURE_2D, mtl['texture_Kd'])
            else:
                # just use diffuse colour
                glColor(*mtl['Kd'])

            glBegin(GL_POLYGON)
            for i in range(len(vertices)):
                if normals[i] > 0:
                    glNormal3fv(self.normals[normals[i] - 1])
                if texture_coords[i] > 0:
                    glTexCoord2fv(self.texcoords[texture_coords[i] - 1])
                glVertex3fv(self.vertices[vertices[i] - 1])
            glEnd()
        glDisable(GL_TEXTURE_2D)
        glEndList()