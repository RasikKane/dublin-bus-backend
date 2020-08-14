"""
Courtesey of Author : Sachin Soman
Modified by : Rasik Kane
Last Modified:264 June '20

Description: This script reads stopID.csv file which lists all stops. Using those stops, it extracts data from  API
provided at "https://data.gov.ie/dataset/real-time-passenger-information-rtpi-for-dublin-bus-bus-eireann-luas-and
-irish-rail"
Code generates: bus_stop.csv -->  STOPPOINTID | STOPPOINTNAME | LATITUDE | LONGITUDE
"""

import csv
import requests
import sys

sys.stdout = open("logfile_CSV_maker.txt", "a+")


def get_Request(link):
    """Function to get request object and returns a json . parameter will be API link"""
    try:
        response = requests.get(link)
        try:
            json_response = response.json()
            return json_response, True
        except Exception as e:
            print("Error in json()\n", e)
            return 0, False

    except Exception as e:
        print("Error in requests\n", e)
        return 0, False


def make_CSV(file_stop_id, file_bus_stops, api_request):
    """
    read stopID.csv to fetch stop IDs for which we need to make JSON query
    fetches Json object; convert it into pandas dataframe and make following file:
    bus_stop.csv [STOPPOINTID,STOPPOINTNAME,LATITUDE,LONGITUDE]
    """

    # write header for bus_stop.csv
    try:
        with open(file_bus_stops, 'w', newline='') as csv_bus_stops:
            fields_stopID = ['STOPPOINTID', 'FULLNAME', 'LATITUDE', 'LONGITUDE']
            writer_stopID = csv.DictWriter(csv_bus_stops, fieldnames=fields_stopID)
            writer_stopID.writeheader()

    except Exception as e:
        print("Error in" + file_bus_stops + "writer\n", e)

    # read 'stopID.csv'; a single column csv hence skip header and save all entries into a list 'bus_Stops'
    try:
        with open(file_stop_id, newline='') as f:
            lines = f.readlines()
            bus_Stops = []
            for line in lines[1:]:
                bus_Stops.append(line.split()[0])
    except Exception as e:
        print("Error in " + file_stop_id + "readlines()\n", e)

    # request information for each stop; using string formatting; %s in 'api_request' is replaced by 'stop'
    for stop in bus_Stops:
        json_obj, flag = get_Request(api_request % ("=", stop))
        if flag:
            if len(json_obj["results"]):
                dataEntry_CSV(file_bus_stops, json_obj)
            else:
                print("Empty result returned for", fields_stopID[0], stop)
        else:
            print("Error during API call for", fields_stopID[0], stop)


def dataEntry_CSV(file_bus_stops, json_obj):
    try:
        with open(file_bus_stops, 'a+', newline='') as csv_bus_stops:
            fields_stopID = ['STOPPOINTID', 'FULLNAME', 'LATITUDE', 'LONGITUDE']
            writer_stopID = csv.DictWriter(csv_bus_stops, fieldnames=fields_stopID)

            for stopEntry in range(len(json_obj["results"])):
                data = json_obj["results"][stopEntry]
                stopid = data['stopid']
                if stopid.isnumeric():
                    fullname = data['fullname']
                    latitude = data['latitude'][:15]
                    longitude = data['longitude'][:15]
                else:
                    continue

                try:
                    writer_stopID.writerow(
                        {'STOPPOINTID': stopid, 'FULLNAME': fullname, 'LATITUDE': latitude, 'LONGITUDE': longitude})

                except Exception as e:
                    print("Error in " + str(stopEntry) + "writer entry\n", e)

    except Exception as e:
        print("Error in " + file_bus_stops + "writer\n", e)


if __name__ == "__main__":
    # API to find information about a stop and bus routes served at the stop; %s is to be replaced by "=" and "stopID"
    api = "https://data.smartdublin.ie/cgi-bin/rtpi/busstopinformation?stopid%s%s&format=json&operator=bac"
    make_CSV("../stopID.csv", "../bus_stop.csv", api)
