#!/usr/bin/python

#cmd line input to run this file:
# >python trips_clean_data.py <Name_directory_inFile>/ <Name_directory_OutFile>/

#clean vehicles.csv files in present folder and keep cleaned version in new folder vehicleData
import pandas as pd
import os
import gc
import sys

dirInName = sys.argv[1]
dirOutName = sys.argv[2]


# Drop unnecessary columns by selectring columns of interest
def vehicles_clean_files(filename):
    print("Processing file:", dirInName+filename, engine='python')
    df = pd.read_csv(dirInName+filename)
    try:
        df = df[['DAYOFSERVICE','VEHICLEID','DISTANCE','MINUTES']]
    except KeyError as e:
        print(e)
        return
        
    if not os.path.isdir(dirOutName):
                os.mkdir(dirOutName)

    df_header = pd.DataFrame(columns=df.columns)
    df_header.to_csv(dirOutName+filename, index=False)

    df.to_csv(dirOutName+filename, sep=',',mode='a', header=False, index=False)


    del df
    gc.collect()

# Return list of files with provided suffix in argument directory 
def find_files_extension(path_dir, suffix=".csv"):
    filenames = os.listdir(path_dir)
    return [filename for filename in filenames if filename.endswith(suffix)]

def generateCleanVehiclesFiles():
    # clean all csv files in present folder successively
    files = find_files_extension(dirInName, suffix=".csv")
    for file in files:
        vehicles_clean_files(file)


generateCleanVehiclesFiles()
