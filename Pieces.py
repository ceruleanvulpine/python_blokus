# PIECES.PY
# Functions for use with pieces, abstract piece class with functions for
# transformations, and specific pieces extending it 

# Coordinates are 2x1 matrices
# Each corner is represented as a 2x2 matrix, one coordinate on the block and one
# outside of it 
# Sets of corners are stored as 2x2n matrices
# Piece shapes are 2xn matrices where each column is a coordinate
# Transformation matrices are 2x2 matrices where Ax = T(x)

import numpy as np
import pdb
import BlokusFunctions as bfn

class Piece:
    """Generic piece type."""

    # r90 (bool): Does piece lack fourfold rotational symmetry?
    # r180 (bool): Does piece lack twofold rotational symmetry?
    # chiral (bool): Is piece chiral?
    # shape: 2xn array of coordinates where n = size of piece
    # corners: 2x2c array of coordinates where c = number of corners

    # orientation: 3 bits represent direction and whether flipped (if chiral)
    # first bit is axis aligned with, second bit is direction on that axis, third is whether flipped
    # 0b000 (0) is north, 0b001 (1) is north (flipped)
    # 0b100 (4) is west, 0b101 (5) is west (flipped)
    # 0b010 (2) is south, 0b011 (3) is south (flipped)
    # 0b110 (6) is east, 0b111 (7) is east (flipped)

    def flipH(self):
        """Flip this piece over the y-axis."""
        hflip = np.array([[-1, 0],[0,1]])

        # Flip corners
        self.corners = np.dot(hflip, self.corners)

        # Flip shape
        self.shape = np.dot(hflip, self.shape)

        # Update orientation - always flip 3rd bit,
        # flip 2nd bit if piece is "horizontally" aligned (points east or west)
        self.orientation ^= 0b001
        if self.orientation & 0b100:
            self.orientation ^= 0b010

        self.reduceOrientation()

    def flipV(self):
        """Flip this piece over the x-axis."""
        vflip = np.array([[1,0],[0,-1]])

        # Flip corners
        self.corners = np.dot(vflip, self.corners)

        # Flip shape
        self.shape = np.dot(vflip, self.shape)

        # Update orientation - always flip 3rd bit,
        # flip 2nd bit if piece is "vertically" aligned (points north or south)
        self.orientation ^= 0b001
        if not self.orientation & 0b100:
            self.orientation ^= 0b010

        self.reduceOrientation()

    # NOTE: rotation matrices are for cw turns bc of y axis pointing down
    # in matrix indexing
    # returns false if turns is not between one and three
    def rotate(self, turns):
        """Rotate this piece 90*turns degrees counterclockwise."""
        if turns == 1 and self.r90:
            rmat = np.array([[0,1],[-1,0]])
            self.corners = np.dot(rmat, self.corners)
            self.shape = np.dot(rmat, self.shape)

            # update orientation - if "vertically" aligned,
            # flip only first, else flip first and second
            if not self.orientation & 0b100:
                self.orientation ^= 0b100
            else:
                self.orientation ^= 0b110

            self.reduceOrientation()  
            return True
        elif turns == 2 and self.r180:
            rmat = np.array([[-1,0],[0,-1]])
            self.corners = np.dot(rmat, self.corners)
            self.shape = np.dot(rmat, self.shape)

            # update orientation - flip second bit
            self.orientation ^= 0b010

            self.reduceOrientation()            
            return True
        elif turns == 3 and self.r90:
            rmat = np.array([[0,-1],[1,0]])
            self.corners = np.dot(rmat, self.corners)
            self.shape = np.dot(rmat, self.shape)

            # update orientation - if "horizontally" aligned,
            # flip only first, else flip first and second
            if self.orientation & 0b100:
                self.orientation ^= 0b100
            else:
                self.orientation ^= 0b110

            self.reduceOrientation()
            return True
        else:
            return False

    def translate(self, x,y):
        """Translate this piece by [x,y]."""

        self.shape[0] += x
        self.shape[1] += y
        self.corners[0] += x
        self.corners[1] += y

    def setOrientation(self, new_orientation):
        """Put this piece into the provided orientation."""
        if self.orientation & 0b001 != new_orientation & 0b001:
            self.flipH()
        while self.orientation != new_orientation:
            self.rotate(1)
        self.reduceOrientation()

    def matchingOrientation(self, compare):
        """Return the orientation, if any, of this piece that matches the shape in compare, or -1 otherwise."""

        compare = bfn.toBoolArray(compare)
        boolshape = bfn.toBoolArray(self.shape)
        if np.array_equal(boolshape, compare):
            self.reduceOrientation()
            return self.orientation

        if self.r90 and self.r180:
            for i in range(3):
                self.rotate(1)
                boolshape = bfn.toBoolArray(self.shape)
                if np.array_equal(boolshape, compare):
                    self.reduceOrientation()
                    return self.orientation
        elif self.r90 and not self.r180:
            self.rotate(1)
            boolshape = bfn.toBoolArray(self.shape)
            if np.array_equal(boolshape, compare):
                self.reduceOrientation()
                return self.orientation

        if self.chiral:
            self.flipV()

            boolshape = bfn.toBoolArray(self.shape)
            if np.array_equal(boolshape, compare):
                self.reduceOrientation()
                return self.orientation

            if self.r90 and self.r180:
                for i in range(3):
                    self.rotate(1)
                    boolshape = bfn.toBoolArray(self.shape)
                    if np.array_equal(boolshape, compare):
                        self.reduceOrientation()
                        return self.orientation
            elif self.r90 and not self.r180:
                self.rotate(1)
                boolshape = bfn.toBoolArray(self.shape)
                if np.array_equal(boolshape, compare):
                    self.reduceOrientation()
                    return self.orientation
                
        return -1

    def reduceOrientation(self):
        """Change own orientation to the smallest congruent orientation considering piece's symmetry."""
        if self.r90 and self.r180 and not self.chiral:
            if self.orientation == 1:
                self.orientation = 0
            if self.orientation == 3:
                self.orientation = 2
            if self.orientation == 5:
                self.orientation = 4
            if self.orientation == 7:
                self.orientation = 6
        if self.r90 and not self.r180 and self.chiral:
            if self.orientation == 2:
                self.orientation = 0
            if self.orientation == 3:
                self.orientation = 1
            if self.orientation == 6:
                self.orientation = 4
            if self.orientation == 7:
                self.orientation = 5
        if self.r90 and not self.r180 and not self.chiral:
            if (self.orientation == 1 or self.orientation == 2
                or self.orientation == 3):
                self.orientation = 0
            if (self.orientation == 5 or self.orientation == 6
                or self.orientation == 7):
                self.orientation = 4    
                
    def __repr__(self):
        return bfn.toBoolArray(self.shape).__repr__()


