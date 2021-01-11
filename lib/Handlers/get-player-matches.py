import requests

def lambda_handler(event, context):
    '''
    Function to pull player matches from Riot API.
    '''
    
    # API Key in header 
    header = {"X-Riot-Token": "RGAPI-6d962893-7cf1-411a-9734-2deb4189adbf" }
    
    player_to_process = event["players"][0]

    region = player_to_process['region']
    player_uuid = player_to_process['player_uuid']

    endpoint = f"https://{region}.api.riotgames.com/lor/match/v1/matches/by-puuid/{player_uuid}/ids"

    matches = requests.get(endpoint, headers=header)

    match_result = {}

    match_result['status_code'] = matches.status_code
    match_result['headers'] = matches.headers
    match_result['Data'] = matches.json()

    event["match_result"] = match_result
    event["current_player"] = player_to_process

    return event

    # if matches.status_code == 200:
    #     # match_list = matches.json()

    #     # matches_to_check = []

    #     # for match in match_list:
    #     #     if match not in match_cache:
    #     #         matches_to_check.append(match)

    #     # return matches_to_check
    #     return matches

    # elif matches.status_code == 429:
    #     return matches.headers
    # else:
    #     return "oof"