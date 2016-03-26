import random
import sys
import math


class Preprocessor():
    def forceStep(self, val, step):
        return val // step * step

    def correctBirth(self, coordinates, birthX, birthY, birthTime, step):
        coordinates[1] = self.forceStep(coordinates[1] + birthTime, step)
        coordinates[2] = coordinates[2] + birthX
        coordinates[3] = coordinates[3] + birthY
        return coordinates

    def correctArena(self, coordinates, arenaX, arenaY):
        if coordinates[2] < 0:
            coordinates[2] = coordinates[2] + arenaX
        if coordinates[2] > arenaX:
            coordinates[2] = coordinates[2] - arenaX
        if coordinates[3] < 0:
            coordinates[3] = coordinates[3] + arenaY
        if coordinates[3] > arenaY:
            coordinates[3] = coordinates[3] - arenaY
        return coordinates

    def addStartingPointArenaAndTime(self, filename, vox_preamble=8, arenaX=5, arenaY=5, arenaType="i", birthX=0, birthY=0, birthTime=0, timestep=0.002865):
        out = []
        with open(filename, 'r') as inputFile:
            for i, line in enumerate(inputFile):
                if i < 8:
                    continue
                coordinates = line.split()
                if coordinates[0] == 'Ended':
                    break
                coordinates = map(float, coordinates)
                coordinates = self.correctBirth(coordinates, birthX, birthY, birthTime, timestep)
                coordinates = self.correctArena(coordinates, arenaX, arenaY)
                coordinates = map(str, coordinates)
                out.append("\t".join(coordinates))

        with open(filename, 'w') as outputFile:
            outputFile.write("\n".join(out))
