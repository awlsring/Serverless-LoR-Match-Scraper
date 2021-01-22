import requests
import json
import boto3
import base64
import time
import datetime
from botocore.exceptions import ClientError

def get_secret():
    secret_name = "Riot-API-Key"
    region_name = "us-west-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            raise e
    else:
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            secret = base64.b64decode(get_secret_value_response['SecretBinary'])
    
    secret = secret.split(":")
    secret = secret[1].strip('"}')

    return secret

def lambda_handler(event, context):
    '''
    Function to pull list of player matches from Riot API.
    '''
    secret = get_secret()

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