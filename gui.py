import PySimpleGUI as sg
from game_data import game_data

# Auston Matthews GLAZERSSS

gd = game_data()
teams = []
players = []
print('Collecting Data...')
for game in gd.get_schedule():
    teams.append(game['awayTeamName']['short'])
    teams.append(game['homeTeamName']['short'])
for team in teams:
    players += gd.get_team_roster(teamAbb=team)

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


def add_parlay_leg(parlay_list, leg):
    parlay_list.append(leg)
    return parlay_list


def open_parlay_window():
    stats = ["Goals", "Assists", "Shots"]
    numbers = [str(i) for i in range(1, 10)]

    player_columns, stat_columns, number_columns = [], [], []

    for i in range(10):  # Predefine the max number of legs
        player_columns.append(
            [sg.Combo(players, key=f"-Player-{i}-", visible=False)]
        )
        stat_columns.append(
            [sg.Combo(stats, key=f"-Stat-{i}-", visible=False)]
        )
        number_columns.append(
            [sg.Combo(numbers, key=f"-Number-{i}-", visible=False)]
        )

    title_row = [
        sg.Text("Player", justification="center", key="-PlayerTitle-", visible=False),
        sg.Text("Stat", justification="center", key="-StatTitle-", visible=False),
        sg.Text("Number", justification="center", key="-NumberTitle-", visible=False)
    ]

    # The dropdown rows
    dropdown_rows = [
        sg.Column([[title_row[0]]] + player_columns, key='-PlayerColumn-', element_justification="center"),
        sg.Column([[title_row[1]]] + stat_columns, key='-StatColumn-', element_justification="center"),
        sg.Column([[title_row[2]]] + number_columns, key='-NumberColumn-', element_justification="center")
    ]

    parlay_layout = [
        [sg.Text("Number of Legs:"), sg.Combo([str(i) for i in range(1, 11)], key="-numLegs-", enable_events=True)],
        dropdown_rows,
        [sg.Button("Add Parlay"), sg.Button("Close")]
    ]
    parlay_window = sg.Window("Create Parlay", parlay_layout)

    parlay_list = []
    while True:
        event, values = parlay_window.read()
        if event == sg.WIN_CLOSED or event == "Close":
            break
        elif event == "-numLegs-":
            num_legs = int(values["-numLegs-"])
            # Show rows based on the number of legs selected
            parlay_window["-PlayerTitle-"].update(visible=(num_legs > 0))
            parlay_window["-StatTitle-"].update(visible=(num_legs > 0))
            parlay_window["-NumberTitle-"].update(visible=(num_legs > 0))
            for i in range(10):
                parlay_window[f"-Player-{i}-"].update(visible=(i < num_legs))
                parlay_window[f"-Stat-{i}-"].update(visible=(i < num_legs))
                parlay_window[f"-Number-{i}-"].update(visible=(i < num_legs))
        elif event == "Add Parlay":
            popup_str = ''
            num_legs = int(values["-numLegs-"])
            for i in range(num_legs):
                # Retrieve values for each leg
                player = values[f"-Player-{i}-"]
                stat = values[f"-Stat-{i}-"]
                number = values[f"-Number-{i}-"]

                # Create the leg and add it to the parlay list
                leg = [player, stat, number]
                parlay_list = add_parlay_leg(parlay_list, leg)
                if i == num_legs - 1:
                    popup_str += f"{player} {number}+ {stat}"
                else:
                    popup_str += f"{player} {number}+ {stat}\n"

            sg.popup(f"Added parlay:\n{popup_str}")

            parlay_window.close()


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
    [sg.Button("Create Parlay")],
    [sg.Frame("", layout_column1),
     sg.Frame("Scoreboard", layout_column2, title_location=sg.TITLE_LOCATION_TOP)],
]

window = sg.Window("NHL Scoreboard", layout)

# Run the Event Loop
while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break

    if event == "Create Parlay":
        open_parlay_window()

    if event == "-GAME LIST-":
        # Get live data from selected game
        for game in gd.games:
            if game['awayTeamName']['long'] == values["-GAME LIST-"][0].split(" @ ")[0]:
                gd.get_live_game_data(game)

        # Update scoreboard
        update_scoreboard(window)

window.close()