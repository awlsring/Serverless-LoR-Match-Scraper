import requests
import json
import boto3
import base64
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
    Function to pull a player match from Riot API.
    '''
    secret = get_secret()

    header = {"X-Riot-Token": secret}
    
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