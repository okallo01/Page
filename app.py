import sqlite3
from flask import render_template, url_for, make_response, Flask, request, json
import requests
import csv
import os
import pandas as pd


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        #go to the home page
        op = [
            "Chelsea",
            "Manchester City",
            "Liverpool",
            "West Ham United",
            "Arsenal",
            "Tottenham Hotspur",
            "Manchester United",
            "Wolverhampton Wanderers",
            "Leicester City",
            "Crystal Palace",
            "Brentford",
            "Aston Villa",
            "Everton",
            "Leeds United",
            "Southampton",
            "Watford",
            "Burnley",
            "Norwich City",
            "Newcastle United",
            "Brighton & Hove Albion"
        ]
        op.sort()
        return render_template("index.html",options=op )



#https://apiv3.apifootball.com/?action=get_teams&league_id=152&APIkey=ae37245d1c770f7cddfff8b1827ada9e866fac2469250be8a7d4b2d9597c8000
@app.route("/team", methods=["GET", "POST"])
def team():
    playersname = []
    d = []
    data = request.form.get("team_names")
    r = requests.get("https://apiv3.apifootball.com/?action=get_teams&league_id=152&APIkey=ae37245d1c770f7cddfff8b1827ada9e866fac2469250be8a7d4b2d9597c8000")
    team_data = json.loads(r.content)
    x = team_data
    for v in x:
        team_name = v["team_name"]
        if team_name == data:
            d.append(v["players"])

    for names in d:
        for e in names:
            m = e["player_name"]
            playersname.append(m)
        return render_template("playerselection.html", team=playersname)


copylist = []
@app.route("/players_info", methods=["GET", "POST"])
def players():
    profile_data = []
    players_information = []
    selected_name = request.form.get("team_players")
    r = requests.get("https://apiv3.apifootball.com/?action=get_players&player_name="+selected_name+"&APIkey=ae37245d1c770f7cddfff8b1827ada9e866fac2469250be8a7d4b2d9597c8000")
    player_data = json.loads(r.content)

    p = player_data
    for data in p:
        players_information.append(data)

    for profile in players_information:
        profile_data.append(profile)
        copylist.append(profile)
   
    #create stats table
    conn = sqlite3.connect("PlayerInformation.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS Stats (IDNumber Integer, Matches Integer, Injuries TEXT, Minutes Integer, Rating Integer)")
    check = c.execute("SELECT COUNT(*) FROM Stats")
    results = check.fetchall()
    if results[0]== (0,):
        for d in profile_data:
            ID = d["player_id"]
            Marches = d["player_match_played"]
            Injuries = d["player_injured"]
            Minutes = d["player_minutes"]
            Rating = d["player_rating"]
        stats_data = (ID,Marches,Injuries,Minutes,Rating)
        c.execute("INSERT INTO Stats VALUES (?,?,?,?,?)", stats_data)
        conn.commit()
    else:
        conn = sqlite3.connect("PlayerInformation.db")
        c = conn.cursor()
        for x in profile_data:
            ID = x["player_id"]
            Marches = x["player_match_played"]
            Injuries = x["player_injured"]
            Minutes = x["player_minutes"]
            Rating = x["player_rating"]
        stats_datas = (ID,Marches,Injuries,Minutes,Rating)
        c.execute("INSERT INTO Stats VALUES (?,?,?,?,?)", stats_datas)
        conn.commit()


    
    return render_template("playersdata.html", info=profile_data)


@app.route("/save", methods=["GET", "POST"])
def saveing_data():
    data_to_save = []
    if len(copylist) > 0:
        data_to_save = copylist[:]
        copylist.clear()

        #create the database
        conn = sqlite3.connect("PlayerInformation.db")
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS players (IDNumber Integer,Name TEXT,Position TEXT, Number Integer)")
        for data in data_to_save:
            Id_col = data["player_id"]
            name_col = data["player_name"]
            position_col = data["player_type"]
            number_col = data["player_number"]


            #insert item into the table
            param = (Id_col, name_col, position_col, number_col)
    
            c.execute("INSERT INTO players VALUES (?,?,?,?)", param)
            conn.commit()
        
    success_message = "Data save successfully "
    
    return render_template("playersdata.html", s=success_message)

@app.route("/dbdata" ,methods=["GET", "POST"])
def saved_data():
    saved = []
    #get the saved data from database
    conn = sqlite3.connect("PlayerInformation.db")
    c = conn.cursor()
    data = c.execute("SELECT players.IDNumber, players.Name, players.Position,players.Number, Topscorers.Place, Topscorers.Goals, Topscorers.Team, Stats.Matches, Stats.Injuries, Stats.Minutes, Stats.Rating FROM players LEFT JOIN Topscorers ON players.IDNumber= Topscorers.IDNumber LEFT JOIN Stats ON players.IDNumber= Stats.IDNumber GROUP BY players.IDNumber")
    for db_data in data.fetchall():
        saved.append(db_data)
    return render_template("savedata.html", x=saved)

@app.route("/delete", methods=["GET", "POST"])
def delete():
    #delete everything in the database
    conn = sqlite3.connect("PlayerInformation.db")
    c = conn.cursor()
    data = c.execute("DELETE FROM players")
    conn.commit()
    msg = "DATA SUCCESSFULLY DELETED!!!!!"
    return render_template("savedata.html", del_message=msg)


@app.route("/topscorers", methods=["GET", "POST"])
def topscore():
    conn = sqlite3.connect("PlayerInformation.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS Topscorers (IDNumber Integer,Name TEXT,Place Integer, Goals Integer, Team TEXT )")
    check = c.execute("SELECT COUNT(*) FROM Topscorers")
    results = check.fetchall()

    #return render_template("topscore.html", message=results[0])
    #check if the table is empty
    if results[0]== (0,):
        #c.execute("CREATE TABLE Topscorers (IDNumber Integer,Name TEXT,Place TEXT, Goals TEXT, Team TEXT )")
        full_data = []
        top_scorers = []
        r = requests.get("https://apiv3.apifootball.com/?action=get_topscorers&league_id=152&APIkey=ae37245d1c770f7cddfff8b1827ada9e866fac2469250be8a7d4b2d9597c8000")
        score_data = json.loads(r.content)
    
        for gol_scorers in score_data:
            full_data.append(gol_scorers)
        for top in full_data:
            ID = int(top["player_key"])
            Name = top["player_name"]
            place = int(top["player_place"])
            Goals = int(top["goals"])
            Team = top["team_name"]
            data = (ID,Name,place,Goals,Team)
            c.execute("INSERT INTO Topscorers VALUES (?,?,?,?,?)", data)
            conn.commit()
        x = c.execute("SELECT * FROM Topscorers GROUP BY IDNumber ORDER BY Goals DESC")
        return render_template("topscore.html", message=x)
    else:
        v = c.execute("SELECT * FROM Topscorers GROUP BY IDNumber ORDER by Goals DESC")
        return render_template("topscore.html", message=v)




