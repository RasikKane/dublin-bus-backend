#!/usr/bin/python

#cmd line input to run this file:
# >python splitTo_monthly_data.py <Name_directory_inFile>/ <Name_directory_OutFile>/

# saggregate source data in rt_leavetimes_DB_2018.csv, an 11.5 GB file into month_year.csv files
import pandas as pd
import os
import gc
import sys

# dirName = "monthlyData/"
dirInName = sys.argv[1]
dirOutName = sys.argv[2]

# segregate leavetime_split_*.csv files into monthly data
# file is read and features analysed to be dropped are removed [Check notebook for details]
# Further, list of months and years for which data entry are made are obtained
# For each month in an year, seperate csv file is made if not already present
# Data for that month is appended in respective csv file

def toMonthly_files(filename):
    print("Processing file:", dirInName+filename)
    df = pd.read_csv(dirInName+filename)
    # df = df .drop(['DATASOURCE','PASSENGERS', 'PASSENGERSIN', 'PASSENGERSOUT', 'DISTANCE','SUPPRESSED', 'JUSTIFICATIONID', 'LASTUPDATE','NOTE'], axis=1)

    df = df[['DAYOFSERVICE','TRIPID','PROGRNUMBER','STOPPOINTID','PLANNEDTIME_ARR','PLANNEDTIME_DEP','ACTUALTIME_ARR','ACTUALTIME_DEP','VEHICLEID']]

    df['DAYOFSERVICE'] = pd.to_datetime(df['DAYOFSERVICE'])

    months = list(df['DAYOFSERVICE'].dt.month_name().unique())
    years = list(df['DAYOFSERVICE'].dt.year.unique())

    df_header = pd.DataFrame(columns=df.columns)


    for year in years:
        for month in months:

            fname = dirOutName+month+'_'+str(year)+'.csv'

            if not os.path.isdir(dirOutName):
                os.mkdir(dirOutName)

            if not os.path.isfile(fname):
                df_header.to_csv(fname, index=False)

            df.loc[(df['DAYOFSERVICE'].dt.month_name() == month) & (df['DAYOFSERVICE'].dt.year == year)]\
                .to_csv(fname, mode='a', header=False, index=False)

    del df
    gc.collect()

# Seeperated Monthly files may have unordered data
# Thus, monthly files are sorted again by DAYOFSERVICE[Day of the month] and PLANNEDTIME_DEP[Time the bus leaves busstop]
def sortMonthly_files(filename):
    print("Sorting Monthly file:", filename)
    df = pd.read_csv(filename)
    df.sort_values(by=['DAYOFSERVICE', 'PLANNEDTIME_DEP'])\
        .drop_duplicates()\
        .to_csv(filename, index=False)
    del df
    gc.collect()

# Return list of files with provided suffix in argument directory 
def find_files_extension(path_dir, suffix=".csv"):
    filenames = os.listdir(path_dir)
    return [filename for filename in filenames if filename.endswith(suffix)]

# Return count of files with provided suffix in argument directory 
def Count_files_extension(path_dir, suffix=".csv"):
    filenames = os.listdir(path_dir)
    return len([filename for filename in filenames if filename.endswith(suffix)])

def generateMonthlyDataFiles():
    # Convert all csv files in directory to month_year.csv [ and save into dirName = "monthlyData/"]
    for i in range(1, Count_files_extension(dirInName, suffix=".csv")+1):
        file = "leavetime_split_"+str(i)+".csv"
        toMonthly_files(file)

    # Using all CSV files (i.e. leavetime_split_*.csv files) in folder successively, make monthly data files
    files = find_files_extension(dirOutName, suffix=".csv")
    for file in files:
        sortMonthly_files(dirOutName+file)


generateMonthlyDataFiles()
