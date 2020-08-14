#!/usr/bin/python

#cmd line input to run this file:
# >python trips_clean_data.py <Name_directory_inFile>/ <Name_directory_OutFile>/

#clean trips.csv files in present folder and keep cleaned version in new folder tripData
import pandas as pd
import os
import gc
import sys

dirInName = sys.argv[1]
dirOutName = sys.argv[2]


def trips_clean_files(filename):
    print("Processing file:",filename)
    df = pd.read_csv(dirInName+filename, engine='python')
    try:
        df = df[['DAYOFSERVICE','TRIPID','LINEID','ROUTEID','DIRECTION','PLANNEDTIME_ARR','PLANNEDTIME_DEP','ACTUALTIME_ARR','ACTUALTIME_DEP']]
    except KeyError as e:
        print(e)
        return
        
    if not os.path.isdir(dirOutName):
                os.mkdir(dirOutName)

    df_header = pd.DataFrame(columns=df.columns)
    df_header.to_csv(dirOutName+filename, index=False)

    df.to_csv(dirOutName+filename, sep=',',mode ='a',header=False, index=False)

    del df
    gc.collect()

# Return list of files with provided suffix in argument directory 
def find_files_extension(path_dir, suffix=".csv"):
    filenames = os.listdir(path_dir)
    return [filename for filename in filenames if filename.endswith(suffix)]

def generateCleanTripsFiles():
    # clean all csv files in present folder successively
    files = find_files_extension(dirInName, suffix=".csv")
    for file in files:
        trips_clean_files(file)


generateCleanTripsFiles()
