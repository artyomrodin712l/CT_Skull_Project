import numpy as np
import datetime
import math
from scipy.spatial import Delaunay 
import struct

def write(filename, x, y, z, mode='binary'):

    if type(filename) is not str:
        raise Exception('Invalid filename')

    if mode != 'ascii':
        mode = 'binary'

    if z.ndim != 2:
        raise Exception('Variable z must be a 2-dimensional array')

    ### x, y can not be used as dx, dy in Python
    ### if arguments type of x(or y) is 'int',
    ### type error will raise in next 'if' block
    # if type(x) == int and type(y) == int:
    #    x = np.arange(0, z.shape[1], x)
    #    x = np.arange(0, z.shape[0], y)

    if len(x.shape) == 1 and x.shape[0] == z.shape[1] \
            and len(y.shape) == 1 and y.shape[0] == z.shape[0]:
        x, y = np.meshgrid(x, y)

    if len(x.shape) != len(z.shape) \
            or len(y.shape) != len(z.shape) \
            or x.shape[1] != z.shape[1] \
            or y.shape[0] != z.shape[0]:
        raise Exception('Unable to resolve x and y variables')

    nfacets = 0
    title_str = 'Created by surf2stl.py %s' % datetime.datetime.now().strftime('%d-%b-%Y %H:%M:%S')

    f = open(filename, 'wb' if mode != 'ascii' else 'w')

    if mode == 'ascii':
        f.write('solid %s\n' % title_str)
    else:
        title_str_ljust = title_str.ljust(80)
        # f.write(title_str_ljust.encode('utf-8')) # same as 'ascii' for alphabet characters
        f.write(title_str_ljust.encode('ascii'))
        f.write(struct.pack('i', 0))

    for i in range(z.shape[0]-1):
        for j in range(z.shape[1]-1):
            p1 = np.array([x[i,j], y[i,j], z[i,j]])
            p2 = np.array([x[i,j+1], y[i,j+1], z[i,j+1]])
            p3 = np.array([x[i+1,j+1], y[i+1,j+1], z[i+1,j+1]])
            val = local_write_facet(f, p1, p2, p3, mode)
            nfacets += val

            p1 = np.array([x[i+1,j+1], y[i+1,j+1], z[i+1,j+1]])
            p2 = np.array([x[i+1,j], y[i+1,j], z[i+1,j]])
            p3 = np.array([x[i,j], y[i,j], z[i,j]])
            val = local_write_facet(f, p1, p2, p3, mode)
            nfacets += val

    if mode == 'ascii':
        f.write('endsolid %s\n' % title_str)
    else:
        f.seek(80, 0)
        f.write(struct.pack('i', nfacets))

    f.close()

    print('Wrote %d facets' % nfacets)
    return

def tri_write(filename, x, y, z, tri, mode='binary'):

    if type(filename) is not str:
        raise Exception('Invalid filename')

    if mode != 'ascii':
        mode = 'binary'

    if len(x.shape) != 1 \
            or len(y.shape) != 1 \
            or len(z.shape) != 1:
        raise Exception('Each variable x,y,z must be a 1-dimensional array')

    if x.shape[0] != z.shape[0] \
            or y.shape[0] != z.shape[0]:
        raise Exception('Number of x,y,z elements must be equal')

    nfacets = 0
    title_str = 'Created by surf2stl.py %s' % datetime.datetime.now().strftime('%d-%b-%Y %H:%M:%S')

    f = open(filename, 'wb' if mode != 'ascii' else 'w')

    if mode == 'ascii':
        f.write('solid %s\n' % title_str)
    else:
        title_str_ljust = title_str.ljust(80)
        # f.write(title_str_ljust.encode('utf-8')) # same as 'ascii' for alphabet characters
        f.write(title_str_ljust.encode('ascii'))
        f.write(struct.pack('i', 0))

    indices = tri.simplices
    verts = tri.points[indices]
    for i in range(0, indices.shape[0], 1):
        p = indices[i]
        p1 = np.array([x[p[0]], y[p[0]], z[p[0]]])
        p2 = np.array([x[p[1]], y[p[1]], z[p[1]]])
        p3 = np.array([x[p[2]], y[p[2]], z[p[2]]])
        val = local_write_facet(f, p1, p2, p3, mode)
        nfacets += val

    if mode == 'ascii':
        f.write('endsolid %s\n' % title_str)
    else:
        f.seek(80, 0)
        f.write(struct.pack('i', nfacets))

    f.close()

    print('Wrote %d facets' % nfacets)
    return

# Local subfunctions

def local_write_facet(f, p1, p2, p3, mode):
    if np.isnan(p1).any() or np.isnan(p2).any() or np.isnan(p3).any():
            return 0

    n = local_find_normal(p1, p2, p3)
    if mode == 'ascii':
        f.write('facet normal %.7f %.7f %.7f\n' % (n[0], n[1], n[2]))
        f.write('outer loop\n')
        f.write('vertex %.7f %.7f %.7f\n' % (p1[0], p1[1], p1[2]))
        f.write('vertex %.7f %.7f %.7f\n' % (p2[0], p2[1], p2[2]))
        f.write('vertex %.7f %.7f %.7f\n' % (p3[0], p3[1], p3[2]))
        f.write('endloop\n')
        f.write('endfacet\n')
    else:
        f.write(struct.pack('%sf' % len(n), *n))
        f.write(struct.pack('%sf' % len(p1), *p1))
        f.write(struct.pack('%sf' % len(p2), *p2))
        f.write(struct.pack('%sf' % len(p3), *p3))
        f.write(struct.pack('h', 0))
    return 1

def local_find_normal(p1, p2, p3):
    v1 = p2 - p1
    v2 = p3 - p1
    v3 = np.cross(v1, v2)
    n = v3 / math.sqrt(np.sum(v3*v3))
    return n