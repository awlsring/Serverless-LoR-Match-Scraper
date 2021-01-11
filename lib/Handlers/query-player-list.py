import boto3

def lambda_handler():
    '''
    Function to pull player list from DDB.
    '''
    dynamo = boto3.resource('dynamodb')
    player_list_table = dynamo.Table('LoR-Player-Table')

    scan_results = player_list_table.scan()

    player_entries = scan_results['Items']

    return {
        "players": player_entries,
        "all_players_checked?": False
    }