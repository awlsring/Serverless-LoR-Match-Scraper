import requests
import json

def lambda_handler(event, context):
    '''
    Function to pull player matches from Riot API.
    '''
    
    # API Key in header 
    header = {"X-Riot-Token": "RGAPI-988b244e-3499-471a-93bd-823dc777102b" }
    
    player_to_process = event["Payload"]["players"][0]

    region = player_to_process['region']
    player_uuid = player_to_process['player_uuid']

    endpoint = f"https://{region}.api.riotgames.com/lor/match/v1/matches/by-puuid/{player_uuid}/ids"

    matches = requests.get(endpoint, headers=header)

    match_result = {}

    match_result['status_code'] = matches.status_code
    if matches.status_code == 429:
        match_result['retry_after'] = matches.headers['Retry-After']
    match_result['Data'] = matches.json()

    event["Payload"]["match_result"] = match_result
    event["Payload"]["current_player"] = player_to_process

    return event["Payload"]