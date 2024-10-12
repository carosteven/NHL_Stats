import requests
from datetime import timedelta, datetime
import player_stats as ps

"""
Reference:
https://github.com/Zmalski/NHL-API-Reference?tab=readme-ov-file#get-player-information
"""

def short_2_long_name(short_name):
        switcher = {
            "ANA": "Anaheim Ducks",
            "ARI": "Arizona Coyotes",
            "BOS": "Boston Bruins",
            "BUF": "Buffalo Sabres",
            "CAR": "Carolina Hurricanes",
            "CBJ": "Columbus Blue Jackets",
            "CGY": "Calgary Flames",
            "CHI": "Chicago Blackhawks",
            "COL": "Colorado Avalanche",
            "DAL": "Dallas Stars",
            "DET": "Detroit Red Wings",
            "EDM": "Edmonton Oilers",
            "FLA": "Florida Panthers",
            "LAK": "Los Angeles Kings",
            "MIN": "Minnesota Wild",
            "MTL": "Montreal Canadiens",
            "NJD": "New Jersey Devils",
            "NSH": "Nashville Predators",
            "NYI": "New York Islanders",
            "NYR": "New York Rangers",
            "OTT": "Ottawa Senators",
            "PHI": "Philadelphia Flyers",
            "PIT": "Pittsburgh Penguins",
            "SEA": "Seattle Kraken",
            "SJS": "San Jose Sharks",
            "STL": "St. Louis Blues",
            "TBL": "Tampa Bay Lightning",
            "TOR": "Toronto Maple Leafs",
            "UTA": "Utah Hockey Club",
            "VAN": "Vancouver Canucks",
            "VGK": "Vegas Golden Knights",
            "WPG": "Winnipeg Jets",
            "WSH": "Washington Capitals"
        }
        return switcher.get(short_name, "Invalid team name")

def day_2_index(self, day): # Can probably delete this
        switcher = {
            "Mon": 0,
            "Tue": 1,
            "Wed": 2,
            "Thu": 3,
            "Fri": 4,
            "Sat": 5,
            "Sun": 6
        }
        return switcher.get(day, "Invalid day")

