import requests
import json

def lambda_handler(event, context):
    '''
    Function to pull player matches from Riot API.
    '''
    # API Key in header. Store in AWS key store
    header = {"X-Riot-Token": "RGAPI-988b244e-3499-471a-93bd-823dc777102b" }
    
    region = event["Payload"]['current_player']['region']
    match_id = event["Payload"]["current_player"]["matches_to_check"][0]

    endpoint = f"https://{region}.api.riotgames.com/lor/match/v1/matches/{match_id}"

    match = requests.get(endpoint, headers=header)

    current_match = {}

    current_match['status_code'] = match.status_code
    if match.status_code == 429:
        current_match['retry_after'] = match.headers['Retry-After']
    current_match['Data'] = match.json()
    current_match['match_id'] = match_id

    event["Payload"]['current_player']['current_match'] = current_match

    return event["Payload"]