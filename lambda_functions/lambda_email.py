import json
import boto3


def lambda_handler(event, context):
    body = json.loads(event["body"])
    response = subscribe_email_sns(body)
    return {
        'statusCode': response[0],
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            # 'Access-Control-Allow-Origin': 'http://nyp-lostnfoundwebsite-201665w.s3-website-us-east-1.amazonaws.com/',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(response[1])
    }


def subscribe_email_sns(body):
    client = boto3.client('sns')
    response = client.subscribe(
        TopicArn='arn:aws:sns:us-east-1:328337088526:nyp-lostnfoundwebsite-201665w-topic',
        Protocol='email',
        Endpoint=body["Email"],
        Attributes={
            'FilterPolicy': json.dumps({
                "category": [body["Category"]
                             ]
            })
        }
    )
    return (200, response)
