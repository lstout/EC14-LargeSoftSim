import ConfigParser
import random
import shutil
import threading, time, os
from db import DB
from preprocessing import Preprocessor
import cPickle as pickle
import math


class PostprocessingWorker(threading.Thread):
    """ Python script for Postprocessing worker... runs until cancelled or till max waiting time
    """

    pause_time = 2
    max_waiting_time = 60 * 60  # 60seconds * 60min = 1 hour in seconds
    base_path = ""
    saves_path = "mating_progress/"
    pickle_prefix = ""
    get_save = False
    pop_path = "population/"
    traces_path = "traces_afterVox/"
    traces_backup_path = "traces_afterVox_backup/"
    traces_during_pp_path = "traces_duringPP/"
    traces_after_pp_path = "traces_afterPP/"
    debug = False
    db = None
    queue = set()
    vox_preamble = 8  # number of lines that voxelyze adds before the actual output in a trace file
    config = ConfigParser.RawConfigParser()
    arena_x = 0
    arena_y = 0
    arena_type = ""
    end_time = 0
    timeTolerance = 0.0  # maximum mating time distance
    spaceTolerance = 0.01  # maximum mating distance radius
    one_child = False
    infertile_birth = False
    infertile_birth_percent = 0.1
    area_birthcontrol = False
    area_birthcontrol_radius = 0.05
    area_birthcontrol_cutoff = 25
    population_cap = False
    pp = Preprocessor()
    indiv_max_age = 0
    indiv_infertile = False
    indiv_infertile_span = 0.25
    random_birth_place = False
    queue_length = 1
    timestep = 0.002865
    pick_from_pool = False

    def readConfig(self, config_path):
        self.config.read(config_path)
        self.exp_name = self.config.get('Experiment', 'name')
        self.path_prefix = self.config.get('Experiment', 'path_prefix')
        self.debug = self.config.get('Experiment', 'debug')
        self.end_time = self.config.getfloat('Experiment', 'end_time')

        self.base_path = os.path.expanduser(self.path_prefix + self.exp_name) + "/"
        self.queue_length = self.config.getint('Postprocessing', 'queue_len')
        self.pop_path = self.config.get('Postprocessing', 'pop_path')
        self.traces_path = self.config.get('Postprocessing', 'traces_path')
        self.traces_backup_path = self.config.get('Postprocessing', 'traces_backup_path')
        self.traces_during_pp_path = self.config.get('Postprocessing', 'traces_during_pp_path')
        self.traces_after_pp_path = self.config.get('Postprocessing', 'traces_after_pp_path')
        self.vox_preamble = self.config.getint('Postprocessing', 'vox_preamble')
        self.timestep = self.config.getfloat('Postprocessing', 'timestep')

        self.pause_time = self.config.getint('Workers', 'pause_time')
        self.max_waiting_time = self.config.getint('Workers', 'max_waiting_time')

        self.timeTolerance = self.config.getfloat('Mating', 'timeTolerance')
        self.spaceTolerance = self.config.getfloat('Mating', 'spaceTolerance')
        self.indiv_infertile = self.config.getboolean('Mating', 'indiv_infertile')
        self.indiv_infertile_span = self.config.getfloat('Mating', 'indiv_infertile_span')
        self.one_child = self.config.getboolean('Mating', 'onlyOneChildPerParents')
        self.infertile_birth = self.config.getboolean('Mating', 'infertileAfterBirth')
        self.infertile_birth_percent = self.config.getfloat('Mating', 'infertileAfterBirthPercentage')
        self.area_birthcontrol = self.config.getboolean('Mating', 'areaBirthControl')
        self.area_birthcontrol_radius = self.config.getfloat('Mating', 'areaBirthControlRadius')
        self.area_birthcontrol_cutoff = self.config.getfloat('Mating', 'areaBirthControlCutoff')
        self.population_cap = self.config.getboolean('Mating', 'populationCap')
        self.random_birth_place = self.config.getboolean('Mating', 'randomBirthPlace')
        self.pick_from_pool = self.config.getboolean('Mating', 'pickFromPool')

        self.arena_x = self.config.getfloat('Arena', 'x')
        self.arena_y = self.config.getfloat('Arena', 'y')
        self.arena_type = self.config.get('Arena', 'type')

        self.indiv_max_age = self.config.getfloat('Population', 'indiv_max_age')

    def __init__(self, dbParams, config_path):
        threading.Thread.__init__(self)
        self.db = DB(dbParams[0], dbParams[1], dbParams[2], dbParams[3])
        self.readConfig(config_path)

        self.stopRequest = threading.Event()

    def run(self):
        """ main thread function
        :return: None
        """
        waitCounter = 0
        startTime = time.time()

        obs_path = os.path.normpath(self.base_path + self.traces_path)

        while not self.stopRequest.isSet() and waitCounter < self.max_waiting_time:
            self.dirCheck(obs_path)

            if (len(self.queue) > 0):
                item = self.queue.pop()
                if self.debug:
                    print "PP: working on id", item
                self.markAsVoxelyzed(item)
                self.moveFilesToTmp(item)
                self.adjustTraceFile(item)
                self.traceToDatabase(item)
                self.findMates(item)
                babies = self.calculateOffspring(item)
                self.makeBabies(babies)
                self.moveFilesToFinal(item)
                self.markAsPostprocessed(item)
                self.db.cleanTraces()
                waitCounter = 0
            else:
                if (self.debug):
                    print("PP: found nothing")
                waitCounter += time.time() - startTime
                startTime = time.time()

                jobsRunning = self.db.finishJobs()

                if (self.debug):
                    print("PP: {n} jobs currently waiting in LISA queue...".format(n=jobsRunning))
                    print("PP: sleeping now for " + str(self.pause_time) + "s")

                self.stopRequest.wait(self.pause_time)

        print ("PP: got exit signal... cleaning up")
        self.join()

    def join(self, timeout=None):
        """ function to terminate the thread (softly)
        :param timeout: not implemented yet
        :return: None
        """
        if (self.debug):
            print("PP: got kill request for thread")
        self.stopRequest.set()
        super(PostprocessingWorker, self).join(timeout)

    def getIDfromTrace(self, file_path):
        path, filename = os.path.split(file_path)
        name_parts = filename.split(".")
        return name_parts[0]

    def dirCheck(self, path):
        """ upon start check if there are files in the target diretory, because the watcher only notices files being moved there while running
        :return: None
        """
        unprocessed = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.endswith('.trace')]
        self.queue |= set(unprocessed)
        return self.queue 

    def markAsVoxelyzed(self, todo):
        """ mark all the individuals as voxelyzed, i.e. as successfully processed by Voxelyze
        :param todos: list of strings with trace file paths
        :return: None
        """
        id = self.getIDfromTrace(todo)
        self.db.markAsVoxelyzed(id)

    def markAsPostprocessed(self, todo):
        """ mark all the individuals as postprocessed, i.e. all offspring has been calculated, files have been moved and the individuals are basically done
        :param todos: list of strings with trace file paths
        :return: None
        """
        id = self.getIDfromTrace(todo)
        self.db.markAsPostprocessed(id)
        self.db.setFinalTime(id)

    def adjustTraceFile(self, todo):
        """ put the individuals into an arena, correct their coordinates, etc.
        :param todos: list of strings with the individual trace filepaths
        :return: None
        """

        id = self.getIDfromTrace(todo)
        # get initial coordinates from DB
        indiv = self.db.getIndividual(id)
        first_trace = self.db.getFirstTrace(id)
        self.pp.addStartingPointArenaAndTime(self.getPathDuringPP(id),
                                             self.vox_preamble,
                                             self.arena_x,
                                             self.arena_y,
                                             self.arena_type,
                                             first_trace["x"],
                                             first_trace["y"],
                                             indiv["born"],
                                             self.timestep)

    def traceToDatabase(self, todo):
        """ put the individuals into the database
        :param todos: list of strings with the individual trace filepaths
        :return: None
        """

        id = self.getIDfromTrace(todo)
        with open(self.getPathDuringPP(id), 'r') as inputFile:
            traces = []

            fileAsList = inputFile.readlines()
            fileLen = len(fileAsList)
            for i in range(0, fileLen):
                fertile = 1
                if (self.infertile_birth):
                    if (i <= self.infertile_birth_percent * fileLen):
                        fertile = 0
                traceLine = fileAsList[i].split()
                traces.append([id, traceLine[1], traceLine[2], traceLine[3], traceLine[4], fertile])
        self.db.addTraces(id, traces)

    def filterPopulationCap(self, id, mates):
        if len(mates) > 0:
             return [random.choice(mates)]
        else:
            return []

    def matesToBabies(self, mates):
        babies = []
        for line in mates:
            parent1 = {}
            parent1["id"] = line["id"]
            parent1["indiv_id"] = line["indiv_id"]
            parent1["ltime"] = line["ltime"]
            parent1["x"] = line["x"]
            parent1["y"] = line["y"]
            parent1["z"] = line["z"]

            parent2 = {}
            parent2["id"] = line["mate_id"]
            parent2["indiv_id"] = line["mate_indiv_id"]
            parent2["ltime"] = line["mate_ltime"]
            parent2["x"] = line["mate_x"]
            parent2["y"] = line["mate_y"]
            parent2["z"] = line["mate_z"]
            babies.append([parent1, parent2, line["ltime"]])
        return babies

    def calculateOffspring(self, todo):
        """ Generate offspring, calculate where the individual met others               :param todo: Strings with the individual IDs
        :return: list of babies to make
        """

        if (not os.path.exists(todo)) or os.path.getsize(todo) == 0:
            return [] 
        id = self.getIDfromTrace(todo)
        mates = self.db.getMates(id)

        if self.population_cap:
            mates = self.filterPopulationCap(id, mates)
        if not mates:
            if self.debug:
                print 'PP: Did not find a mate, getting a random one for id:', id
            randomMate = self.db.getRandomMate(id)
            mates.append(randomMate)
        return self.matesToBabies(mates)

    def close_in_time(self, t1, t2):
        return abs(t1['ltime']-t2['ltime']) <= self.timeTolerance

    def close_in_space(self, t1, t2):
        return math.sqrt((t1['x'] - t2['x'])**2 + (t1['y'] - t2['y'])**2) <= self.spaceTolerance

    def findMates(self, indiv_path):
        id = self.getIDfromTrace(indiv_path)
        traces = self.db.getTraces(id)
        territory = self.db.getTerritory(id)
        lifetime = self.db.getLifetime(id)
        if not all(territory.values()) or not all(lifetime.values()):
            return
        possibleMates = self.db.getPossibleMates(id, territory, lifetime)
        mates = []
        for t in traces:
            for p in possibleMates:
                if self.close_in_time(t, p) and self.close_in_space(t, p):
                    mates.append((t,p))
        self.db.insertMates(mates)
    
    def makeBabies(self, babies):
        for baby in babies:
            self.db.makeBaby(baby[0], baby[1], baby[2], self.one_child,
                             self.indiv_max_age * self.indiv_infertile_span,
                             self.arena_x, self.arena_y, self.random_birth_place)

    def getPathDuringPP(self, id):
        return self.base_path + self.traces_during_pp_path + str(id) + ".trace"

    def moveFilesToTmp(self, indiv):
        """ once all preprocessing is done, move the files to their target destination
        :param todos: list of strings with the individual IDs
        :return: None
        """
        id = self.getIDfromTrace(indiv)
        try:
            shutil.copy2(indiv, self.base_path + self.traces_backup_path + str(id) + ".trace")
            shutil.copy2(indiv, self.getPathDuringPP(id))
        except:
            pass

    def moveFilesToFinal(self, indiv):
        """ once all preprocessing is done, move the files to their target destination
        :param todos: list of strings with the individual IDs
        :return: None
        """
        id = self.getIDfromTrace(indiv)
        if os.path.isfile(self.getPathDuringPP(id)):
            shutil.move(self.getPathDuringPP(id),
                        self.base_path + self.traces_after_pp_path + str(id) + ".trace")
        if os.path.isfile(indiv):
            os.remove(indiv)
