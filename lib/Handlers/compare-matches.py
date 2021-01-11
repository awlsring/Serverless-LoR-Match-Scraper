def lambda_handler(event, context):
    '''
    Function to pull player matches from Riot API.
    '''
    matches = event['match_result']['Data']
    match_cache = event["current_player"]['match_cache']

    matches_to_check = []

    for match in matches:
        if match not in match_cache:
            matches_to_check.append(match)

    event["current_player"]["matches_to_check"] = matches_to_check
    event["all_matches_checked?"] = False

    return event