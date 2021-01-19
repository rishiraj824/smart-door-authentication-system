import json
import os
import boto3
import math, random
import uuid
from datetime import datetime, timedelta

PASSCODE_TABLE = 'passcodes'
VISITOR_USER_TABLE = 'visitors'
REK_COLLECTION = 'smart-door-collection'
S3_BUCKET = 'cc-smart-door'

def store_in_db(payload, TABLE_NAME):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)
    print(payload)
    response = table.put_item(
        Item=payload
    )
    print(response)
    
    return response

def add_faces_to_collection(bucket, photo, collection_id):

    client=boto3.client('rekognition')

    response=client.index_faces(CollectionId=collection_id,
                                Image={'S3Object':{'Bucket':bucket,'Name':photo}},
                                ExternalImageId=photo,
                                MaxFaces=1,
                                QualityFilter="AUTO",
                                DetectionAttributes=['ALL'])

    print ('Results for ' + photo)  
    print('Faces indexed:')                     
    for faceRecord in response['FaceRecords']:
         return faceRecord['Face']['FaceId']
    return len(response['FaceRecords'])


def send_sms(number, message):
    sns = boto3.client(
        'sns',
        aws_access_key_id=os.getenv('AWS_SERVER_PUBLIC_KEY'),
        aws_secret_access_key=os.getenv('AWS_SERVER_SECRET_KEY')
    )

    smsattrs = {
        'AWS.SNS.SMS.SenderID': {
            'DataType': 'String',
            'StringValue': 'TestSender'
        },
        'AWS.SNS.SMS.SMSType': {
            'DataType': 'String',
            'StringValue': 'Promotional'  # change to Transactional from Promotional for dev
        }
    }

    response = sns.publish(
        PhoneNumber=number,
        Message=message,
        MessageAttributes=smsattrs
    )
    print(number)
    print(response)
    print("The message is: ", message)

def generate_OTP():
  
    digits = "0123456789"
    OTP = ""
  
    for i in range(6) : 
        OTP += digits[math.floor(random.random() * 10)] 
  
    return OTP

def lambda_handler(event, context):
    print(event)
    if 'body' in event:
        event = json.loads(event['body'])
    print("name = " + event['name'])
    print("phone number = " + event['phoneNumber'])
    
    phoneNumber = event['phoneNumber']
    name = event['name']
    s3Image = event['image']
    
    OTP = generate_OTP()
    
    faceId = add_faces_to_collection(S3_BUCKET, s3Image, REK_COLLECTION)
    print(faceId)
    otpDetails = {
        "otp": OTP,
        "faceId": faceId,
        "timestamp": int((datetime.now() + timedelta(seconds=5*60)).timestamp())
    }
    
    store_in_db(otpDetails, PASSCODE_TABLE)
    
    photos = [{
        "objectKey": s3Image,
        "bucket": S3_BUCKET,
        "createdTimestamp": int(datetime.now().timestamp())
    }]
    userDetails = {
        "faceId": faceId,
        "name": name,
        "phoneNumber": phoneNumber,
        "timestamp": int((datetime.now() + timedelta(seconds=5*60)).timestamp()),
        "photos": photos
    }
    store_in_db(userDetails, VISITOR_USER_TABLE)
    
    url = "http://smart-door-cloud.s3-website-us-east-1.amazonaws.com/otp?faceId="+faceId
    
    send_sms("+1"+phoneNumber, "Hi " + name + "! Open "+ url+ ". Please use this OTP to access the door " + OTP)
    return {
    'statusCode': 200,
    'headers': {
        "Access-Control-Allow-Headers" : "*",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,POST",
        "Content-Type": "application/json"
    },
    'body': json.dumps({'message': 'Successfully Saved'})
    }
