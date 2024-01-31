import PySimpleGUI as sg
import time
from game_data import game_data

def update_scoreboard(window):
    window["-SCOREBOARD-"].update(f"{gd.game_data['period']} per - {gd.game_data['timeRemaining']} remaining")

    window["-AWAY NAME-"].update(f"{gd.game_data['awayTeamName']['long']}")
    window["-AWAY SCORE-"].update(f"Goals: {gd.game_data['awayScore']}")
    window["-AWAY SHOTS-"].update(f"Shots: {gd.game_data['awayShots']}")
    window["-AWAY ON ICE-"].update(gd.game_data['awayOnIce'])

    window["-HOME NAME-"].update(f"{gd.game_data['homeTeamName']['long']}")
    window["-HOME SCORE-"].update(f"Goals: {gd.game_data['homeScore']}")
    window["-HOME SHOTS-"].update(f"Shots: {gd.game_data['homeShots']}")
    window["-HOME ON ICE-"].update(gd.game_data['homeOnIce'])

font = ('Courier New', 11)
gd = game_data()

games = []
max_len = 0
for game in gd.games:
    games.append(f"{game['awayTeamName']['long']} @ {game['homeTeamName']['long']} at {game['startTime']}")
    if len(games[-1]) > max_len:
        max_len = len(games[-1])

game_list_column = [
    [
        sg.Listbox(
            values=games, enable_events=True, size=(max_len, len(games)), expand_x=True, key="-GAME LIST-"
        )
    ],
]

scoreboard_viewer_column = [
    [sg.Text("Choose a game from list on left:", size=(40, 1), key="-SCOREBOARD-")],
]

scoreboard_away_column = [
    [sg.Text(size=(30, 1), key="-AWAY NAME-")],
    [sg.Text(size=(30, 1), key="-AWAY SCORE-")],
    [sg.Text(size=(30, 2), key="-AWAY SHOTS-")],
    [sg.Text("On the Ice", size=(30, 1))],
    [sg.Listbox(values=[], enable_events=True, size=(30, 10), key="-AWAY ON ICE-")],
]

scoreboard_home_column = [
    [sg.Text(size=(30, 1), key="-HOME NAME-")],
    [sg.Text(size=(30, 1), key="-HOME SCORE-")],
    [sg.Text(size=(30, 2), key="-HOME SHOTS-")],
    [sg.Text("On the Ice", size=(30, 1))],
    [sg.Listbox(values=[], enable_events=True, size=(30, 10), key="-HOME ON ICE-")],
]

roster_away_column = [
    [sg.Listbox(values=[], enable_events=True, size=(30, 10), key="-AWAY ROSTER-")],
]

roster_home_column = [
    [sg.Listbox(values=[], enable_events=True, size=(30, 10), key="-HOME ROSTER-")],
]

live_stats_column = [
    [sg.Table(values=[], headings=['Player', ' G ', ' A ', 'SOG', 'FO '], auto_size_columns=False, def_col_width=8, justification='center', key='-LIVE STATS-')],
]

stats_column = [
    [sg.Text(size=(30, 1), key="-STAT NAME-")],
    [sg.Table(values=[], headings=['Date', 'Opp', ' G ', ' A ', 'SOG'], auto_size_columns=False, def_col_width=8, justification='center', key='-STATS-')],
]

# ----- Make the frames -----
frame_game_list = sg.Frame("Today's Games", game_list_column, title_location=sg.TITLE_LOCATION_TOP)
frame_selected_game = sg.Frame("", scoreboard_viewer_column, border_width=0)
frame_scoreboard_away = sg.Frame("Away", scoreboard_away_column, title_location=sg.TITLE_LOCATION_TOP)
frame_scoreboard_home = sg.Frame("Home", scoreboard_home_column, title_location=sg.TITLE_LOCATION_TOP)
frame_roster_away = sg.Frame("Away Roster", roster_away_column, title_location=sg.TITLE_LOCATION_TOP, visible=False, key="-AWAY ROSTER FRAME-")
frame_roster_home = sg.Frame("Home Roster", roster_home_column, title_location=sg.TITLE_LOCATION_TOP, visible=False, key="-HOME ROSTER FRAME-")
frame_live_stats = sg.Frame("Live Stats", live_stats_column, title_location=sg.TITLE_LOCATION_TOP, visible=False, key="-LIVE STATS FRAME-")
frame_stats = sg.Frame("Stats", stats_column, title_location=sg.TITLE_LOCATION_TOP, visible=False, key="-STATS FRAME-")

