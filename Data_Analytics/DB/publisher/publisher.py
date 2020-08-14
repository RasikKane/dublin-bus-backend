import sys
from datetime import datetime
import pymysql

sys.stdout = open("logfile.txt", "a+")

featureList = {"bus_stops": ("stop_id", "stop_name", "stop_lat", "stop_lng"),
               "stops_routes": ("route", "direction", "stop_id", "program_number"),
               "lines_prognumbers": ("line_id", "direction", "first_program_number", "last_program_number"),
               "lines_routeids": ("direction", "line_id", "route_id"),
               "timetable": ("line_id", "direction", "stop_id", "program_number", "planned_arrival"),
               "weather": ("date_weather", "hour_of_day", "feels_like", "wind_speed", "weather_id",
                           "temp", "temp_min", "temp_max", "humidity", "weather_main", "weather_description")
               }
arg = {"bus_stops": " VALUES (%s, %s, %s, %s)", "stops_routes": " VALUES (%s, %s, %s, %s)",
       "lines_prognumbers": "VALUES (%s, %s, %s, %s)", "lines_routeids": "VALUES (%s, %s, %s)",
       "timetable": "VALUES (%s, %s, %s, %s, %s)", "weather": "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"}


# Connection handle to database
def connectDB():
    try:
        # Local connection
        return pymysql.connect(host="localhost", user="root", password="localhost", database="dublin_bus", port=3306,
                               cursorclass=pymysql.cursors.DictCursor)

        # Server connection:
        # return pymysql.connect(host="dublinbikes.cpj6pmkzrors.eu-west-1.rds.amazonaws.com", user="dublinbikes",
        #                        password="dba94w5p7", database="dublin_bike_schema", port=3306, \
        #                        cursorclass=pymysql.cursors.DictCursor)
    except Exception as e:
        print("Error connectDB", e, datetime.now())


# Push data to a database table
def publish(table, features, attr):
    global arg
    try:
        dublinBike_connect = connectDB()
        with dublinBike_connect.cursor() as cursor:
            sql = "INSERT IGNORE INTO " + table + " (" + features + ")" + arg[table]
            cursor.executemany(sql, attr)
        dublinBike_connect.commit()
        dublinBike_connect.close()
        print("valid entry made for key", attr[0][0], attr[0][1])
    except Exception as e:
        # dublinBike_connect.rollback()
        print("Error publish", attr[0][0], attr[0][1], e, datetime.now())



# # Check if a station entry is made in static database or not
# def Check_StaticEntry(table, features, attr):
#     try:
#         dublinBike_connect = connectDB()
#         with dublinBike_connect.cursor() as cursor:
#             sql = "SELECT " + features + " from " + table + " where " + features + " = %s"
#             cursor.execute(sql, attr)
#             dublinBike_connect.close()
#             return cursor.rowcount == 1
#     except Exception as e:
#         print("Error Check_StaticEntry", e, datetime.now())


# Return count of entries into a database table
def count_Entry(table):
    try:
        dublinBike_connect = connectDB()
        with dublinBike_connect.cursor() as cursor:
            sql = "SELECT count(*) from " + table
            cursor.execute(sql)
            rows = cursor.fetchone()
            dublinBike_connect.close()
            return rows['count(*)']
            # return cursor.rowcount
    except Exception as e:
        print("Error", e, datetime.now())


def make_data_entry(file_path, table, features):
    print("Entries for table",table," : schema",features)
    # read csv file; skip header and save all entries in table
    try:
        with open(file_path, newline='') as f:
            lines = f.readlines()
            attr = list()
            # Ignore header of CSV and make list of tuples to enter in database table
            for line in lines[1:]:
                attr.append(line.strip().split(","))
            # list of table columns
            features_string = ','.join(str(s) for s in features)
            # Publish data to database table
            publish(table, features_string, attr)

    except Exception as e:
        print("Error occured at writer part\n", e)



if __name__ == "__main__":
    # make_data_entry("../bus_stop.csv", "bus_stops", featureList["bus_stops"])
    make_data_entry("../stops_routes.csv", "stops_routes", featureList["stops_routes"])
    # make_data_entry("../lines_progr.csv", "lines_prognumbers", featureList["lines_prognumbers"])
    # make_data_entry("../dominant_route.csv", "lines_routeids", featureList["lines_routeids"])
    # make_data_entry("../ML/leavetimes_trips_arr_TIMETABLE.csv", "timetable", featureList["timetable"])
    # make_data_entry("../ML/weather_extendedTime_2018.csv", "weather", featureList["weather"])

# from django.db import models
#
#
# # Create your models here.
# class Weather(models.Model):
#     date_entry = models.CharField(max_length=10, blank=False)
#     hour_Day = models.IntegerField(blank=False)
#     feels_like = models.CharField(max_length=5, blank=False)
#     wind_speed = models.CharField(max_length=5, blank=False)
#     weather_id = models.CharField(max_length=5, blank=False)
#
#     class Meta:
#         managed = True
#         db_table = 'weather'
#         unique_together = (('date_entry', 'hour_Day'),)
