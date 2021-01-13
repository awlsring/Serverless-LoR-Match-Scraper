import boto3

def lambda_handler(event, context):
    '''
    Function to pull player list from DDB.
    '''
    dynamo = boto3.resource('dynamodb')
    match_table = dynamo.Table('LoR-Player-Table')

    current_player = event["Payload"]['current_player']

    match_table.update_item(
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

    for player in event['Payload']['players']:
        if player["player_uuid"] == current_player["player_uuid"]:
            event['Payload']['players'].remove(player)

    event['Payload'].pop('current_player', None)

    if len(event['Payload']['players']) == 0:
        event['Payload']["all_players_checked"] = True

    return event["Payload"]