# ----- Full layout -----
layout_column1 = [
    [
        frame_game_list,
    ],
    [
        frame_roster_away,
        frame_roster_home,
    ]
]

layout_column2 = [
    [frame_selected_game],
    [
        frame_scoreboard_away,
        frame_scoreboard_home,
    ],
]

layout_column3 = [
    [frame_live_stats],
    [frame_stats],
]
    
layout = [
    [sg.Frame("", layout_column1),
     sg.Frame("Scoreboard", layout_column2, title_location=sg.TITLE_LOCATION_TOP),
     sg.Frame("Additional Information", layout_column3),],
]

window = sg.Window("NHL Scoreboard", layout)

# timer = round(time.time())
update_interval = 5 # update every x seconds
# Run the Event Loop
while True:
    event, values = window.read(timeout=1000)
    if event == "Exit" or event == sg.WIN_CLOSED:
        break

    if event == "-GAME LIST-":
        # Get live data from selected game
        for game in gd.games:
            if game['awayTeamName']['long'] == values["-GAME LIST-"][0].split(" @ ")[0]:
                gd.selected_game = game
                gd.get_live_game_data(game)
        
        # Update scoreboard
        update_scoreboard(window)
        window["-AWAY ROSTER FRAME-"].update(visible=True)
        window["-HOME ROSTER FRAME-"].update(visible=True)

        # Add rosters to screen
        away_roster_list = []
        for player in gd.game_data['awayRoster']:
            away_roster_list.append(gd.game_data['awayRoster'][player]['combinedInfo'])

        home_roster_list = []
        for player in gd.game_data['homeRoster']:
            home_roster_list.append(gd.game_data['homeRoster'][player]['combinedInfo'])
        
        window["-AWAY ROSTER-"].update(away_roster_list)
        window["-HOME ROSTER-"].update(home_roster_list)
    
    if event == "-AWAY ROSTER-" or event == "-HOME ROSTER-" or event == "-AWAY ON ICE-" or event == "-HOME ON ICE-":
        live_stats_headings = []
        live_stats = []
        stats_headings = []
        stats = []
        name = ""
        if event == "-AWAY ROSTER-" or event == "-AWAY ON ICE-":
            for player in gd.game_data['awayRoster']:
                if gd.game_data['awayRoster'][player]['combinedInfo'] == values[event][0]: # If this is the player selected
                    if gd.game_data['awayRoster'][player]['position'] == 'G':
                        # stats_headings, stats = gd.player_stats.get_goalie_stats(player=gd.game_data['awayRoster'][player]['name'])
                        name = "No stats available for goalies"
                        continue

                    else:
                        live_stats = gd.get_live_stats(gd.game_data['awayRoster'][player], True) ##########################
                        stats_headings, stats = gd.player_stats.get_player_stats(player=gd.game_data['awayRoster'][player]['name'])
                        name = gd.game_data['awayRoster'][player]['name']
        
        if event == "-HOME ROSTER-" or event == "-HOME ON ICE-":
            for player in gd.game_data['homeRoster']:
                if gd.game_data['homeRoster'][player]['combinedInfo'] == values[event][0]: # If this is the player selected
                    if gd.game_data['homeRoster'][player]['position'] == 'G':
                        # stats_headings, stats = gd.player_stats.get_goalie_stats(player=gd.game_data['homeRoster'][player]['name'])
                        name = "No stats available for goalies"
                        continue

                    else:
                        live_stats = gd.get_live_stats(gd.game_data['homeRoster'][player], False)
                        stats_headings, stats = gd.player_stats.get_player_stats(player=gd.game_data['homeRoster'][player]['name'])
                        name = gd.game_data['homeRoster'][player]['name']
        
        window["-STAT NAME-"].update(value=name)
        # print(f"Stats: {stats}")
        window["-STATS-"].update(values=stats)
        window["-STATS FRAME-"].update(visible=True)
        
        # print(f"Live stats: {live_stats}")
        if live_stats != []:
            window["-LIVE STATS-"].update(values=live_stats)
            window["-LIVE STATS FRAME-"].update(visible=True)
    
    # Live update
    if round(time.time()) % update_interval == 0 and gd.selected_game != {}:
        # print("Updating...")
        gd.get_live_game_data(gd.selected_game)
        # Update scoreboard
        update_scoreboard(window)
        
window.close()