import ConfigParser
import os, sys
import subprocess

config = ConfigParser.RawConfigParser()
config.read(sys.argv[1])

if len(sys.argv) > 2:
    run = sys.argv[2]
else:
    run = 0

path_prefix = config.get("Experiment", "path_prefix")
name = config.get("Experiment", "name")
total = path_prefix+name

walltime = config.get("Experiment","self_wall_time")

base = os.path.dirname(os.path.realpath(__file__))

cmd = 'qsub -o '+total+'/main.run' + str(run) + '.output.log -e '+total+'/main.run'+ str(run) +'.error.log -l walltime=' + walltime + ' -v config='+os.path.abspath(sys.argv[1])+',run='+str(run)+',cwd='+base+' '+base+'/controller/scripts/main_resub.sh'
print cmd
output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()[0]

print output
