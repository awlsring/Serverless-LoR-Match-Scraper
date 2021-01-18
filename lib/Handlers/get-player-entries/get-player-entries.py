import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

def lambda_handler(event, context):

    entry_amount = event['entry_amount']
    scope = event['scope']

    dynamo = boto3.resource('dynamodb')
    player_list_table = dynamo.Table('LoR-Player-Table')

    scan_results = player_list_table.scan(
        FilterExpression=Attr("wins").gt(1) or Attr("losses").gt(1)
    )

    return scan_results['Items']