import orjson
import csv
from openpyxl import Workbook
from datetime import datetime
import matplotlib.pyplot as plt
from collections import OrderedDict


path = r"D:\Users\MatunPC\Documents\Koodit\spotifyparse"



def gather_data(path):

    data= []
    i = 0
    while True:
        try:
            with open("endsong_{:d}.json".format(i), "rb") as f:
                data.extend(orjson.loads(f.read()))
            i += 1
        except:
            break
    return data


def get_artist_data(data):

    artist_data = {}

    for instance in data:
        artist_name = instance["master_metadata_album_artist_name"]
        seconds = instance["ms_played"] / 1000

        if artist_name != None:
            if artist_name not in artist_data:
                artist_data[artist_name] = {"seconds_played": seconds}
            elif artist_name in artist_data:
                artist_data[artist_name]["seconds_played"] += seconds
            else:
                print("Error occurred in getting artist data.")
                return None

    artist_data = dict(sorted(artist_data.items(), key=lambda x: x[1]["seconds_played"], reverse=True))

    for i in list(artist_data.keys()):
        if artist_data[i]["seconds_played"] < 60:
            del artist_data[i]

    for i in artist_data:
        artist_data[i]["minutes_played"] = artist_data[i].pop("seconds_played")
        artist_data[i]["minutes_played"] = artist_data[i]["minutes_played"] // 60

    return artist_data



def get_track_data(data):

    track_data = {}

    for instance in data:
        track_name = instance["master_metadata_track_name"]
        seconds = instance["ms_played"] / 1000

        if track_name != None:
            if track_name not in track_data:
                track_data[track_name] = {"seconds_played": seconds}
            elif track_name in track_data:
                track_data[track_name]["seconds_played"] += seconds
            else:
                print("Error occurred in getting artist data.")
                return None

    track_data = dict(sorted(track_data.items(), key=lambda x: x[1]["seconds_played"], reverse=True))

    for i in list(track_data.keys()):
        if track_data[i]["seconds_played"] < 60:
            del track_data[i]

    for i in track_data:
        track_data[i]["minutes_played"] = track_data[i].pop("seconds_played")
        track_data[i]["minutes_played"] = track_data[i]["minutes_played"] // 60

    return track_data


def get_weekday_data(data):

    weekdays_data = {"Mon": {"Podcast": 0, "Music": 0}, "Tue": {"Podcast": 0, "Music": 0}, "Wed": {"Podcast": 0, "Music": 0}, "Thu": {"Podcast": 0, "Music": 0}, "Fri": {"Podcast": 0, "Music": 0}, "Sat": {"Podcast": 0, "Music": 0}, "Sun": {"Podcast": 0, "Music": 0}}

    for instance in data:
        seconds = instance["ms_played"] / 1000
        day_data = instance["ts"].replace("Z", "").split("T")[0]
        year, month, day = day_data.split("-")
        year = int(year)
        month = int(month)
        day = int(day)
        weekday = datetime(year, month, day).weekday()

        if instance["master_metadata_track_name"] == None:
            type = "Podcast"
        else:
            type = "Music"

        if weekday == 0:
            weekdays_data["Mon"][type] += seconds
        elif weekday == 1:
            weekdays_data["Tue"][type] += seconds
        elif weekday == 2:
            weekdays_data["Wed"][type] += seconds
        elif weekday == 3:
            weekdays_data["Thu"][type] += seconds
        elif weekday == 4:
            weekdays_data["Fri"][type] += seconds
        elif weekday == 5:
            weekdays_data["Sat"][type] += seconds
        elif weekday == 6:
            weekdays_data["Sun"][type] += seconds

    for i in weekdays_data:
        weekdays_data[i]["Podcast"] = weekdays_data[i]["Podcast"] // 3600
        weekdays_data[i]["Music"] = weekdays_data[i]["Music"] // 3600

    return weekdays_data


def get_time_data(data):

    ret = []
    for i in ["year", "month", "hour"]:

        time_data = {}

        for instance in data:
            day_data, clock_data = instance["ts"].replace("Z", "").split("T")
            if i == "year":
                year = day_data.split("-")[0]
                interval = int(year)
            elif i == "month":
                month = day_data.split("-")[1]
                interval = int(month)
            elif i == "hour":
                interval = int(clock_data.split(":")[0])

            seconds = instance["ms_played"] / 1000

            if interval not in time_data:
                time_data[interval] = {"Podcast": 0, "Music": 0}


            if instance["master_metadata_track_name"] == None:
                type = "Podcast"
            else:
                type = "Music"

            time_data[interval][type] += seconds

        for i in time_data:
            time_data[i]["Music"] = time_data[i]["Music"] // 3600
            time_data[i]["Podcast"] = time_data[i]["Podcast"] // 3600

        time_data = OrderedDict(sorted(time_data.items()))

        ret.append(time_data)

    return ret

def create_artist_spreadsheet(artist_data):


    artists_header = ["Artist", "Time Listened (min)"]

    with open("Artists.csv", "w", encoding="utf-16", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(artists_header)

        for i in artist_data:
            writer.writerow([i, artist_data[i]["minutes_played"]])
    
    file.close()






def main():

    data = gather_data(path)

    artist_data = get_artist_data(data)
    track_data = get_track_data(data)

    create_artist_spreadsheet(artist_data)

main()






