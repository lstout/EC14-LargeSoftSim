import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from mpl_toolkits.mplot3d import art3d

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

def drawCube(pos, color):
    r1 = Rectangle((pos[1],pos[2]), 1, 1, fc=color, ec=None)
    r2 = Rectangle((pos[1],pos[2]), 1, 1, fc=color, ec=None)
    r3 = Rectangle((pos[0],pos[2]), 1, 1, fc=color, ec=None)
    r4 = Rectangle((pos[0],pos[2]), 1, 1, fc=color, ec=None)
    r5 = Rectangle((pos[0],pos[1]), 1, 1, fc=color, ec=None)
    r6 = Rectangle((pos[0],pos[1]), 1, 1, fc=color, ec=None)
    rs = [r1, r2, r3, r4, r5, r6]
    for r in rs:
        ax.add_patch(r)
    art3d.pathpatch_2d_to_3d(r1, z=pos[0], zdir='x')
    art3d.pathpatch_2d_to_3d(r2, z=pos[0] + 1, zdir='x')
    art3d.pathpatch_2d_to_3d(r3, z=pos[1], zdir='y')
    art3d.pathpatch_2d_to_3d(r4, z=pos[1] + 1, zdir='y')
    art3d.pathpatch_2d_to_3d(r5, z=pos[2], zdir='z')
    art3d.pathpatch_2d_to_3d(r6, z=pos[2] + 1, zdir='z')


drawCube((0,0,0), "violet")
drawCube((1,0,0), "pink")
drawCube((2,0,0), "red")
drawCube((0,1,0), "blue")
drawCube((0,2,0), "lightblue")

ax.set_xlabel('X axis')
ax.set_ylabel('Y axis')
ax.set_zlabel('Z axis')
plt.show()
