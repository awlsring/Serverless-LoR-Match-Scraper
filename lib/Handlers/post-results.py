import boto3
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    '''
    Function to post data with match results from clients to Dynamo table

    