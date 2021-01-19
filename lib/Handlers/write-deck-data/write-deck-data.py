import boto3

def prep_data_for_put(deck, deck_values, dynamo_data):
    variants = deck_values['variants'].union(dynamo_data['variants'])
    match_ups_combined = {}
    for match_up, match_up_results in deck_values['match_ups'].items():
        dynamo_data.get("match_ups", {})
        dynamo_deck = dynamo_data["match_ups"].get(deck, False)
        if dynamo_deck:
            dynamo_wins = dynamo_deck["wins"]
            dynamo_losses = dynamo_deck["losses"]
        else:
            dynamo_wins = 0
            dynamo_losses = 0

        match_ups_combined[match_up] = {
            "wins": (match_up_results['wins'] + dynamo_wins),
            "losses": (match_up_results['losses'] + dynamo_losses)
        }

    return match_ups_combined

def lambda_handler(event, context):

    dynamo = boto3.resource('dynamodb')
    deck_table = dynamo.Table('LoR-Decks-Table')

    decks_to_update = event["Payload"]["decks_to_update"]

    for deck, deck_values in decks_to_update.items():

        previous_deck_info = deck_table.get_item(
            Key = {
                'legends': deck
            }
        )

        dynamo_data = previous_deck_info.get('Items', {})

        # Prep Dynamo Data
        if dynamo_data == {}:
            codes_dynamo = set()
            wins_dynamo = 0
            losses_dynamo = 0
        else:
            codes_dynamo = previous_deck_info['Items'][deck]['variants']
            wins_dynamo = previous_deck_info['Items'][deck]['wins']
            losses_dynamo = previous_deck_info['Items'][deck]['losses']

        variants = deck_values['variants'].union(codes_dynamo)
        wins = wins_dynamo + deck_values['wins']
        losses = losses_dynamo + deck_values['losses']
        
        deck_table.put_item(
            Item = {
                'legends': deck,
                'variants': variants,
                'wins': wins,
                'losses': losses,
                'match_ups': prep_data_for_put(deck, deck_values, dynamo_data.get(deck, {}))
            }
        )

    return




