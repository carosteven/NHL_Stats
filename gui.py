import PySimpleGUI as sg
from game_data import game_data

gd = game_data()

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
    [sg.Listbox(values=[], enable_events=False, size=(30, 10), key="-AWAY ON ICE-")],
]

scoreboard_home_column = [
    [sg.Text(size=(30, 1), key="-HOME NAME-")],
    [sg.Text(size=(30, 1), key="-HOME SCORE-")],
    [sg.Text(size=(30, 2), key="-HOME SHOTS-")],
    [sg.Text("On the Ice", size=(30, 1))],
    [sg.Listbox(values=[], enable_events=False, size=(30, 10), key="-HOME ON ICE-")],
]

# ----- Make the frames -----
frame_game_list = sg.Frame("Today's Games", game_list_column, title_location=sg.TITLE_LOCATION_TOP)
frame_selected_game = sg.Frame("", scoreboard_viewer_column, border_width=0)
frame_scoreboard_away = sg.Frame("Away", scoreboard_away_column, title_location=sg.TITLE_LOCATION_TOP)
frame_scoreboard_home = sg.Frame("Home", scoreboard_home_column, title_location=sg.TITLE_LOCATION_TOP)

# ----- Full layout -----
layout_column1 = [
    [
        frame_game_list,
    ]
]

layout_column2 = [
    [frame_selected_game],
    [
        frame_scoreboard_away,
        frame_scoreboard_home,
    ],
]
    
layout = [
    [sg.Frame("", layout_column1),
     sg.Frame("Scoreboard", layout_column2, title_location=sg.TITLE_LOCATION_TOP)],
]

window = sg.Window("NHL Scoreboard", layout)

# Run the Event Loop
while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break

    if event == "-GAME LIST-":
        # Get live data from selected game
        for game in gd.games:
            if game['awayTeamName']['long'] == values["-GAME LIST-"][0].split(" @ ")[0]:
                gd.get_live_game_data(game)
        
        # Update scoreboard
        update_scoreboard(window)
        

window.close()