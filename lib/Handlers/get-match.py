import requests

def lambda_handler(event, context):
    '''
    Function to pull player matches from Riot API.
    '''
    # API Key in header. Store in AWS key store
    header = {"X-Riot-Token": "RGAPI-6d962893-7cf1-411a-9734-2deb4189adbf" }
    
    region = event['current_player']['region']
    match_id = event["current_player"]["matches_to_check"][0]

    endpoint = f"https://{region}.api.riotgames.com/lor/match/v1/matches/{match_id}"

    match = requests.get(endpoint, headers=header)

    current_match = {}

    current_match['StatusCode'] = match.status_code
    current_match['Headers'] = match.headers
    current_match['Data'] = match.json()
    current_match['MatchID'] = match_id

    event['current_player']['current_match'] = current_match

    return event