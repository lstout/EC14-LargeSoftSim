import mysql.connector
from datetime import datetime
import random


class DB():
    cur = False
    con = False
    maxSimTime = 0
    maxAge = 0
    timeBuffer = 0
    keys_individuals = []
    keys_traces = []
    keys_offspring = []
    tablePrefix = ""
    maxQueries = 1
    currentQueries = 0
    connectionString = ""
    n_random_indivs = 500

    def connect(self):
        if (self.cur):
            self.cur.close()
            print("DB: closed cursor")
        if (self.con):
            self.con.close()
            print("DB: closed conn")
        self.cur = None
        self.con = None

        components = self.connectionString.split("@")
        if len(components) != 2:
            raise ValueError("connection string did have more or less than 1 @ symbol")

        auth = components[0].split(":")
        hostdb = components[1].split("/")
        if len(auth) != 2:
            raise ValueError("connection string did have more or less than 1 : symbol")
        if len(hostdb) != 2:
            raise ValueError("connection string did have more or less than 1 / symbol")

        config = {
            'user': auth[0],
            'password': auth[1],
            'host': hostdb[0],
            'database': hostdb[1],
            'raise_on_warnings': True,
        }

        self.con = mysql.connector.connect(**config)
        self.cur = self.con.cursor(dictionary=True)

    def __init__(self, connectionString, tablePrefix, maxSimTime=0, maxAge=0):
        self.maxSimTime = maxSimTime
        self.maxAge = maxAge
        self.tablePrefix = tablePrefix
        self.connectionString = connectionString
        self.connect()

    def close(self):
        self.con.close()

    def onlyGetIDs(self, results):
        return [indiv["id"] for indiv in results]

    def getHNtodos(self):
        """ retrieve individuals that need to be created (that only exist in the database so far)
        :return: list with strings (individual names)
        """
        self.cur.execute("SELECT * FROM " + self.tablePrefix + "_individuals AS i " +
                         "WHERE i.hyperneated = 0 AND born < '" + str(self.maxSimTime) + "'")
        results = self.cur.fetchall()
        return self.onlyGetIDs(results)

    def getVoxTodos(self):
        """ retrieve individuals that need to be voxelyzed
        :return: list with strings (individual names)
        """
        searchString = "SELECT * FROM " + self.tablePrefix + "_individuals AS i " + \
                       "WHERE i.hyperneated = 1 AND i.vox_submitted = 0"
        self.cur.execute(searchString)
        results = self.cur.fetchall()
        return self.onlyGetIDs(results)

    def getParents(self, indiv):
        """ get parents, if they exist, for a given individual
        :return: list of strings (parent IDs), length of this list is either 0, 1 or 2, for no parents, has been mutated from 1 parent and was created by mating,
        """
        self.cur.execute("SELECT * FROM " + self.tablePrefix + "_offspring AS o " +
                         "WHERE o.child_id = " + str(indiv) + ';')
        result = self.cur.fetchone()
        if not result:
            return []
        else:
            out = [result['parent1_id']]
            if (result['parent2_id'] != None):
                out.append(result['parent2_id'])
            return out


    def markAsHyperneated(self, indiv):
        """ marks the individual as been processed by HyperNEAT. I.e. an actual file was created from database
        :param indiv: string, ID of an individual
        :return: None
        """
        self.cur.execute(
            "UPDATE " + self.tablePrefix + "_individuals SET hyperneated = 1 WHERE id = " + str(indiv) + ";")
        self.flush()

    def markAsVoxelyzed(self, indiv):
        """ marks the individual as been actually processed by Voxelyze
        :param indiv: string, ID of an individual
        :return: None
        """
        self.cur.execute("UPDATE " + self.tablePrefix + "_individuals SET voxelyzed = 1 WHERE id = " + str(indiv) + ";")
        self.flush()

    def markAsVoxSubmitted(self, indiv):
        """ marks the individual as been submitted to Lisa
        :param indiv: string, ID of an individual
        :return: None
        """
        self.cur.execute(
            "UPDATE " + self.tablePrefix + "_individuals SET vox_submitted = 1 WHERE id = " + str(indiv) + ";")
        self.flush()

    def markAsPostprocessed(self, indiv):
        """ marks the individual as successfully mates, trace file moved and corrected
        :param indiv: string, ID of an individual
        :return: None
        """
        self.cur.execute(
            "UPDATE " + self.tablePrefix + "_individuals SET postprocessed = 1 WHERE id = " + str(indiv) + ";")
        self.flush()

    def setFinalTime(self, indiv):
        """ calculate the total time it took to process this individual
        :param indiv: string, ID of an individual
        :return: None
        """
        indiv_obj = self.getIndividual(indiv)
        start_time = datetime.strptime(str(indiv_obj['created_time']), "%Y-%m-%d %H:%M:%S")
        diff_time = datetime.now() - start_time
        self.cur.execute("UPDATE " + self.tablePrefix + "_individuals SET total_time = " + str(
            self.getTotalSeconds(diff_time)) + " WHERE id = " + str(indiv) + ";")
        self.flush()

    def getTotalSeconds(self, timedelta):
        # hack because the total_seconds method only came in python 2.7 and DAS-4 runs 2.6
        return int((timedelta.microseconds + (timedelta.seconds + timedelta.days * 24 * 3600) * 10 ** 6) / 10 ** 6)

    def markAsDead(self, indiv):
        """ marks the individual as unusable
        :param indiv: string, ID of an individual
        :return: None
        """
        self.cur.execute("UPDATE " + self.tablePrefix + "_individuals SET postprocessed = 1, hyperneated = 1, " + \
                         "voxelyzed = 1, vox_submitted =1 WHERE id = " + str(indiv) + ";")
        self.flush()

    def dropTables(self):
        self.cur.execute("SET sql_notes = 0")
        self.cur.execute("DROP TABLE IF EXISTS " + self.tablePrefix + "_individuals")
        self.cur.execute("DROP TABLE IF EXISTS " + self.tablePrefix + "_traces")
        self.cur.execute("DROP TABLE IF EXISTS " + self.tablePrefix + "_firsttraces")
        self.cur.execute("DROP TABLE IF EXISTS " + self.tablePrefix + "_offspring")
        self.cur.execute("DROP TABLE IF EXISTS " + self.tablePrefix + "_jobs")
        self.cur.execute("DROP TABLE IF EXISTS " + self.tablePrefix + "_mates")
        
        self.cur.execute("SET sql_notes = 1")
        self.flush()

    def createTables(self, spaceTolerance):
        self.cur.execute("SET sql_notes = 0")
        self.cur.execute("CREATE TABLE IF NOT EXISTS " +
                         self.tablePrefix + "_individuals " +
                         "(id INT NOT NULL AUTO_INCREMENT, " +
                         "born FLOAT NOT NULL, " +
                         "hyperneated TINYINT(1) DEFAULT 0 NOT NULL, " +
                         "vox_submitted TINYINT(1) DEFAULT 0 NOT NULL, " +
                         "voxelyzed TINYINT(1) DEFAULT 0 NOT NULL, " +
                         "postprocessed TINYINT(1) DEFAULT 0 NOT NULL, " +
                         "traced TINYINT(1) DEFAULT 0 NOT NULL, "
                         "created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, " +
                         "total_time INT, " +
                         "PRIMARY KEY (id) )")
        self.cur.execute("CREATE TABLE IF NOT EXISTS " +
                         self.tablePrefix + "_traces " +
                         "(id INT NOT NULL AUTO_INCREMENT, " +
                         "indiv_id INT NOT NULL, " +
                         "ltime FLOAT NOT NULL, " +
                         "x FLOAT NOT NULL, " +
                         "y FLOAT NOT NULL, " +
                         "z FLOAT NOT NULL, " +
                         "fertile TINYINT(1) DEFAULT 1 NOT NULL, " +
                         "PRIMARY KEY (id), " +
                         "INDEX `individ` (`indiv_id`) )")
        self.cur.execute("CREATE TABLE IF NOT EXISTS " +
                         self.tablePrefix + "_firsttraces " +
                         "(id INT NOT NULL AUTO_INCREMENT, " +
                         "indiv_id INT NOT NULL, " +
                         "ltime FLOAT NOT NULL, " +
                         "x FLOAT NOT NULL, " +
                         "y FLOAT NOT NULL, " +
                         "z FLOAT NOT NULL, " +
                         "fertile TINYINT(1) DEFAULT 1 NOT NULL, " +
                         "PRIMARY KEY (id), " +
                         "INDEX `individ` (`indiv_id`) )")
        self.cur.execute("CREATE TABLE IF NOT EXISTS " +
                         self.tablePrefix + "_offspring " +
                         "(id INT NOT NULL AUTO_INCREMENT, " +
                         "parent1_id INT NOT NULL, " +
                         "parent2_id INT, " +
                         "child_id INT NOT NULL, " +
                         "ltime FLOAT NOT NULL, " +
                         "PRIMARY KEY (id) )")
        self.cur.execute("CREATE TABLE IF NOT EXISTS " +
                         self.tablePrefix + "_jobs " +
                         "(id INT NOT NULL AUTO_INCREMENT, " +
                         "jname VARCHAR(20), " +
                         "cmd TEXT, " +
                         "start TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, " +
                         "done DATETIME DEFAULT NULL, " +
                         "individuals TEXT DEFAULT NULL, " +
                         "PRIMARY KEY (id) )")
        self.cur.execute("CREATE TABLE IF NOT EXISTS " +
                         self.tablePrefix + "_mates " +
                         "(line INT NOT NULL AUTO_INCREMENT, " +
                         "id INT NOT NULL, " +
                         "indiv_id INT NOT NULL, " +
                         "ltime FLOAT NOT NULL, " +
                         "x FLOAT NOT NULL, " +
                         "y FLOAT NOT NULL, " +
                         "z FLOAT NOT NULL, " +
                         "mate_id INT NOT NULL, " +
                         "mate_indiv_id INT NOT NULL, " +
                         "mate_ltime FLOAT NOT NULL, " +
                         "mate_x FLOAT NOT NULL, " +
                         "mate_y FLOAT NOT NULL, " +
                         "mate_z FLOAT NOT NULL, " +
                         "fertile TINYINT(1) DEFAULT 1 NOT NULL, " +
                         "PRIMARY KEY (line), " +
                         "INDEX `individ` (`indiv_id`) )")
        self.cur.execute("SET sql_notes = 1")
        self.flush()

    def createIndividual(self, born, x, y):
        self.cur.execute("INSERT INTO " + self.tablePrefix + "_individuals VALUES (NULL, '" + str(
            born) + "', 0, 0, 0, 0, 0, NULL, NULL);")
        individual_id = self.getLastInsertID()
        self.cur.execute(
            "INSERT INTO " + self.tablePrefix + "_firsttraces VALUES (NULL, " + individual_id + ", '" + str(
                born) + "', '" + str(x) + "', '" + str(
                y) + "', 0, 1);")
        self.flush()
        print ("created individual: " + individual_id)

        return individual_id

    def addTraces(self, id, traces):
        firstTrace = self.getFirstTrace(id)
        insertSting = "INSERT INTO " + self.tablePrefix + "_traces VALUES (NULL, %s, %s, %s, %s, %s, %s);"
        self.cur.executemany(insertSting, traces)
        # self.cur.execute("DELETE FROM "+self.tablePrefix+"_traces WHERE id={id};".format(id=firstTrace["id"]))
        self.flush()

    def getPopulationTotal(self):
        self.cur.execute("SELECT COUNT(id) FROM " + self.tablePrefix + "_individuals")
        result = self.cur.fetchall()
        return result[0]['COUNT(id)']

    def getIndividual(self, id):
        self.cur.execute("SELECT * FROM " + self.tablePrefix + "_individuals AS i WHERE i.id = '" + str(id) + "' ")
        return self.cur.fetchone()

    def getTraces(self, id):
        self.cur.execute("SELECT * FROM " + self.tablePrefix + "_traces AS t WHERE t.indiv_id = '" + str(id) + "' ")
        return self.cur.fetchall()

    def getFirstTrace(self, id):
        self.cur.execute("SELECT * FROM " + self.tablePrefix + "_firsttraces AS t WHERE t.indiv_id = '" + str(
            id) + "' ORDER BY t.id ASC LIMIT 1")
        return self.cur.fetchone()

    def getUnfinishedIndividuals(self):
        self.cur.execute("SELECT COUNT(id) FROM " + self.tablePrefix + "_individuals WHERE postprocessed = 0")
        result = self.cur.fetchall()
        return result[0]['COUNT(id)']

    def flush(self):
        self.con.commit()

    def addJob(self, name, cmd, individuals=[]):
        name = name.replace("'", "\\'")
        cmd = cmd.replace("'", "\\'")
        if len(individuals):
            indivs = ",".join(map(str,individuals))
        else:
            indives = ''
        insertSting = "INSERT INTO " + self.tablePrefix + "_jobs VALUES (NULL, '{name}', '{cmd}', NOW(), NULL, '{indivs}');"
        self.cur.execute(insertSting.format(name=name, cmd=cmd, indivs=indivs))
        self.flush()

    def finishJobs(self):
        """
        Finishes jobs that are completed
        returns the number of jobs that are still running
        """
        queryString = "SELECT * FROM " + self.tablePrefix + "_jobs WHERE done IS NULL;"
        self.cur.execute(queryString)
        result = self.cur.fetchall()
        remaining = 0
        for job in result:
            for ind in job['individuals'].split(','):
                if ind == u'':
                    continue 
                queryString = "SELECT * FROM " + self.tablePrefix + "_individuals WHERE id = " + ind + ";"
                self.cur.execute(queryString)
                result = self.cur.fetchone()
                if not result['voxelyzed']:
                    remaining += 1
                    break
            else:
                queryString = "UPDATE " + self.tablePrefix + "_jobs SET done=NOW()  WHERE id = " + str(job['id']) +";"
                self.cur.execute(queryString)
        
        return remaining

    def getLastInsertID(self):
        self.cur.execute("SELECT LAST_INSERT_ID();")
        individual_id = self.cur.fetchone()['LAST_INSERT_ID()']
        return str(individual_id)

    def makeBaby(self, parent1, parent2, ltime, single=False, infertileSpan=0.25, arena_x=5, arena_y=5, randomPlace=False):
        if randomPlace:
            x = random.uniform(0, arena_x)
            y = random.uniform(0, arena_y)
        else:
            x = (parent1["x"] + parent2["x"]) / 2
            y = (parent1["y"] + parent2["y"]) / 2
        id = self.createIndividual(ltime, x, y)
        insertString = "INSERT INTO " + self.tablePrefix + "_offspring VALUES (NULL, {parent1}, {parent2}, {child}, {ltime});"
        self.cur.execute(
            insertString.format(parent1=parent1["indiv_id"], parent2=parent2["indiv_id"], child=id, ltime=ltime))
        if not single:
            self.infertilize(parent1["indiv_id"], ltime, infertileSpan)
            self.infertilize(parent2["indiv_id"], ltime, infertileSpan)
        self.flush()
        return id

    def infertilize(self, parent, start, timespan):
        updateString = "UPDATE " + self.tablePrefix + "_traces SET fertile = 0 WHERE indiv_id = {indiv} AND ltime >= {start} AND ltime < {end}"
        self.cur.execute(updateString.format(indiv=parent, start=start, end=start + timespan))

    def getMates(self, indiv):
        querySting = "SELECT * FROM " + self.tablePrefix + "_mates WHERE indiv_id={indiv};"
        self.cur.execute(querySting.format(indiv=indiv))
        result = self.cur.fetchall()
        return result

    def getRandomMate(self, indiv_id):
        lifetime = self.getLifetime(indiv_id)
        query = "SELECT * AS rid FROM " + self.tablePrefix + "_mates 
        WHERE ltime > {birth} AND ltime < {death} AND fertile=1;".format(birth=lifetime['MIN(ltime)'], death=lifetime['MAX(ltime']))
        self.cur.execute(query)
        result = self.cur.fetchall()
        if result:
            return random.choice(result)
        else:
            r1_id = self.getRandomIndiv()
            r1_id = self.getRandomIndiv()
            ltime = random.uniform(lifetime['MIN(ltime)',lifetime['MAX(ltime'])
            new_mate_event = {"line": 0,
                       "id": 0,
                       "indiv_id": r1["id"],
                       "ltime": ltime,
                       "x": 0,
                       "y": 0,
                       "z": 0,
                       "mate_id": 0,
                       "mate_indiv_id": r2["id"],
                       "mate_ltime": ltime,
                       "mate_x": 0,
                       "mate_y": 0,
                       "mate_z": 0,
                       "fertile": 1} 
            return new_mate_event

    def getRandomIndiv(self):
        query = "SELECT id FROM " + self.tablePrefix + "_individuals;"
        query2 = "SELECT * FROM " + self.tablePrefix + "_individuals WHERE id = {indiv_id};"
        self.cur.execute(query1)
        result = self.cur.fetchall()
        return random.choice(result)['id']

    def getTerritory(self, id):
        query = "SELECT MIN(x), MAX(x), MIN(y), MAX(y) " + \
                "FROM " + self.tablePrefix + "_traces " + \
                "WHERE indiv_id = " + id
        self.cur.execute(query)
        result = self.cur.fetchone()
        return result

    def getLifetime(self, id):
        query = "SELECT MIN(ltime), MAX(ltime) FROM " + self.tablePrefix + "_traces " + \
                "WHERE indiv_id = " + id
        self.cur.execute(query)
        result = self.cur.fetchone()
        return result

    def getPossibleMates(self, id, territory, lifetime):
        query = "SELECT * FROM " + self.tablePrefix + "_traces "+ \
                "WHERE indiv_id != {id} AND " + \
                "x BETWEEN {min_x} AND {max_x} AND " + \
                "y BETWEEN {min_y} AND {max_y} AND " + \
                "ltime BETWEEN {min_t} AND {max_t}"
        query = query.format(id=id, min_x = territory['MIN(x)'], max_x = territory['MAX(x)'], min_y = territory['MIN(y)'], max_y = territory['MAX(y)'], min_t = lifetime['MIN(ltime)'], max_t = lifetime['MAX(ltime)'])
        self.cur.execute(query)
        result = self.cur.fetchall()
        return result

    def insertMates(self, mates):
        query = "INSERT INTO " + self.tablePrefix + "_mates" + \
            "(id, indiv_id, ltime, x, y, z, mate_id, mate_indiv_id, mate_ltime, mate_x, mate_y, mate_z, fertile) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        transformed = []
        for t, m in mates:
            event = [ t['id'], t['indiv_id'],  t['ltime'], t['x'], t['y'], t['z'], m['id'],  m['indiv_id'], m['ltime'],  m['x'], m['y'], m['z'], 1]
            transformed.append(event)

        self.cur.executemany(query, transformed)
        self.flush()
