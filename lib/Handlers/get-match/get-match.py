import requests
import json
import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
import base64
import time
from lor_deckcodes import LoRDeck, CardCodeAndCount

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
    if match.status_code == 200:
        current_player = event["Payload"]['current_player']
        match_id = write_match(match.json(), event, current_player)
    
        # Remove match from matches_to_check
        current_player["matches_to_check"].remove(match_id)

        # Remove Player if all matches are cleared
        if len(current_player["matches_to_check"]) == 0:
            event["Payload"]["all_matches_checked"] = True

        return event["Payload"]
    elif match.status_code == 429:
        current_match['retry_after'] = match.headers['Retry-After']
        return event["Payload"]

def write_match(match, event, current_player):
    '''
    Writes match data from current match to LoR-Match-Table.

    After writing match, adds a win or loss to current tracked player depending on
    the match outcome.
    '''
    match_id = match["metadata"]["match_id"]
    match_mode = match["info"]["game_mode"]
    match_type = match["info"]["game_type"]
    match_turns = match["info"]["total_turn_count"]

    players_to_update = event["Payload"]["players_to_update"]
    decks_to_update = event["Payload"]["decks_to_update"]

    match_date = format_time(match["info"]["game_start_time_utc"])

    constructed = False
    if match_mode == "Constructed":
        constructed = True

    if constructed:
        dynamo = boto3.resource('dynamodb')
        match_table = dynamo.Table('LoR-Matches-Table')

        # Player1 is starting player
        for entry in match["info"]["players"]:
            if entry['game_outcome'] == 'win':
                winner = entry['puuid']
            else:
                loser = entry['puuid']

            if entry['order_of_play'] == 1:
                player1 = assemble_player_data(entry)
            else:
                player2 = assemble_player_data(entry)

        if winner == player1['uuid']:
            result = True
        else:
            result = False
        
        add_player_to_update_dict(players_to_update, player1['uuid'], player1['legends'], player1['deckcode'], player2['legends'], result)
        # add_player_to_update_dict(players_to_update, player2['uuid'], player2['legends'], player2['deckcode'], player1['legends'], (not result))
        decks_to_update(decks_to_update, player1['legends'], player1['deckcode'], player2['legends'], result)
        decks_to_update(decks_to_update, player2['legends'], player2['deckcode'], player1['legends'], (not result))

        try:
            match_table.put_item(
                Item = {
                'match_id': match_id,
                'date': match_date,
                'type': match_type,
                'turn_count': match_turns,
                'player1': player1,
                'player2': player2,
                'winner': winner,
                'loser': loser
                },
                ConditionExpression=Attr(match_id).not_exists() 
            )
        except ClientError:
            # Error will occur if match exists. This is fine, as it means two
            # tracked players have played against each other
            pass
    
        if winner == current_player['player_uuid']:
            current_player['wins'] = current_player['wins'] + 1
        else:
            current_player['losses'] = current_player['losses'] + 1

    return match_id

def form_legend_string(legends):
    legend_string = ""
    for legend in legends:
        legend_string = f"{legend_string}-{legend}"

    return legend_string

def assemble_player_data(entry):
    deckcode = entry["deck_code"]
    deck_champions = get_champions_in_deck(deckcode)
    uuid = entry['puuid']
    factions = entry["factions"]
    
    player = {
        "uuid": uuid,
        "deckcode": deckcode,
        "factions": factions,
        "legends": deck_champions
    }

    return player

def add_deck_to_update_dict(decks_to_update, legends, deckcode, opp_legends, result):
    if legends in decks_to_update:
        decks_to_update[legends]['variants'].add(deckcode)
    else:
        decks_to_update[legends] = {
            "variants": set(deckcode)
        }
    
    if opp_legends in decks_to_update[legends]['match_ups']:
        if result:
            decks_to_update[legends]['match_ups'][opp_legends]['wins'] += 1
            decks_to_update[legends]["wins"] = decks_to_update[legends]["wins"] + 1
        else:
            decks_to_update[legends]['match_ups'][opp_legends]['losses'] += 1
            decks_to_update[legends]["losses"] = decks_to_update[legends]["losses"] + 1
    else:
        decks_to_update[legends]['match_ups'] = {
            opp_legends: {
                'wins': 0,
                'losses': 0
            }
        }
        if result:
            decks_to_update[legends]['match_ups'][opp_legends]['wins'] += 1
            decks_to_update[legends]["wins"] = decks_to_update[legends]["wins"] + 1
        else:
            decks_to_update[legends]['match_ups'][opp_legends]['losses'] += 1
            decks_to_update[legends]["losses"] = decks_to_update[legends]["losses"] + 1

def add_player_to_update_dict(players_to_update, puuid, legends, deckcode, opp_legends, result):
    if result:
        match_result = 'wins'
    else:
        match_result = 'losses'

    if puuid in players_to_update:
        if legends in players_to_update[puuid]:
            players_to_update[puuid][legends]['variants'].add(deckcode)
        else:
            players_to_update[puuid][legends] = {
                "variants": set(deckcode)
            }
    else:
        players_to_update[puuid] = {
            legends: {
                "variants": set(deckcode)
            }
        }
    
    if players_to_update[puuid][legends][match_result] in players_to_update[puuid][legends]:
        players_to_update[puuid][legends][match_result] += 1
    else:
        players_to_update[puuid][legends][match_result] = 1

    add_deck_to_update_dict(players_to_update[puuid], legends, deckcode, opp_legends, result)

def format_time(date_riot):
    date_time = date_riot.split("T")
    date = date_time[0]
    time_string = date_time[1].split(".")
    time_string = time_string[0]

    pattern = '%Y-%m-%d %H:%M:%S'
    date_time = f"{date} {time_string}"
    time_tuple = time.strptime(date_time, pattern)
    epoch = int(time.mktime(time_tuple))

    return epoch

def get_champions_in_deck(deck_code):
    deck = LoRDeck.from_deckcode(deck_code)

    list(deck)
    deck_cards = set()

    for card in deck:
        card_split = card.split(":")
        deck_cards.add(card_split[1])

    with open('all_champions_codes.json') as champion_codes_file:
        champion_codes = json.load(champion_codes_file)

    set(champion_codes)

    champions_in_deck = deck_cards.intersection(champion_codes)

    legend_string = form_legend_string(champions_in_deck)

    return legend_string