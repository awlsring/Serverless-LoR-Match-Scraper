import boto3

def lambda_handler(event):
    '''
    Function to pull player list from DDB.
    '''
    dynamo = boto3.resource('dynamodb')
    match_table = dynamo.Table('LoR-Wins-Table')

    match = event['current_player']['current_match']['Data']

    match_id = match["metadata"]["match_id"]
    match_mode = match["info"]["game_mode"]
    match_type = match["info"]["game_type"]
    match_date = match["info"]["game_start_time_utc"]

    # Player1 is starting player
    for entry in match["info"]["players"]:
        if entry['order_of_play'] == 1:
            player1 = entry['puuid']
            player1_deck = entry["deck_code"]
        else:
            player2 = entry["puuid"]
            player2_deck = entry["deck_code"]

        if entry['game_outcome'] == 'win':
            winner = entry['puuid']
        else:
            loser = entry['puuid']

    # Make player1 always the starting player
    match_table.put_item(
        Item = {
           'MatchID': {
               'S': match_id
           },
           'Date': {
               'S': match_date
           },
           'Mode': {
               'S': match_mode
           },
           'Type': {
               'S': match_type
           },
           'Player1 UUID': {
               'S': player1
           },
           'Player2 UUID': {
               'S' : player2
           },
           'Player1 Deck': {
               'S' : player1_deck
           },
           'Player2 Deck': {
               'S' : player2_deck
           },
           'Winner': {
               'S': winner
           },
           'Loser': {
               'S': loser
           }
        },
        ConditionExpression = 'attribute_not_exists'
    )
    
    # Delete current match from dict
    event['current_player'].pop('current_match', None)

    # Remove match from matches_to_check
    event["current_player"]["matches_to_check"].remove(match_id)

