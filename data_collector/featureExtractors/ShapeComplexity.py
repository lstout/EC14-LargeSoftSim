from __future__ import division
from FeatureExtractorAbstract import FeatureExtractorAbstract
from scipy.spatial import ConvexHull
from scipy.ndimage import label
import numpy as np

class ShapeComplexity(FeatureExtractorAbstract):
    
    def getCSVheader(self):
        return ['hullRatio','triangles', 'limbs']

    def extract(self, args):
        if args['voxelBefore'].isValid:
            vd = args['voxelBefore']
        elif args['voxelAfter'].isValid:
            vd = args['voxelAfter']
        else:
            return ['NA']
        dnaMatrix = vd.getDNAmatrix().astype(int)
        ratio, triangles = self.calc_complexity(dnaMatrix)
        limbs = self.calc_limbs(dnaMatrix)

        return [ratio, triangles, limbs]

    def volume_hull(self, hull):
        def tetrahedron_volume(a, b, c, d):
            return np.abs(np.einsum('ij,ij->i', a-d, np.cross(b-d, c-d))) / 6

        simplices = np.column_stack((np.repeat(hull.vertices[0], hull.nsimplex),
                                 hull.simplices))
        tets = hull.points[simplices]
        return np.sum(tetrahedron_volume(tets[:, 0], tets[:, 1],
                                     tets[:, 2], tets[:, 3]))
    
    def create_points(self, points, dnaMatrix):
        new_points = set()         
        for x,y,z in points:
            new_points.add((x+0.5, y+0.5, z+0.5))
            new_points.add((x+0.5, y+0.5, z-0.5))
            new_points.add((x+0.5, y-0.5, z+0.5))
            new_points.add((x+0.5, y-0.5, z-0.5))
            new_points.add((x-0.5, y+0.5, z+0.5))
            new_points.add((x-0.5, y+0.5, z-0.5))
            new_points.add((x-0.5, y-0.5, z+0.5))
            new_points.add((x-0.5, y-0.5, z-0.5))
        
        new_points = np.array(new_points)
        return new_points

    def calc_complexity(self, dnaMatrix):
        points = np.squeeze(np.dstack((dnaMatrix.nonzero())))
        new_points = self.create_points(points)
        hull = ConvexHull(new_points, qhull_options='FA')
        volume = self.volume_hull(hull)
        ratio = 1-(len(points)/volume)
        triangles = len(hull.simplices)
        if ratio < 0:
            return 0, triangles
        return ratio, triangles


    def find_centroid(self, dnaMatrix):
        x, y, z = dnaMatrix.nonzero()
        return np.round([np.average(x), np.average(y), np.average(z)])
    
    def remove_area_around_centroid(self, dnaMatrix, centroid, radius=0):
        m = np.copy(dnaMatrix)
        
        if not np.any(m):
            return m

        x_start = max(0,centroid[0]-radius)
        x_end =  min(10,centroid[0]+radius+1)
        y_start = max(0,centroid[1]-radius)
        y_end =  min(10,centroid[1]+radius+1)
        z_start = max(0,centroid[2]-radius)
        z_end =  min(10,centroid[2]+radius+1)

        m[x_start:x_end,y_start:y_end,z_start:z_end] = 0
        return m
    
    def find_islands(self, dnaMatrix):
        dnaMatrix[dnaMatrix>0] = 1
        l, n_islands = label(dnaMatrix)
        return n_islands, l

    
    def calc_limbs(self,dnaMatrix):
        centroid = map(int,self.find_centroid(dnaMatrix).tolist())
        islands = []
        for r in range(10):
            m = self.remove_area_around_centroid(dnaMatrix, centroid, radius=r)
            n_islands, clusters = self.find_islands(m)
            if not np.any(m):
                break
            islands.append(n_islands)
        return max(islands) 
    
    
