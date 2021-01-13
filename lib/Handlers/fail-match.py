def lambda_handler(event, context):
    '''
    Function to pull player list from DDB.
    '''
    current_player = event["Payload"]['current_player']
    match_id = event["Payload"]['current_player']['current_match']['match_id']

    # Delete current match from dict
    current_player.pop('current_match', None)

    # Remove match from matches_to_check
    current_player["matches_to_check"].remove(match_id)

    # Remove Player if all matches are cleared
    if len(current_player["matches_to_check"]) == 0:
        event["Payload"]["all_matches_checked"] = True

    return event['Payload']