class F(Piece):
    def __init__(self):
        self.name = "F"
        self.shape = np.array([[ 0, -1, -1, -2, -1],
                                    [ 0,  0,  1,  1,  2]])
        self.corners = np.array([[ 0,  1, -1, -2, -1,  0, -1, -2,  0,  1, -2, -3, -2, -3],
                                 [ 0, -1,  0, -1,  2,  3,  2,  3,  0,  1,  1,  0,  1,  2]])
        self.r90 = True
        self.r180 = True
        self.chiral = True
        self.size = 5

        self.orientation = 0b000

class I(Piece):
    def __init__(self):
        self.name = "I"
        self.shape = np.array([[0,0,0,0,0],
                               [0,1,2,3,4]])
        self.corners = np.array([[0,-1,0,1,0,-1,0,1],
                                 [0,-1,0,-1,4,5,4,5]])
        self.r90 = True
        self.r180 = False
        self.chiral = False
        self.size = 5

        self.orientation = 0b000

class L(Piece):
    def __init__(self):
        self.name = "L"
        self.shape = np.array([[ 0,  0,  0,  0,  1],
                               [ 0, -1, -2, -3,  0]])
        self.corners = np.array([[ 0, -1,  1,  2,  1,  2,  0, -1,  0,  1],
                                 [ 0,  1,  0,  1,  0, -1, -3, -4, -3, -4]])
        self.r90 = True
        self.r180 = True
        self.chiral = True
        self.size = 5

        self.orientation = 0b000

