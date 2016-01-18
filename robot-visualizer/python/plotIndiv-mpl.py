from getVoxelData import VoxelData
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from mpl_toolkits.mplot3d import art3d


### WARNING, THIS SCRIPT USES CPU RENDERING AND IS TERRIBLY SLOW FOR 3D

class PlotIndividual:
    def __init__(self):
        pass

    def getColor(self, cell):
        if cell == 0: # empty
            return None
        if cell == 1: # fat
            return "cyan"
        if cell == 2: # bone
            return "blue"
        if cell == 3: # muscle negative
            return "green"
        if cell == 4: # muscle positive
            return "red"


    def plot(self, filePath):
        dnamatrix = VoxelData(filePath).getDNAmatrix()
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')

        for z in range(10):
            for y in range(10):
                for x in range(10):
                    cellContent = int(dnamatrix[z][y][x])
                    color = self.getColor(cellContent)
                    if color != None:
                        self.drawCube((x,y,z), color)

        self.ax.set_xlabel('X axis')
        self.ax.set_ylabel('Y axis')
        self.ax.set_zlabel('Z axis')
        plt.show()

    def drawCube(self, pos, color):
        r1 = Rectangle((pos[1],pos[2]), 1, 1, fc=color, ec=None)
        r2 = Rectangle((pos[1],pos[2]), 1, 1, fc=color, ec=None)
        r3 = Rectangle((pos[0],pos[2]), 1, 1, fc=color, ec=None)
        r4 = Rectangle((pos[0],pos[2]), 1, 1, fc=color, ec=None)
        r5 = Rectangle((pos[0],pos[1]), 1, 1, fc=color, ec=None)
        r6 = Rectangle((pos[0],pos[1]), 1, 1, fc=color, ec=None)
        rs = [r1, r2, r3, r4, r5, r6]
        for r in rs:
            self.ax.add_patch(r)
        art3d.pathpatch_2d_to_3d(r1, z=pos[0], zdir='x')
        art3d.pathpatch_2d_to_3d(r2, z=pos[0] + 1, zdir='x')
        art3d.pathpatch_2d_to_3d(r3, z=pos[1], zdir='y')
        art3d.pathpatch_2d_to_3d(r4, z=pos[1] + 1, zdir='y')
        art3d.pathpatch_2d_to_3d(r5, z=pos[2], zdir='z')
        art3d.pathpatch_2d_to_3d(r6, z=pos[2] + 1, zdir='z')

if __name__ == "__main__":
    pi = PlotIndividual()
    pi.plot("vxa_demo/404_vox.vxa")
