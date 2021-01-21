import json
import requests
import boto3
import base64
from botocore.exceptions import ClientError

def get_secret():
    ###
    # TODO Share this function acroos lambdas
    ###
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
    Recieve player name and region. Query riot api to get player id.
    '''
    secret = get_secret()
    header = {"X-Riot-Token": secret}
    
    username = event["username"]
    region = event["region"]

    # Technically Americas can find any player, but it is better practice to use a closer endpoint
    endpoint = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{username}/{region}"

    query_player = requests.get(endpoint, headers=header)

    if query_player.status_code == 200:
        json_response = query_player.json()
        player_uuid = json_response["puuid"]
        player_name = json_response["gameName"]
        player_tag = json_response["tagLine"]

        americas = {"NA", "BR", "LAN", "LAS", "OCE"}
        asia = {"KR", "JP"}
        europe = {"EUNE", "EUW", "TR", "RU"}

        player_tag_no_digit = ''.join([i for i in player_tag if not i.isdigit()])

        if player_tag_no_digit in americas:
            region = "americas"
        elif player_tag_no_digit in asia:
            region = "asia"
        elif player_tag_no_digit in europe:
            region = "europe"

        dynamo = boto3.resource('dynamodb')
        player_info_table = dynamo.Table('LoR-Player-Info-Table')

        try:
            player_info_table.put_item(
                Item = {
                'player_uuid': player_uuid,
                'last_scanned': 0,
                'region': region,
                'match_cache': [],
                'wins': 0,
                'losses': 0,
                'player_name': player_name,
                'player_tag': player_tag,
                },
                ConditionExpression = 'attribute_not_exists(player_uuid)'
            )
        except ClientError:
            return "Player already in database"

        player_deck_table = dynamo.Table('LoR-Player-Decks-Table')

        try:
            player_deck_table.put_item(
                Item = {
                'player_uuid': player_uuid,
                },
                ConditionExpression = 'attribute_not_exists(player_uuid)'
            )
        except ClientError:
            return "Player already in database"

        player_matches_table = dynamo.Table('LoR-Player-Matches-Table')

        try:
            player_matches_table.put_item(
                Item = {
                'player_uuid': player_uuid,
                },
                ConditionExpression = 'attribute_not_exists(player_uuid)'
            )
        except ClientError:
            return "Player already in database"
        else:
            return "Player found and added to the database."

    elif query_player.status_code == 404:
        return "Player not found"
    elif query_player.status_code >= 500:
        return "Server error. Try again later."
    else:
        return "Unknown error"