import csv, sys
from itertools import islice
distX, distY, distZ, oldX, oldY, oldZ = 0.0,0.0,0.0,0.0,0.0,0.0
traceFile = str(sys.argv[1])
with open(traceFile, 'rb') as input:
	linereader = csv.reader(input, delimiter=' ')
	for row in islice(linereader, 8, None):
		if (row[0] == "Ended"):
			continue
		if (oldX != 0):
			distX += abs(oldX - float(row[2]))
			distY += abs(oldY - float(row[3]))
			distZ += abs(oldZ - float(row[4]))
		oldX = float(row[2])
		oldY = float(row[3])
		oldZ = float(row[4])
print ("distance \nX:{}\nY:{}\nZ:{}".format(distX, distY, distZ)) 

