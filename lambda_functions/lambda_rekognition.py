import json
import boto3
import uuid
import base64


def lambda_handler(event, context):
    if event["path"] == "/":
        if event["httpMethod"] == "GET":
            response = getItemsByQuery(event)
        if event["httpMethod"] == "PUT":
            response = putItems(event)
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


def getItemsByQuery(event):
    client = boto3.client('dynamodb')
    item_name = event["queryStringParameters"]["ItemName"]
    response = client.scan(
        TableName='NYP-LostNFound',
        FilterExpression="contains(ItemName, :item_name)",
        ExpressionAttributeValues={
            ":item_name": {"S": item_name}
        })
    return (200, response)


def putItems(event):
    client = boto3.client('dynamodb')
    body = json.loads(event["body"])
    ItemID = str(uuid.uuid4())
    imageBytes = save_img_s3(ItemID, body["ImageEncoded"])
    data = {
        'ItemID': {'S': ItemID},
        'DateFound': {'S': body["DateFound"]},
        'ItemName': {'S': body["ItemName"]},
        'Category': {'S': body["Category"]},
        'Colour': {'S': body["Colour"]},
        'Description': {'S': body["Description"]},
        'Indoors': {'BOOL': body["Indoors"]},
    }
    if "Location" in body:
        data["Location"] = {'S': str(body["Location"])}
        location = body["Location"]
    else:
        data["Block"] = {'S': body["Block"]}
        data["Level"] = {'S': body["Level"]}
        data["RoomNo"] = {'S': body["RoomNo"]}
        location = f'{body["Block"]}.{body["Level"]}{body["RoomNo"]}'
    response = client.put_item(
        TableName='NYP-LostNFound',
        Item=data
    )
    send_email_sns(body["ItemName"], body["Category"],
                   location, body["Description"], body["Colour"])
    return (200, response)


def save_img_s3(id, base64_img):
    client = boto3.client('s3')
    BUCKET_NAME = "nyp-lostnfoundwebsite-201665w"
    file_name = "images/items/" + id + ".png"
    imageBytes = base64.b64decode(base64_img)
    response = client.put_object(
        Body=imageBytes,
        Bucket=BUCKET_NAME,
        Key=file_name
    )

    return


def send_email_sns(name, category, location, description, colour):
    client = boto3.client('sns')
    response = client.publish(
        TopicArn='arn:aws:sns:us-east-1:328337088526:nyp-lostnfoundwebsite-201665w-topic',
        Message=f'Found Item: {name}\n' +
        f'Location: {location}\n' +
        f'Description: {description}\n' +
        f'Color: {colour}\n' +
        'Check out found items on our website: http://nyp-lostnfoundwebsite-201665w.s3-website-us-east-1.amazonaws.com/',
        Subject=f"NYP's LostNFound - Found Item for Category: {category}",
        MessageAttributes={
            "category": {
                "DataType": "String",
                "StringValue": category
            }
        }
    )
    return response
