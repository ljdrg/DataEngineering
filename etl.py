import os
import glob
import psycopg2
import pandas as pd
import numpy as np
import datetime
from sql_queries import *


def process_song_file(cur, filepath):
    """This function reads in the json song file and divides the data in their respective tables songs and artists.
    It takes two input arguments:
    cur: the cursor position in the database
    filepath: the filepath where the json song files are stored"""
    # open song file
    df = pd.read_json(filepath, typ= "series")
    df = pd.DataFrame([df])

    for i, row in df.iterrows():
        # insert song record
        song_data = row[["song_id", "title", "artist_id", "year", "duration"]].values.tolist()
        song_data = [int(item) if isinstance(item, np.integer) else item for item in song_data]
        song_data = [float(item) if isinstance(item, np.floating) else item for item in song_data]
        cur.execute(song_table_insert, song_data)
        
        # insert artist record
        artist_data = row[["artist_id", "artist_name", "artist_location", "artist_latitude", "artist_longitude"]].values.tolist()
        cur.execute(artist_table_insert, artist_data)


def process_log_file(cur, filepath):
    """ This function reads in the json log file, filters the data on the NextSong action and divides the data in their respective tables time and users.
    It takes two input arguments:
    cur: the cursor position in the database
    filepath: the filepath where the json log files is stored
    """
    # open log file
    df = pd.read_json(filepath, lines= True)
    df = pd.DataFrame(df)
    

    # filter by NextSong action
    df = df.loc[df["page"] == "NextSong"]

    # convert timestamp column to datetime
    df["ts"] = df["ts"].apply(lambda x: datetime.datetime.fromtimestamp(x/1000.0))
    
    # insert time data records
    time_data = (df["ts"], df["ts"].dt.hour, df["ts"].dt.day, df["ts"].dt.isocalendar().week, df["ts"].dt.month, df["ts"].dt.year, df["ts"].dt.weekday)
    column_labels = ("timestamp" ,"hour", "day", "week", "month", "year", "weekday")

    time_df = pd.DataFrame(dict(zip(column_labels, time_data)))

    for i, row in time_df.iterrows():
        cur.execute(time_table_insert, list(row))

    # load user table
    user_df = df[["userId", "firstName", "lastName", "gender", "level"]]
    user_df = user_df.loc[~(user_df["userId"] == "")]

    # insert user records
    for i, row in user_df.iterrows():
        cur.execute(user_table_insert, row)

    # insert songplay records
    for index, row in df.iterrows():
        
        # get songid and artistid from song and artist tables
        cur.execute(song_select, (row.song, row.artist, row.length))
        results = cur.fetchone()
        
        if results:
            songid, artistid = results
        else:
            songid, artistid = None, None

        # insert songplay record
        songplay_data =(row.ts, row.userId, row.level, songid, artistid, row.sessionId, row.location, row.userAgent)

        cur.execute(songplay_table_insert, songplay_data)


def process_data(cur, conn, filepath, func):
    """ This function takes a function and filepath. Important: the input function must match the data in the filepath.
    cur: cursor position in the database
    conn: the connection of the current session to the database
    filepath: location of the data you want to process
    func: respective function to the data in the filepath
    """
    # get all files matching extension from directory
    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root,'*.json'))
        for f in files :
            all_files.append(os.path.abspath(f))

    # get total number of files found
    num_files = len(all_files)
    print('{} files found in {}'.format(num_files, filepath))

    # iterate over files and process
    for i, datafile in enumerate(all_files, 1):
        func(cur, datafile)
        conn.commit()
        print('{}/{} files processed.'.format(i, num_files))


def main():
    """This function executes the data processing steps when the script is called as a main programm."""
    conn = psycopg2.connect("host=127.0.0.1 dbname=sparkifydb user=leonie password=nanodegree")
    cur = conn.cursor()

    process_data(cur, conn, filepath='data/song_data', func=process_song_file)
    process_data(cur, conn, filepath='data/log_data', func=process_log_file)

    conn.close()


if __name__ == "__main__":
    main()