class N(Piece):
    def __init__(self):
        self.name = "N"
        self.shape = np.array([[ 0,  0,  0,  1,  1],
                               [ 0, -1, -2, -2, -3]])
        self.corners = np.array([[ 0, -1,  0,  1,  0, -1,  1,  2,  1,  0,  1,  2],
                                 [ 0,  1,  0,  1, -2, -3, -2, -1, -3, -4, -3, -4]])
        self.r90 = True
        self.r180 = True
        self.chiral = True
        self.size = 5

        self.orientation = 0b000
    
class P(Piece):
    def __init__(self):
        self.name = "P"
        self.shape = np.array([[0,1,0,1,0],
                               [0,0,1,1,2]])
        self.corners = np.array([[0,-1,1,2,1,2,0,-1,0,1],
                                 [0,-1,0,-1,1,2,2,3,2,3]])
        self.r90 = True
        self.r180 = True
        self.chiral = True
        self.size = 5

        self.orientation = 0b000

class T(Piece):
    def __init__(self):
        self.name = "T"
        self.shape = np.array([[0,1,2,1,1],
                               [0,0,0,1,2]])
        self.corners = np.array([[0,-1,0,-1,2,3,2,3,1,0,1,2],
                                 [0,-1,0,1,0,-1,0,1,2,3,2,3]])
        self.r90 = True
        self.r180 = True
        self.chiral = False
        self.size = 5

        self.orientation = 0b000

class U(Piece):
    def __init__(self):
        self.name = "U"
        self.shape = np.array([[0,0,1,2,2],
                               [0,1,1,1,0]])
        self.corners = np.array([[0,-1,0,1,0,-1,2,3,2,1,2,3],
                                 [0,-1,0,-1,1,2,1,2,0,-1,0,-1]])
        self.r90 = True
        self.r180 = True
        self.chiral = False
        self.size = 5

        self.orientation = 0b000

class V(Piece):
    def __init__(self):
        self.name = "V"
        self.shape = np.array([[ 0,  0,  1,  0,  2],
                               [ 0, -1,  0, -2,  0]])
        self.corners = np.array([[ 0, -1,  0, -1,  0,  1,  2,  3,  2,  3],
                                 [ 0,  1, -2, -3, -2, -3,  0,  1,  0, -1]])

        self.r90 = True
        self.r180 = True
        self.chiral = False
        self.size = 5

        self.orientation = 0b000

class W(Piece):
    def __init__(self):
        self.name = "W"
        self.shape = np.array([[ 0, -1, -1, -2, -2],
                               [ 0,  0, -1, -1, -2]])
        self.corners = np.array([[ 0,  1,  0,  1, -1, -2, -1,  0, -2, -3, -2, -1, -2, -3],
                                 [ 0,  1,  0, -1,  0,  1, -1, -2, -1,  0, -2, -3, -2, -3]])

        self.r90 = True
        self.r180 = True
        self.chiral = True
        self.size = 5

        self.orientation = 0b000

class X(Piece):
    def __init__(self):
        self.name = "X"
        self.shape = np.array([[1,0,1,2,1],
                               [0,1,1,1,2]])
        self.corners = np.array([[1,0,1,2,0,-1,0,-1,1,0,1,2,2,3,2,3],
                                 [0,-1,0,-1,1,0,1,2,2,3,2,3,1,0,1,2]])
        self.r90 = False
        self.r180 = False
        self.chiral = False
        self.size = 5

        self.orientation = 0b000

class Y(Piece):
    def __init__(self):
        self.name = "Y"
        self.shape = np.array([[ 0,  0,  0,  0, -1],
                               [ 0,  1,  2,  3,  1]])
        self.corners = np.array([[ 0,  1,  0, -1, -1, -2, -1, -2,  0,  1,  0, -1],
                                 [ 0, -1,  0, -1,  1,  0,  1,  2,  3,  4,  3,  4]])
        self.r90 = True
        self.r180 = True
        self.chiral = True
        self.size = 5

        self.orientation = 0b000

