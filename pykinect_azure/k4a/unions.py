from ctypes import *

class POINT(Structure):
    _fields_ = [("x", c_int),
                 ("y", c_int)]

class POINT_1(Structure):
    _fields_ = [("x", c_int),
                 ("y", c_int),
                 ("z",c_int)]

class POINT_UNION(Union):
    _fields_ = [("a", POINT),
                 ("b", POINT_1)]

class TEST(Structure):
    _fields_ = [("magic", c_int),
                 ("my_union", POINT_UNION)]

testing = TEST()
testing.magic = 10;
testing.my_union.b.x=100
testing.my_union.b.y=200