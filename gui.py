import PySimpleGUI as sg
from game_data import game_data
from PIL import Image
from io import BytesIO
import json
import time as time

with open('player2id.json', 'r') as file:
    player2id = json.load(file)

# Auston Matthews GLAZERSSS

font = ('Courier New', 11)
gd = game_data()
teams = []
players = []
team_rosters = {}
parlays = {}
parlays = {'Chicago Blackhawks @ Winnipeg Jets at 08:00 PM': [['Connor Bedard', 'Shots', '4'], ['Alex Vlasic', 'Shots', '1']],
           'Philadelphia Flyers @ Vancouver Canucks at 10:00 PM': [['Travis Konecny', 'Shots', '2'], ['Brock Boeser', 'Shots', '2'], ['J.T. Miller', 'Shots', '2'], ['Owen Tippett', 'Shots', '3']]}


print('Collecting Data...')
for game in gd.get_schedule():
    teams.append([game['awayTeamName']['short'], game['awayTeamName']['long']])
    teams.append([game['homeTeamName']['short'], game['homeTeamName']['long']])
    team_rosters[game['awayTeamName']['long']] = []
    team_rosters[game['homeTeamName']['long']] = []
for team in teams:
    team_rosters[team[1]] += gd.get_team_roster(teamAbb=team[0])

def resize_image(image_path, scale=None, new_width=None, new_height=None):
    image = Image.open(image_path)
    w, h = [image.width, image.height]
    if scale:
        new_width = int(w * scale)
        new_height = int(h * scale)
        image = image.resize((new_width, new_height), Image.LANCZOS)
    elif new_width and new_height:
        image = image.resize((new_width, new_height), Image.LANCZOS)
    bio = BytesIO()
    image.save(bio, format="PNG")  # Save it as PNG in memory
    return bio.getvalue()
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