class Z(Piece):
    def __init__(self):
        self.name = "Z"
        self.shape = np.array([[0,1,1,1,2],
                               [0,0,1,2,2]])
        self.corners = np.array([[0,-1,0,-1,1,2,1,0,2,3,2,3],
                                 [0,-1,0,1,0,-1,2,3,2,3,2,1]])
        self.r90 = True
        self.r180 = False
        self.chiral = True
        self.size = 5

        self.orientation = 0b000

class I4(Piece):
    def __init__(self):
        self.name = "I4"
        self.shape = np.array([[0,0,0,0],
                               [0,1,2,3]])
        self.corners = np.array([[0,-1,0,1,0,-1,0,1],
                                 [0,-1,0,-1,3,4,3,4]])
        self.r90 = True
        self.r180 = False
        self.chiral = False
        self.size = 4

        self.orientation = 0b000

class L4(Piece):
    def __init__(self):
        self.name = "L4"
        self.shape = np.array([[ 0,  1,  0,  0],
                               [ 0,  0, -1, -2]])
        self.corners = np.array([[ 0, -1,  1,  2,  1,  2,  0, -1,  0,  1],
                                 [ 0,  1,  0,  1,  0, -1, -2, -3, -2, -3]])
        self.r90 = True
        self.r180 = True
        self.chiral = True
        self.size = 4

        self.orientation = 0b000

class N4(Piece):
    def __init__(self):
        self.name = "N4"
        self.shape = np.array([[ 0,  0, -1, -1],
                               [ 0,  1,  1,  2]])
        self.corners = np.array([[ 0,  1,  0, -1,  0,  1, -1, -2, -1,  0, -1, -2],
                                 [ 0, -1,  0, -1,  1,  2,  1,  0,  2,  3,  2,  3]])

        self.r90 = True
        self.r180 = False
        self.chiral = True
        self.size = 4

        self.orientation = 0b000

class O(Piece):
    def __init__(self):
        self.name = "O"
        self.shape = np.array([[0,1,0,1],
                               [0,0,1,1]])
        self.corners = np.array([[0,-1,1,2,0,-1,1,2],
                                 [0,-1,0,-1,1,2,1,2]])
        self.r90 = False
        self.r180 = False
        self.chiral = False
        self.size = 4

        self.orientation = 0b000

class T4(Piece):
    def __init__(self):
        self.name = "T4"
        self.shape = np.array([[0,1,1,2],
                               [0,0,1,0]])
        self.corners = np.array([[0,-1,2,3,1,0,1,2],
                                 [0,-1,0,-1,1,2,1,2]])
        self.r90 = True
        self.r180 = True
        self.chiral = False
        self.size = 4

        self.orientation = 0b000

class I3(Piece):
    def __init__(self):
        self.name = "I3"
        self.shape = np.array([[0,0,0],
                               [0,1,2]])
        self.corners = np.array([[0,-1,0,1,0,-1,0,1],
                                 [0,-1,0,-1,2,3,2,3]])
        self.r90 = True
        self.r180 = False
        self.chiral = False
        self.size = 3

        self.orientation = 0b000

class V3(Piece):
    def __init__(self):
        self.name = "V3"
        self.shape = np.array([[ 0, -1, -1],
                               [ 0,  0, -1]])
        self.corners = np.array([[ 0,  1,  0,  1, -1, -2, -1,  0, -1, -2],
                                 [ 0,  1,  0, -1,  0,  1, -1, -2, -1, -2]])
        self.r90 = True
        self.r180 = True
        self.chiral = False
        self.size = 3

        self.orientation = 0b000

class Two(Piece):
    def __init__(self):
        self.name = "Two"
        self.shape = np.array([[0,0],
                               [0,1]])
        self.corners = np.array([[0,-1,0,1,0,-1,0,1],
                                 [0,-1,0,-1,1,2,1,2]])
        self.r90 = True
        self.r180 = False
        self.chiral = False
        self.size = 2

        self.orientation = 0b000

class One(Piece):
    def __init__(self):
        self.name = "One"
        self.shape = np.array([[0],
                               [0]])
        self.corners = np.array([[0,-1,0,1,0,1,0,-1],
                                 [0,-1,0,-1,0,1,0,1]])
        self.r90 = False
        self.r180 = False
        self.chiral = False
        self.size = 1

        self.orientation = 0b000


        