class game_data:
    def __init__(self):
        self.player_stats = ps.PlayerStats()

        # Base url for all endpoints
        self.base_url = 'https://api-web.nhle.com/v1'

        # Get today's date
        self.today = datetime.today()
        self.today = self.today.strftime("%Y-%m-%d")
        # self.today = '2024-10-09'

        # Get today's games
        self.games = self.get_schedule()

        self.selected_game = {}

        # Selected game's data
        self.game_data = {}
    
    def get_schedule(self):
        schedule_endpoint = '/schedule/'
        schedule_dict = requests.get(self.base_url + schedule_endpoint + self.today).json()

        games = []
        for game in schedule_dict['gameWeek'][0]["games"]:
            gameInfo = {
                "gameId": game['id'],
                "startTime": (datetime.strptime(game['startTimeUTC'][-9:-1], '%H:%M:%S') + timedelta(hours=int(game['easternUTCOffset'].split(":")[0]))).strftime('%I:%M %p'),
                "awayTeamName": {
                    "short": game['awayTeam']['abbrev'], # logo available
                    "long": short_2_long_name(game['awayTeam']['abbrev']),
                    "Id": game['awayTeam']['id'],
                },
                # "awayTeamScore": game['awayTeam']['score'],
                "homeTeamName": {
                    "short": game['homeTeam']['abbrev'], # logo available
                    "long": short_2_long_name(game['homeTeam']['abbrev']),
                    "Id": game['homeTeam']['id'],
                },
                # "homeTeamScore": game['homeTeam']['score'],
            }
            games.append(gameInfo)

        return games
    
    def get_roster(self, roster_spots):
        for player in roster_spots:
            if player['teamId'] == self.game_data['awayTeamName']['Id']:
                self.game_data['awayRoster'][player['playerId']] = { # Headshots available
                    "name": f"{player['firstName']['default']} {player['lastName']['default']}",
                    "sweaterNumber": player['sweaterNumber'],
                    "position": player['positionCode'],
                    "playerId": player['playerId'],
                }
                playerInfo = []
                for info in ['name', 'sweaterNumber', 'position']:
                    playerInfo.append(self.game_data['awayRoster'][player['playerId']][info])
                self.game_data['awayRoster'][player['playerId']]['combinedInfo'] = f"{playerInfo[2]} #{playerInfo[1]} {playerInfo[0]}"
            
            elif player['teamId'] == self.game_data['homeTeamName']['Id']:
                self.game_data['homeRoster'][player['playerId']] = { # Headshots available
                    "name": f"{player['firstName']['default']} {player['lastName']['default']}",
                    "sweaterNumber": player['sweaterNumber'],
                    "position": player['positionCode'],
                    "playerId": player['playerId'],
                }
                playerInfo = []
                for info in ['name', 'sweaterNumber', 'position']:
                    playerInfo.append(self.game_data['homeRoster'][player['playerId']][info])
                self.game_data['homeRoster'][player['playerId']]['combinedInfo'] = f"{playerInfo[2]} #{playerInfo[1]} {playerInfo[0]}"


    def get_live_game_data(self, game_info):
        live_game_endpoint = '/gamecenter/'
        play_by_play_endpoint = '/play-by-play'
        live_game_dict = requests.get(self.base_url + live_game_endpoint + str(game_info['gameId']) + play_by_play_endpoint).json()

        self.game_data = {
            "gameId": game_info['gameId'],
            "period": 0,
            "timeRemaining": '20:00',
            "isIntermission": True,

            "awayTeamName": game_info['awayTeamName'],
            "awayScore": live_game_dict['awayTeam']['score'],
            "awayShots": 0,
            "awayRoster": {},
            "awayOnIce": [],

            "homeTeamName": game_info['homeTeamName'],
            "homeScore": live_game_dict['homeTeam']['score'],
            "homeShots": 0,
            "homeRoster": {},
            "homeOnIce": [],
        }
        
        if not live_game_dict['gameState'] == 'FUT' and not live_game_dict['gameState'] == 'PRE': # If game has started
            self.game_data["period"]= live_game_dict['displayPeriod']
            self.game_data["timeRemaining"]= live_game_dict['clock']['timeRemaining']
            self.game_data["isIntermission"]= live_game_dict['clock']['inIntermission']

            self.game_data["awayShots"]= live_game_dict['awayTeam']['sog']
            self.game_data["homeShots"]= live_game_dict['homeTeam']['sog']

        self.get_roster(live_game_dict['rosterSpots'])

        awayOnIce = []
        homeOnIce = []
        if not live_game_dict['gameState'] == 'FUT' and not live_game_dict['gameState'] == 'PRE' and live_game_dict['summary']:
            awayOnIce = live_game_dict['summary']['iceSurface']['awayTeam']['forwards'] + live_game_dict['summary']['iceSurface']['awayTeam']['defensemen']
            homeOnIce = live_game_dict['summary']['iceSurface']['homeTeam']['forwards'] + live_game_dict['summary']['iceSurface']['homeTeam']['defensemen']

        onIce = []
        for player in awayOnIce:
            onIce.append(self.game_data['awayRoster'][player['playerId']]['combinedInfo'])
        self.game_data["awayOnIce"] = onIce

        onIce = []
        for player in homeOnIce:
            onIce.append(self.game_data['homeRoster'][player['playerId']]['combinedInfo'])
        self.game_data["homeOnIce"] = onIce

        # Get score, time remaining, period, etc.
        # can get score, shots, period, time remaining from play by play --> maybe who's on the ice!!
        # this is followed by a list of all players for both teams --> get player id's
        # play by play from first to last follows, including coords of event with center ice being 0,0 --> range: x: -100 to 100, y: -42 to 42 (in feet)
        # uses team and player id's

    def get_live_stats(self, player, isAway=True):

        live_game_endpoint = '/gamecenter/'
        boxscore_endpoint = '/boxscore'
        live_game_dict = requests.get(self.base_url + live_game_endpoint + str(self.selected_game['gameId']) + boxscore_endpoint).json()
        info = []
        if live_game_dict['gameState'] == 'FUT' or live_game_dict['gameState'] == 'PRE': # If game has not started
            return info
        
        if isAway:
            for pos in ['forwards', 'defense']:
                for away_player in live_game_dict['playerByGameStats']['awayTeam'][pos]:
                    if player['playerId'] == away_player['playerId']:
                        info.append([away_player['name']['default']])
                        for stat in ['goals', 'assists', 'sog', 'faceoffWinningPctg']:
                            info[0].append(away_player[stat])
        
        else:
            for pos in ['forwards', 'defense']:
                for home_player in live_game_dict['playerByGameStats']['homeTeam'][pos]:
                    if player['playerId'] == home_player['playerId']:
                        info.append([home_player['name']['default']])
                        for stat in ['goals', 'assists', 'sog', 'faceoffWinningPctg']:
                            info[0].append(home_player[stat])

        return info

    def get_team_roster(self, teamAbb='TOR', season='20242025'):
        roster = []

        roster_endpoint = '/roster'
        team_endpoint = f'/{teamAbb}'
        season_endpoint = f'/{season}'
        url = self.base_url + roster_endpoint + team_endpoint + season_endpoint
        roster_df = requests.get(url).json()

        for row in roster_df:
            for player in roster_df[row]:
                name = player['firstName']['default'] + ' ' + player['lastName']['default']
                roster.append(name)
        return roster

#
# gd = game_data()
#
# # Fetch the schedule for today
# games_today = gd.get_schedule()
#
# # Find the game where the Chicago Blackhawks are playing
# chicago_game = None
# for game in games_today:
#     if game['awayTeamName']['long'] == 'Chicago Blackhawks' or game['homeTeamName']['long'] == 'Chicago Blackhawks':
#         chicago_game = game
#         break
#
# # Check if Chicago Blackhawks are playing today
# if chicago_game:
#     # Set the selected game
#     gd.selected_game = chicago_game
#
#     # Fetch live game data for the game involving the Chicago Blackhawks
#     gd.get_live_game_data(chicago_game)
#
#     # Print the live score
#     print(
#         f"Live Game: {gd.game_data['awayTeamName']['long']} {gd.game_data['awayScore']} vs {gd.game_data['homeTeamName']['long']} {gd.game_data['homeScore']}")
#
#     # Get live stats for all players on Chicago Blackhawks
#     is_away = gd.game_data['awayTeamName']['long'] == 'Chicago Blackhawks'
#     roster = gd.game_data['awayRoster'] if is_away else gd.game_data['homeRoster']
#
#     # Fetch live stats for each player on Chicago Blackhawks roster
#     print("Live Stats for Chicago Blackhawks players:")
#     for player_id, player_data in roster.items():
#         live_stats = gd.get_live_stats(player_data, is_away)
#         if live_stats:
#             print(live_stats)
#         else:
#             print(f"No live stats available for {player_data['name']} yet.")
# else:
#     print("Chicago Blackhawks are not playing today.")