def choose_game_window():
    layout = [
        [sg.Text("Choose a game from the list:")],
        [sg.Listbox(values=games, enable_events=True, size=(max_len, len(games)), key="-GAME LIST-")],
        [sg.Button("Close")]
    ]
    window = sg.Window("Choose Game", layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == "Close":
            window.close()
            break
        elif event == "-GAME LIST-":
            game = values["-GAME LIST-"][0]
            window.close()
            return game

    return None


def open_tracker_window():
    if len(parlays) == 0:
        sg.popup("No parlays to track.")
        return
    else:
        parlayCombo = []
        # Creating a displayable format for each parlay
        for key in parlays:
            tempList = []
            for leg in parlays[key]:
                tempList.append(f"{leg[0]} {leg[2]}+ {leg[1]}")
            parlayCombo.append(f"{', '.join(tempList)}")

        # Ask which parlay you would like to track
        layout = [
            [sg.Combo(parlayCombo, key="-PARLAY CHOICE-", enable_events=True)],
            [sg.Table(values=[], headings=['Player', ' G ', ' A ', 'SOG', 'FO '], auto_size_columns=False,
                      def_col_width=8, justification='center', key='-LIVE STATS-', visible=False)],
            [sg.Button("Submit"), sg.Button("Close")]
        ]
        window = sg.Window("Track Parlay", layout)

        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == "Close":
                window.close()
                break
            elif event == "Submit":
                window.close()
                break
            elif event == "-PARLAY CHOICE-":
                # Get the selected parlay
                parlay = values["-PARLAY CHOICE-"]
                selected_parlay = None
                for key in parlays:
                    temp_parlay = []
                    for leg in parlays[key]:
                        temp_parlay.append(f"{leg[0]} {leg[2]}+ {leg[1]}")
                    if parlay == f"{', '.join(temp_parlay)}":
                        selected_parlay = parlays[key]
                        game = key
                        break

                if selected_parlay:
                    window['-LIVE STATS-'].update(visible=True)

                    # Find the game being tracked
                    for game_info in gd.get_schedule():
                        if game_info['awayTeamName']['long'] in game or game_info['homeTeamName']['long'] in game:
                            gd.selected_game = game_info
                            gd.get_live_game_data(game_info)

                            # Check if the selected team is the away or home team
                            is_away = gd.game_data['awayTeamName']['long'] in game
                            is_home = gd.game_data['homeTeamName']['long'] in game

                            # Get the respective rosters
                            away_roster = gd.game_data['awayRoster']
                            home_roster = gd.game_data['homeRoster']

                            # List to store live stats
                            live_stats_data = []

                            # Fetch live stats for each player in the parlay
                            for leg in selected_parlay:
                                player_name = leg[0]  # Player name from parlay

                                # Search the player in the away roster first
                                player_data = None
                                for player_id, player_info in away_roster.items():
                                    if player_info['name'] == player_name:
                                        player_data = player_info
                                        is_away = True
                                        break

                                # If player not found in away roster, search in home roster
                                if not player_data:
                                    for player_id, player_info in home_roster.items():
                                        if player_info['name'] == player_name:
                                            player_data = player_info
                                            is_away = False
                                            break

                                # Fetch live stats if the player is found
                                if player_data:
                                    live_stats = gd.get_live_stats(player_data, is_away)
                                    if live_stats:
                                        # Append the live stats to the data list
                                        live_stats_data.append(live_stats[0])
                                    else:
                                        live_stats_data.append(
                                            [player_name, 'No data', 'No data', 'No data', 'No data'])

                            # Update the table with the fetched live stats
                            if live_stats_data:
                                window['-LIVE STATS-'].update(values=live_stats_data)

                            break


def open_parlay_window():
    chosenGame = choose_game_window()
    chosenTeams = [chosenGame.split(" @ ")[0], chosenGame.split(" @ ")[1].split(" at ")[0]]
    chosenPlayers = team_rosters[chosenTeams[0]] + team_rosters[chosenTeams[1]]

    stats = ["Goals", "Assists", "Shots"]
    numbers = [str(i) for i in range(1, 10)]

    rows = []
    for i in range(10):  # Predefine the max number of legs

        # Create a single row with image, player combo, stat combo, and number combo
        row = [
            sg.Image(data=None, key=f"-Image-{i}-", visible=False, size=(35, 35)),  # Image
            sg.Combo(chosenPlayers, key=f"-Player-{i}-", visible=False, enable_events=True),  # Player Combo
            sg.Combo(stats, key=f"-Stat-{i}-", visible=False),  # Stat Combo
            sg.Combo(numbers, key=f"-Number-{i}-", visible=False)  # Number Combo
        ]

        rows.append(row)  # Add the row to the list

    title_row = [
        sg.Text("Image", justification="center", key="-ImageTitle-", visible=False),
        sg.Text("Player", justification="center", key="-PlayerTitle-", visible=False, pad=((115, 0), (0, 0))),
        sg.Text("Stat", justification="center", key="-StatTitle-", visible=False, pad=((83, 0), (0, 0))),
        sg.Text("Number", justification="center", key="-NumberTitle-", visible=False, pad=((23, 0), (0, 0)))
    ]

    parlay_layout = [
        [sg.Text("Number of Legs:"), sg.Combo([str(i) for i in range(1, 11)], key="-numLegs-", enable_events=True)],
        title_row,  # Add title row before rows
        *rows,  # Spread operator to add the rows dynamically
        [sg.Button("Add Parlay", visible=False), sg.Button("Close", visible=False)]
    ]
    parlay_window = sg.Window("Create Parlay", parlay_layout)

    parlay_list = []


    while True:
        event, values = parlay_window.read()
        if event == sg.WIN_CLOSED or event == "Close":
            parlay_window.close()
            break
        elif event == "-numLegs-":
            num_legs = int(values["-numLegs-"])
            # Show rows based on the number of legs selected
            parlay_window["-PlayerTitle-"].update(visible=(num_legs > 0))
            parlay_window["-StatTitle-"].update(visible=(num_legs > 0))
            parlay_window["-NumberTitle-"].update(visible=(num_legs > 0))
            parlay_window["Add Parlay"].update(visible=True)
            parlay_window["Close"].update(visible=True)
            for i in range(10):
                # parlay_window[f"-Image-{i}-"].update(visible=(i < num_legs))
                parlay_window[f"-Image-{i}-"].update(data=None, visible=(i < num_legs))
                parlay_window[f"-Player-{i}-"].update(visible=(i < num_legs))
                parlay_window[f"-Stat-{i}-"].update(visible=(i < num_legs))
                parlay_window[f"-Number-{i}-"].update(visible=(i < num_legs))
        elif "-Player-" in event:
            # Find out which player combo was selected
            player_index = int(event.split("-")[2])
            selected_player = values[f"-Player-{player_index}-"]
            if selected_player:

                image_path = f"C:/_Repos/NHL_Stats/Headshots/{player2id[selected_player]}.png"
                resized_image_data = resize_image(image_path, new_width=35, new_height=35)

                # Make the corresponding image visible and update it
                parlay_window[f"-Image-{player_index}-"].update(data=resized_image_data)

        elif event == "Add Parlay":
            VALID = True
            popup_str = ''
            num_legs = int(values["-numLegs-"])
            for i in range(num_legs):
                # Retrieve values for each leg
                player = values[f"-Player-{i}-"]
                stat = values[f"-Stat-{i}-"]
                number = values[f"-Number-{i}-"]

                # Create the leg and add it to the parlay list
                leg = [player, stat, number]
                if "" in leg:
                    VALID = False
                parlay_list.append(leg)
                if i == num_legs - 1:
                    popup_str += f"{player} {number}+ {stat}"
                else:
                    popup_str += f"{player} {number}+ {stat}\n"

            if VALID:
                parlays[chosenGame] = parlay_list
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
    [frame_live_stats,
    frame_stats],
]

