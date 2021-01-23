import requests
import json
import boto3
import base64
import time
import datetime
import get_secret as secrets

def lambda_handler(event, context):
    '''
    Function to pull list of player matches from Riot API.
    '''
    secret_name = "Riot-API-Key"
    region_name = "us-west-2"

    secret = secrets.get_secret(secret_name, region_name)

    header = {"X-Riot-Token": secret}
    
    player_to_process = event["Payload"]["players"][0]
    event["Payload"]["current_player"] = player_to_process

    region = player_to_process['region']
    player_uuid = player_to_process['player_uuid']

    endpoint = f"https://{region}.api.riotgames.com/lor/match/v1/matches/by-puuid/{player_uuid}/ids"

    matches = requests.get(endpoint, headers=header)

    match_result = {}

    match_result['status_code'] = matches.status_code
    event["Payload"]["match_result"] = match_result

    if matches.status_code == 200:
        match_result['Data'] = matches.json()
        match_cache = event["Payload"]["current_player"]['match_cache']
        matches_to_check = []

        for match in match_result['Data']:
            if match not in match_cache:
                matches_to_check.append(match)

        event["Payload"]["current_player"]["match_cache"] = matches.json()
        event["Payload"]["current_player"]["matches_to_check"] = matches_to_check

        if len(matches_to_check) == 0:
            event["Payload"]["all_matches_checked"] = True
        else:
            event["Payload"]["all_matches_checked"] = False

    elif matches.status_code == 429:
        back_off_till = (round(time.time()) + int(match.headers['Retry-After']))
        match_result['retry_after'] = datetime.datetime.fromtimestamp(back_off_till).isoformat()

    return event["Payload"]