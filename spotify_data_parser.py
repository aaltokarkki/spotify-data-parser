import orjson
import csv
from openpyxl import Workbook
from datetime import datetime
import matplotlib.pyplot as plt
from collections import OrderedDict


def main():
    json = []
    data_list = []

    file_name = input("Enter the name of the json file (.json included)\n")
    json.append(file_name)
    while json[-1] != "":
        file_name = input("Input the name of the next json file if left. Otherwise leave empty and press enter.\n")
        json.append(file_name)

    del json[-1]

    for i in json:
            with open(i, "rb") as f:
                data_list.append(orjson.loads(f.read()))





    songs = {}
    artists = {}

    for data in data_list:
        for i in data:
            track = i["master_metadata_track_name"]
            if track == None:
                continue
            if track in songs:
                songs[track]["times_played"] += 1
                songs[track]["seconds_played"] += i["ms_played"] // 1000
            else:
                songs[track] = {"times_played": 1, "seconds_played": i["ms_played"] // 1000}

    for data in data_list:
        for i in data:
            artist = i["master_metadata_album_artist_name"]
            if artist == None:
                continue
            if artist in artists:
                artists[artist]["seconds_played"] += i["ms_played"] // 1000
            else:
                artists[artist] = {"seconds_played": i["ms_played"] // 1000}


    songs = sorted(songs.items(), key=lambda x: x[1]["times_played"], reverse=True)

    songs_list = []

    for i in songs:
        if i[1]["times_played"] > 1:
            songs_list.append([i[0], i[1]["times_played"], i[1]["seconds_played"] // 60])
        #print("{:s}: {:d} ({:d}min)".format(i[0], i[1]["times_played"], i[1]["seconds_played"] // 60))

    tracks_header = ["Track", "Times Played", "Time Listened (min)"]

    with open("Tracks.csv", "w", encoding="utf-16", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(tracks_header)

        writer.writerows(songs_list)

    file.close()

    wb = Workbook()
    ws = wb.active
    ws.append(["Track", "Times Played", "Time Listened (min)"])
    for i in songs:
        if i[1]["times_played"] > 1:
            ws.append([i[0], i[1]["times_played"], i[1]["seconds_played"] // 60])
    wb.save('Tracks.xlsx')





    artists = sorted(artists.items(), key=lambda x: x[1]["seconds_played"], reverse=True)

    artists_list = []

    for i in artists:
        if i[1]["seconds_played"] > 60:
            artists_list.append([i[0], i[1]["seconds_played"] // 60])
        #print("{:s}: {:d}min".format(i[0],i[1]["seconds_played"] // 60))

    artists_header = ["Artist", "Time Listened (min)"]

    with open("Artists.csv", "w", encoding="utf-16", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(artists_header)

        writer.writerows(artists_list)

    file.close()

    wb = Workbook()
    ws = wb.active
    ws.append(["Artist", "Time Listened (min)"])
    for i in artists:
        if i[1]["seconds_played"] > 60:
            ws.append([i[0], i[1]["seconds_played"] // 60])
    wb.save('Artists.xlsx')



    weekdays = {"Mon": 0, "Tue": 0, "Wed": 0, "Thu": 0, "Fri": 0, "Sat": 0, "Sun": 0}

    years = {}
    months = {}
    days = {}
    hours = {}

    time_d = [years, months, days, hours]

    for data in data_list:
        for i in data:
            duration = i["ms_played"] / 1000
            day_data, time_data = i["ts"].replace("Z", "").split("T")
            hour = int(time_data.split(":")[0])
            year, month, day = day_data.split("-")
            year = int(year)
            month = int(month)
            day = int(day)
            time = [year, month, day, hour]
            weekday = datetime(year, month, day).weekday()

            for i in range(len(time)):
                if time[i] == None:
                    continue
                if time[i] in time_d[i]:
                    time_d[i][time[i]] += duration
                else:
                    time_d[i][time[i]] = duration


            if weekday == 0:
                    weekdays["Mon"] += duration
            elif weekday == 1:
                    weekdays["Tue"] += duration
            elif weekday == 2:
                    weekdays["Wed"] += duration
            elif weekday == 3:
                    weekdays["Thu"] += duration
            elif weekday == 4:
                    weekdays["Fri"] += duration
            elif weekday == 5:
                    weekdays["Sat"] += duration
            elif weekday == 6:
                    weekdays["Sun"] += duration


    for i in weekdays:
        weekdays[i] = weekdays[i] // 3600
    plt.bar(range(len(weekdays)), list(weekdays.values()), tick_label=list(weekdays.keys()))
    plt.title("Listening Time over Weekdays (h)")
    plt.savefig('Weekdays.png')
    plt.close()

    for i in years:
        years[i] = years[i] // 3600
    years = OrderedDict(sorted(years.items()))
    plt.bar(range(len(years)), list(years.values()), tick_label=list(years.keys()))
    plt.title("Listening Time over Years (h)")
    plt.savefig('Years.png')
    plt.close()

    for i in months:
        months[i] = months[i] // 3600
    months = OrderedDict(sorted(months.items()))
    plt.bar(range(len(months)), list(months.values()), tick_label=list(months.keys()))
    plt.title("Listening Time over Months (h)")
    plt.savefig('Months.png')
    plt.close()

    #days = OrderedDict(sorted(days.items()))
    #plt.bar(range(len(days)), list(days.values()), tick_label=list(days.keys()))
    #plt.savefig('Days.png')
    #plt.close()

    for i in hours:
        hours[i] = hours[i] // 3600
    hours = OrderedDict(sorted(hours.items()))
    plt.bar(range(len(hours)), list(hours.values()), tick_label=list(hours.keys()))
    plt.title("Listening Time over Hours of the Day (h)")
    plt.savefig('Hours.png')
    plt.close()





























main()