layout = [
    [sg.Button("Create Parlay"), sg.Push(), sg.Image(data=resize_image(r"C:\_Repos\NHL_Stats\MiscellaneousPictures\bet365.png", scale=0.2))],
    [sg.Button("Track Parlay")],
    [sg.Frame("", layout_column1),
     sg.Frame("Scoreboard", layout_column2, title_location=sg.TITLE_LOCATION_TOP)],
    [sg.Frame("Additional Information", layout_column3)]
]

window = sg.Window("NHL Scoreboard", layout)

# Update every x seconds
update_interval = 5

# Run the Event Loop
while True:
    event, values = window.read(timeout=1000)
    if event == "Exit" or event == sg.WIN_CLOSED:
        break

    if event == "Create Parlay":
        open_parlay_window()

    if event == "Track Parlay":
        open_tracker_window()

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
                if gd.game_data['awayRoster'][player]['combinedInfo'] == values[event][0]:  # If this is the player selected
                    if gd.game_data['awayRoster'][player]['position'] == 'G':
                        # stats_headings, stats = gd.player_stats.get_goalie_stats(player=gd.game_data['awayRoster'][player]['name'])
                        name = "No stats available for goalies"
                        continue

                    else:
                        live_stats = gd.get_live_stats(gd.game_data['awayRoster'][player],True)  ##########################
                        stats_headings, stats = gd.player_stats.get_player_stats(
                            player=gd.game_data['awayRoster'][player]['name'])
                        name = gd.game_data['awayRoster'][player]['name']

        if event == "-HOME ROSTER-" or event == "-HOME ON ICE-":
            for player in gd.game_data['homeRoster']:
                if gd.game_data['homeRoster'][player]['combinedInfo'] == values[event][
                    0]:  # If this is the player selected
                    if gd.game_data['homeRoster'][player]['position'] == 'G':
                        # stats_headings, stats = gd.player_stats.get_goalie_stats(player=gd.game_data['homeRoster'][player]['name'])
                        name = "No stats available for goalies"
                        continue

                    else:
                        live_stats = gd.get_live_stats(gd.game_data['homeRoster'][player], False)
                        stats_headings, stats = gd.player_stats.get_player_stats(
                            player=gd.game_data['homeRoster'][player]['name'])
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