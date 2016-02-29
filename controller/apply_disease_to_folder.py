import disease_functions as disease
import ConfigParser

path = sys.argv[1]
config_fn = sys.argv[2]
cp = ConfigParser.RawConfigParser()

cp.read(config_fn)
indiv = cp.get("Disease", "indiv_function")
cell = cp.get("Disease", "cell_function")


for dna_file in os.listdir(path):
    if not dna_file.endswith(".vxa"):
        continue
    print dna_file
    disease.apply_disease(dna_file, indiv, cell)
