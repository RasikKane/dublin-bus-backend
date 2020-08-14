This repo forms the backend of Dublin Bus application which is the project to be done for Research Practicum. 
In this project, user will enter start and end destination. Using ML models, a travel time will be generated
and displayed to the user. Django framework of Python is used as the backend technology.


### `Data analytics`

This directory contains notebooks used for creating prediction models for dublin bus arrival time at bus stops. 
* Each notebook has markdown explaining operations.

### `EDA`

Exploratory data anlytics and CSV file creation for model training is done using notebooks in the directory. 

### `ML`

Machine learning efforts to train Linear regression/ LGBM prediction models using One hot encoding/ Nominal encoding are enlisted in notebooks. These models work towards Dublin Bus arrival 

### `RTPI_API`

[Real Time Passenger Information](https://data.gov.ie/dataset/real-time-passenger-information-rtpi-for-dublin-bus-bus-eireann-luas-and-irish-rail) API for dublin bus gives information about operational bus stop. 

### `Reports` 

Frequency distribution for ROUTEIDs of dublin Buses

### `DB`

This directory contains codes for generating relevant CSVs contributing to EDA

### `processingFiles`

python Files used to clean raw dublin bus data

#### `NOTE`

* Base CSV files containing Dublin Bus data 2018, Weather data 2018, and any other csv files generated in process are not published 
* This is in line with Data protection guidelines by UCD School of computer science for module COMP47360-Research Practicum (MSc Conv) 
