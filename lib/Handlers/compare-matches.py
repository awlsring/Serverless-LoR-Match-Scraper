def lambda_handler(event, context):
    '''
    Function to pull player matches from Riot API.
    '''
    matches = event["Payload"]['match_result']['Data']
    match_cache = event["Payload"]["current_player"]['match_cache']

    matches_to_check = []

    for match in matches:
        if match not in match_cache:
            matches_to_check.append(match)

    event["Payload"]["current_player"]["match_cache"] = matches
    event["Payload"]["current_player"]["matches_to_check"] = matches_to_check

    if len(matches_to_check) == 0:
        event["Payload"]["all_matches_checked"] = True
    else:
        event["Payload"]["all_matches_checked"] = False

    return event["Payload"]