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
        # self.today = '2024-01-29'

        # Get today's games
        self.games = self.get_schedule()

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
        
        if not live_game_dict['gameState'] == 'FUT':
            self.game_data["period"]= live_game_dict['period']
            self.game_data["timeRemaining"]= live_game_dict['clock']['timeRemaining']
            self.game_data["isIntermission"]= live_game_dict['clock']['inIntermission']

            self.game_data["awayShots"]= live_game_dict['awayTeam']['sog']
            self.game_data["homeShots"]= live_game_dict['homeTeam']['sog']

        self.get_roster(live_game_dict['rosterSpots'])

        awayOnIce = live_game_dict['awayTeam']['onIce']
        homeOnIce = live_game_dict['homeTeam']['onIce']

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

