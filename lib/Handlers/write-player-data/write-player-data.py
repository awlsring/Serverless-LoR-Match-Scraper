import boto3

def lambda_handler(event, context):
    '''
    Update player entry in DynamoDB with new wins, losses, and match_cache.
    '''
    dynamo = boto3.resource('dynamodb')
    player_table = dynamo.Table('LoR-Player-Info-Table')
    player_deck_table = dynamo.Table('LoR-Player-Deck-Table')

    current_player = event["Payload"]['current_player']
    current_player_puuid = current_player["player_uuid"]
    player_deck_data = event["Payload"]["players_to_update"][current_player_puuid]

    # Update Player Entry
    player_table.update_item(
        Key = {
            'player_uuid': current_player['player_uuid'],
        },
        UpdateExpression='SET losses=:l, wins=:w, match_cache=:m',
        ExpressionAttributeValues={
            ':l': current_player['losses'],
            ':w': current_player['wins'],
            ':m': current_player['match_cache'],
        },
    )

    # Write catch
    previous_deck_info = player_deck_table.get_item(
        Key = {
            'player_uuid': current_player['player_uuid']
        }
    )

    update_expression, expression_attribute_values = generate_dynamo_update_params(
        player_deck_data,
        previous_deck_info.get("Items", {})
    )

    player_deck_table.update_item(
        Key = {
            'player_uuid': current_player['player_uuid']
        },
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attribute_values,
    )

    for player in event['Payload']['players']:
        if player["player_uuid"] == current_player["player_uuid"]:
            event['Payload']['players'].remove(player)

    event['Payload'].pop('current_player', None)
    event["Payload"]["players_to_update"].pop(current_player_puuid, None)

    if len(event['Payload']['players']) == 0:
        event['Payload']["all_players_checked"] = True

    return event["Payload"]

def generate_dynamo_update_params(deck_data, dynamo_data):
    update_expression = 'SET '
    expression_attribute_values = {}
    i = 1
    for deck, deck_values in deck_data.items():
        if dynamo_data == {}:
            codes_dynamo = set()
            wins_dynamo = 0
            losses_dynamo = 0
        else:
            codes_dynamo = dynamo_data[deck]['variants']
            wins_dynamo = dynamo_data[deck]['wins']
            losses_dynamo = dynamo_data[deck]['losses']

        update_expression = f"{update_expression} {deck}=:{i},"

        expression_attribute_values[f'{i}'] = {
            "variants": deck_values["variants"].union(codes_dynamo),
            "wins": (deck_values.get("wins", 0) + wins_dynamo),
            "losses": (deck_values.get("wins", 0) + losses_dynamo)
        }

        i += 1

    update_expression = update_expression[:-1]

    return update_expression, expression_attribute_values