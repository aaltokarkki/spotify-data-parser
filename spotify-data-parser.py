import json
import csv
from openpyxl import Workbook
from datetime import datetime
import matplotlib.pyplot as plt
from collections import OrderedDict

#Insert here the path to the folder containing the json files provided by Spotify. Use / as path separator.
raw_data_path = r"path_here"

#Insert here the path to the folder you want the parsed data to be stored in. Use / as path separator.
analytics_path = r"path_here"

#And specify whether you want to include podcast data in the plots (1 = yes, 0 = no).
include_podcasts = 1

#Give the number of rows you want in your top lists (0 for all).
top_items = 100


#Goes over all the json files in the given folder.
#Returns them as a list of dictionaries one dictionary being one listen.
def gather_data(path):

    data = []

    i = 0
    while True:
        try:
            with open(path+"/endsong_{:d}.json".format(i), "rb") as f:
                data.extend(json.loads(f.read()))
            i += 1
        except:
            break

    return data


#Takes the data and extracts artist data from it.
#Returns a sorted dictionary with listening times for every artist.
def get_artist_data(data):

    artist_data = {}

    for instance in data:
        if instance["ms_played"] < 30000:
            continue
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


#Takes the data and extracts track data from it.
#Returns a sorted dictionary with listening durations and times played for every track.
def get_track_data(data):

    track_data = {}

    for instance in data:
        if instance["ms_played"] < 30000:
            continue
        track_name = instance["master_metadata_track_name"]
        artist_name = instance["master_metadata_album_artist_name"]
        seconds = instance["ms_played"] / 1000

        if track_name != None:
            if track_name not in track_data:
                track_data[track_name] = {"seconds_played": seconds,
                                          "times_played": 1,
                                          "Artist": instance["master_metadata_album_artist_name"]}
            elif track_name in track_data:
                if artist_name == track_data[track_name]["Artist"]:
                    track_data[track_name]["seconds_played"] += seconds
                    track_data[track_name]["times_played"] += 1
                else:
                    track_data[track_name+" ({:s})".format(artist_name)] = {"seconds_played": seconds,
                                              "times_played": 1,
                                              "Artist": instance["master_metadata_album_artist_name"]}

            else:
                print("Error occurred in getting artist data.")
                return None

    track_data = dict(sorted(track_data.items(), key=lambda x: x[1]["times_played"], reverse=True))

    for i in list(track_data.keys()):
        if track_data[i]["seconds_played"] < 60:
            del track_data[i]

    for i in track_data:
        track_data[i]["minutes_played"] = track_data[i].pop("seconds_played")
        track_data[i]["minutes_played"] = track_data[i]["minutes_played"] // 60

    return track_data


#Divides the data by different days of the week.
#Returns a dictionary with listening times by days of the week for both podcasts and music.
def get_weekday_data(data):

    weekdays_data = {"Mon": {"Podcast": 0, "Music": 0}, "Tue": {"Podcast": 0, "Music": 0}, "Wed": {"Podcast": 0, "Music": 0}, "Thu": {"Podcast": 0, "Music": 0}, "Fri": {"Podcast": 0, "Music": 0}, "Sat": {"Podcast": 0, "Music": 0}, "Sun": {"Podcast": 0, "Music": 0}}

    for instance in data:
        if instance["ms_played"] < 30000:
            continue
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


#Divides the data by years, months and hours of the day.
#Returns a dictionary for each with listening times for both podcasts and music.
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


