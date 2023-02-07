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
            #'Access-Control-Allow-Origin': 'http://nyp-lostnfoundwebsite-201665w.s3-website-us-east-1.amazonaws.com/',
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
        FilterExpression= "contains(ItemName, :item_name)",
        ExpressionAttributeValues={
            ":item_name": {"S": item_name}
        })
    return (200, response)
    
def putItems(event):
    client = boto3.client('dynamodb')
    body = json.loads(event["body"])
    ItemID = str(uuid.uuid4())
    data = {}
    if "Location" in body:
            data={
            'ItemID': {'S': ItemID},
            'DateTimeFound': {'S': body["DateTimeFound"]},
            'ItemName': {'S': body["ItemName"]},
            'Brand': {'S': body["Brand"]},
            'Description': {'S': body["Description"]},
            'Indoors': {'BOOL': body["Indoors"]},
            'Location': {'S': str(body["Location"])}
        }
    else:
        data={
            'ItemID': {'S': ItemID},
            'DateTimeFound': {'S': body["DateTimeFound"]},
            'ItemName': {'S': body["ItemName"]},
            'Block': {'S': body["Block"]},
            'Level': {'S': body["Level"]},
            'Brand': {'S': body["Brand"]},
            'Description': {'S': body["Description"]},
            'Indoors': {'BOOL': body["Indoors"]},
            'RoomNo': {'S': str(body["RoomNo"])}
        }
    response = client.put_item(
        TableName='NYP-LostNFound',
            Item = data
        )
    save_img_s3(ItemID, body["ImageEncoded"])
    return (200, response)

def save_img_s3(id, base64_img):
    s3 = boto3.resource('s3')
    bucket_name = "nyp-lostnfoundwebsite-201665w"
    file_name = "images/items/" + id + ".png"
    obj = s3.Object(bucket_name, file_name)
    obj.put(Body=base64.b64decode(base64_img))
    location = boto3.client('s3').get_bucket_location(Bucket=bucket_name)['LocationConstraint']