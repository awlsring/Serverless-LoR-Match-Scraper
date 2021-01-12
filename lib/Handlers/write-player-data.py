import boto3

def lambda_handler(event, context):
    '''
    Function to pull player list from DDB.
    '''
    dynamo = boto3.resource('dynamodb')
    match_table = dynamo.Table('LoR-Player-Table')

    current_player = event["Payload"]['current_player']

    match_table.put_item(
        Item = {
           'PUUID': {
               'S': current_player['player_uuid']
           },
           'region': {
               'S': current_player['region']
           },
           'wins': {
               'N': current_player['wins']
           },
           'losses': {
               'N': current_player['losses']
           },
           'match_cache': {
               'L': current_player['match_cache']
           }
        }
    )

    event['Payload']['players'].remove(event['Payload']['current_player'])
    event['Payload'].pop('current_player', None)

    return event["Payload"]