#Creates and saves csv and xlsx files of the artist data
def create_artist_spreadsheet(artist_data, top_items):

    artist_header = ["Artist", "Time Listened (min)"]

    if top_items == 0:
        top_items = float("inf")

    count = 0

    with open(analytics_path+"/Artists.csv", "w", encoding="utf-16", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(artist_header)

        for i in artist_data:
            if count < top_items and i:
                writer.writerow([i, artist_data[i]["minutes_played"]])
                count += 1
            else:
                break

    file.close()

    count = 0

    wb = Workbook()
    ws = wb.active
    ws.append(artist_header)
    for i in artist_data:
        if count < top_items and i:
            ws.append([i, artist_data[i]["minutes_played"]])
            count += 1
        else:
            break
    wb.save(analytics_path+'/Artists.xlsx')

    wb.close()


#Creates and saves csv and xlsx files of the track data
def create_track_spreadsheet(track_data, top_items):

    track_header = ["Track", "Times Played", "Time Listened (min)"]

    if top_items == 0:
        top_items = float("inf")

    count = 0

    with open(analytics_path+"/Tracks.csv", "w", encoding="utf-16", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(track_header)

        for i in track_data:
            if count < top_items and i:
                writer.writerow([i, track_data[i]["times_played"], track_data[i]["minutes_played"]])
                count += 1
            else:
                break

    count = 0

    file.close()

    wb = Workbook()
    ws = wb.active
    ws.append(track_header)
    for i in track_data:
        if count < top_items and i:
            ws.append([i, track_data[i]["times_played"], track_data[i]["minutes_played"]])
            count += 1
        else:
            break
    wb.save(analytics_path+'/Tracks.xlsx')

    wb.close()


#Creates and saves a barplot with listen data for each day of the week.
def plot_weekday_data(weekday_data, include_podcasts=1):

    fig, ax = plt.subplots()

    music = []
    podcast = []

    for i in weekday_data:
        music.append(weekday_data[i]["Music"])
        if include_podcasts==1:
            podcast.append(weekday_data[i]["Podcast"])

    ax.bar(list(weekday_data), height=music, label="Music", width=0.6, color="#7A7BED")
    if include_podcasts == 1:
        ax.bar(list(weekday_data), height=podcast, label="Podcast", width=0.6, bottom=music, color="#D6CAFF")
        ax.legend()

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#DDDDDD')
    ax.tick_params(bottom=False, left=False)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color='#EEEEEE')
    ax.xaxis.grid(False)

    ax.set_ylabel('Hours')
    ax.set_title('Hours Listened by Day of the Week')

    fig.savefig(analytics_path+"/Listen_Time_Week")

    plt.close(fig)


#Creates and saves barplots with listen data for years, months and hours of the day.
def plot_timed_data(timed_data, include_podcasts=1):

    for data in timed_data:

        fig, ax = plt.subplots()

        music = []
        podcast = []

        for i in data:
            music.append(data[i]["Music"])
            if include_podcasts == 1:
                podcast.append(data[i]["Podcast"])

        ax.bar(list(data), height=music, label="Music", width=0.6, color="#7A7BED")
        if include_podcasts == 1:
            ax.bar(list(data), height=podcast, label="Podcast", width=0.6, bottom=music, color="#D6CAFF")
            ax.legend()

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color('#DDDDDD')
        ax.tick_params(bottom=False, left=False)
        ax.set_axisbelow(True)
        ax.yaxis.grid(True, color='#EEEEEE')
        ax.xaxis.grid(False)
        ax.set_ylabel('Hours')
        plt.xticks(list(data))

        if data == timed_data[0]:
            ax.set_title('Hours Listened by Year')
            fig.savefig(analytics_path+"/Listen_Time_Year")
        elif data == timed_data[1]:
            ax.set_title('Hours Listened by Month')
            fig.savefig(analytics_path+"/Listen_Time_Month")
        elif data == timed_data[2]:
            ax.set_title('Hours Listened by Hour of the Day')
            fig.savefig(analytics_path+"/Listen_Time_Hour")

        plt.close(fig)


def main():

    data = gather_data(raw_data_path)

    artist_data = get_artist_data(data)
    track_data = get_track_data(data)

    create_track_spreadsheet(track_data, top_items)
    create_artist_spreadsheet(artist_data, top_items)

    timed_data = get_time_data(data)
    weekday_data = get_weekday_data(data)

    plot_weekday_data(weekday_data, include_podcasts)
    plot_timed_data(timed_data, include_podcasts)


main()
