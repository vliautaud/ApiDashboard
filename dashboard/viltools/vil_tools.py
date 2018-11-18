import logging

# #######################################################################
# Parsing d'un fichier de conf qui retourne un dictionnaire clé/Valeur
# ####################################################################### 
def config_dict(filename):
    """Convert content of config-file into dictionary."""
    with open(filename, "r") as f:
        cfglines = f.readlines()
    cfgdict = {}
    for line in cfglines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        key_value = line.split("=")
        if len(key_value)==1 :
            print("Bad line in config-file %s:\n%s" % (filename,line))
            continue
        key,value=key_value[0],"=".join(key_value[1:])
        key = key.strip()
        value = value.strip()
        if value in ["True", "False", "None", "''", '""']:
            value = eval(value)
        else:
            try:
                if "." in value:
                    value = float(value)
                else:
                    value = int(value)
            except ValueError:
                pass # value need not be converted
        cfgdict[key] = value
    return cfgdict

# #############################################################
# Initialisation Fwk Python (logging + Fichier de conf
# In : emplacement/nom du fichier de conf
# Out : Dictionnaire cle/valeur correspondant au fichier de conf
# #############################################################
def fwk_init(conf_file) :
    myconf = config_dict(conf_file)
    #logging.basicConfig(filename=myconf["LOG_FILE"],level=myconf["LOG_LEVEL"],format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S %p')
    return myconf
