from lor_deckcodes import LoRDeck, CardCodeAndCount
import boto3
import time
import json

def lambda_handler(event, context):
    '''
    Writes match data from current match to LoR-Match-Table.

    After writing match, adds a win or loss to current tracked player depending on
    the match outcome.
    '''
    dynamo = boto3.resource('dynamodb')
    match_table = dynamo.Table('LoR-Match-Table')

    current_player = event["Payload"]['current_player']

    match = event["Payload"]['current_player']['current_match']['Data']
    match_id = match["metadata"]["match_id"]
    match_mode = match["info"]["game_mode"]
    match_type = match["info"]["game_type"]
    match_turns = match["info"]["total_turn_count"]

    match_date = format_time(match["info"]["game_start_time_utc"])

    single_player = False
    if len(match["info"]["players"]) == 1:
        single_player = True

    if not single_player:
        # Player1 is starting player
        for entry in match["info"]["players"]:
            if entry['order_of_play'] == 1:
                deck = entry["deck_code"]
                deck_champions = get_champions_in_deck(deck)
                
                player1 = entry['puuid']
                player1_deck = deck
                player1_factions = entry["factions"]
                player1_champions = deck_champions

            else:
                deck = entry["deck_code"]
                deck_champions = get_champions_in_deck(deck)

                player2 = entry["puuid"]
                player2_deck = deck
                player2_factions = entry["factions"]
                player2_champions = deck_champions

            if entry['game_outcome'] == 'win':
                winner = entry['puuid']
            else:
                loser = entry['puuid']

        # Make player1 always the starting player
        match_table.put_item(
            Item = {
            'match_id': match_id,
            'date': match_date,
            'mode': match_mode,
            'type': match_type,
            'turn_count': match_turns,
            'player1_uuid': player1,
            'player2_uuid': player2,
            'player1_deck': player1_deck,
            'player2_deck': player2_deck,
            'player1_factions': player1_factions,
            'player2_factions': player2_factions,
            'player1_champions': player1_champions,
            'player2_champions': player2_champions,
            'winner': winner,
            'loser': loser
            },
            ConditionExpression = 'attribute_not_exists(MatchID)'
        )
    
        if winner == current_player['player_uuid']:
            current_player['wins'] = current_player['wins'] + 1
        else:
            current_player['losses'] = current_player['losses'] + 1

    # Delete current match from dict
    current_player.pop('current_match', None)

    # Remove match from matches_to_check
    current_player["matches_to_check"].remove(match_id)

    # Remove Player if all matches are cleared
    if len(current_player["matches_to_check"]) == 0:
        event["Payload"]["all_matches_checked"] = True

    return event["Payload"]

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

    return champions_in_deck