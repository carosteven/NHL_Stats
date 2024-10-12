import pandas as pd
import requests
import json
import copy
import os
import urllib.parse as up

def urlencode_wrapper(qstrobj):
    return (up.urlencode(qstrobj, quote_via=up.quote)
            .replace('%3D', '=')
            .replace('%3A', ':')
            .replace('%2C', ',')
            .replace('%5B%27', '')
            .replace('%27%5D', '')
    )

def generate_qstrobj(qstrobj, start, year, skater):#, teamID):
    qstrobj = copy.deepcopy(qstrobj)
    qstrobj['start'] = start
    qstrobj['cayenneExp'][0] = qstrobj['cayenneExp'][0].format(year=year, skater=skater)#, teamID=teamID)
    # qstrobj['cayenneExp'][0] = qstrobj['cayenneExp'][0].format(skater=skater)
    return urlencode_wrapper(qstrobj)



class PlayerStats:
    def get_player_stats(self, years=['20232024'], pagination=[0]+[x * 100 + 1 for x in range(1, 4)], player='Mitchell Marner'):
        years = years
        pagination = pagination
        player = player

        url = ('https://api.nhle.com/stats/rest/en/skater/summary'
       '?isAggregate=false'
       '&isGame=true'
       '&sort=%5B%7B%22property%22:%22gameDate%22,%22direction%22:%22DESC%22%7D%5D'
       '&start=0'
       '&limit=100'
       '&factCayenneExp=gamesPlayed%3E=1'
       '&cayenneExp='#franchiseId%3D5%20and%20'
       'gameTypeId=2%20and%20'
        'seasonId%3C=20192020%20and%20seasonId%3E=20192020%20and%20'
        'skaterFullName%20likeIgnoreCase%20%22Auston%20Matthews%25%22'
        )

        url_base, qstring = url.split('?')
        qstrobj = up.parse_qs(qstring)
        qstrobj['cayenneExp'][0] = qstrobj['cayenneExp'][0].replace('20192020', '{year}').replace('Auston Matthews', '{skater}')#.replace('franchiseId%3D5', 'franchiseId%3D{teamID}')

        # years = [str(x) + str(x+1) for x in range(2021, 2022)]
        # years = ['20232024']
        # pagination = [45]# + [x * 100 + 1 for x in range(1, 4)]
        frames = []
        # TODO: To get most current game, any call returns "total" so set start to total - 1. But this means that you would have to make a call to get total first.
        for year in years:
            for start in pagination:
                qstring = generate_qstrobj(qstrobj, start, year, player)#, teamID)
                url = url_base + '?' + qstring
                response = requests.get(url)
                data = json.loads(response.text)
                frames.append(pd.DataFrame(data['data']))

        df = pd.concat(frames)
        return df[['gameDate', 'opponentTeamAbbrev', 'goals', 'assists', 'shots']].columns.values.tolist(), df[['gameDate', 'opponentTeamAbbrev', 'goals', 'assists', 'shots']].values.tolist()

        # df.to_csv('player_stats.csv', index=False)

# ps = PlayerStats()
# stats = ps.get_player_stats(player='Brock Boeser')
# print(stats)