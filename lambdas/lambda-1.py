import json
import base64
import time
import boto3
import cv2
import math, random, time
import os


PASSCODE_TABLE = 'passcodes'
VISITOR_TABLE = 'visitors'
S3_FACE_BUCKET = 'cc-smart-door'
OWNER_NUMBER = '9293347904'
BASE_URL = 'http://smart-door-cloud.s3-website-us-east-1.amazonaws.com/'
OTP_URL = BASE_URL+'otp'


def lambda_handler(event, context):
    # TODO implement
    print("event : ",event)
    matchedFaceCount = 0;
    detectedFaceCount = 0;
    matchedFaces = set();
    streamARN = None
    fragmentNumber = None
    Records = event['Records']
    try:
        for record in Records:
            load = base64.b64decode(record['kinesis']['data'])
            payload = json.loads(load)
            print('data : ',payload)
            if payload['FaceSearchResponse'] is not None:
                faceSearchResponse = payload['FaceSearchResponse']
                for face in faceSearchResponse:
                    data = payload['InputInformation']['KinesisVideo']
                    if streamARN is None:
                        streamARN = data['StreamArn']
                    if fragmentNumber is None:
                        fragmentNumber = data['FragmentNumber']
                    if face['DetectedFace'] is not None:
                        detectedFaceCount+=1
                    if face['MatchedFaces'] is not None and len(face['MatchedFaces'])>0 and face['MatchedFaces'][0]['Face'] is not None and face['MatchedFaces'][0]['Face']['FaceId'] is not None:
                        matchedFaceCount+=1
                        matchedFaces.add(face['MatchedFaces'][0]['Face']['FaceId'])
                        
    except:
        print("An exception occurred while looping records")
    fileName = ""
    try:
        print("matchedFaceCount : ",  matchedFaceCount,  " detectedFaceCount : ", detectedFaceCount)
        fileName=store_image(streamARN,fragmentNumber)
    except:
        print("An exception occurred while storing image")
        
    if matchedFaceCount > 0:
        for faceId in matchedFaces:
            print("Face found : " + faceId)
            try:
                authorize(faceId,fileName)
            except Exception as e:
                print("An exception occurred while authorizing : ",e)

    elif detectedFaceCount > 0:
        print("New face detected");
        url = BASE_URL + '?image=' + fileName
        message = "Someone at gate. Please click on this link to view and take action: " + url; 
        print(message)
        send_sms(message,OWNER_NUMBER)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
    
def get_item(payload, TABLE_NAME):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)
    response = table.get_item(
        Key=payload
    )
    if 'Item' in response:
        return response['Item']
    else:
        return None
        
        
def store_in_db(payload, TABLE_NAME):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)
    print(payload)
    response = table.put_item(
        Item=payload
    )
    print(response)
    return response
    
    
def generate_OTP():
    print('in generate_OTP')
    digits = "0123456789"
    OTP = ""
    for i in range(6) : 
        OTP += digits[math.floor(random.random() * 10)]
    response = None
    try:
        response = get_item({'otp': OTP}, PASSCODE_TABLE)
        print(response)
    except:
        print('Exception occurred while checking opt uniqueness')
    if response is not None:
        generate_OTP()
    return OTP

# def send_sms(message,phoneNumber):
#     print('send_sms')
#     sns = boto3.client('sns')
#     x = sns.publish(PhoneNumber = "+1" + phoneNumber, Message=message )
#     print("SNS Result : " , x)

def send_sms(message, number):
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
        PhoneNumber= "+1" + number,
        Message=message,
        MessageAttributes=smsattrs
    )
    print(number)
    print(response)
    print("The message is: ", message)


def authorize(faceId,fileName):
    print("Authorize")
    response = get_item({'faceId': faceId}, VISITOR_TABLE)
    print("response from visitors table: ",response)
    if response is None:
        return
    phoneNumber = response['phoneNumber']
    name = response['name']
    print("phoneNumber: " , phoneNumber , " name : " , name)
    OTP = generate_OTP()
    print('otp : ' , OTP)
    otpDetails = {
        "otp": OTP,
        "faceId": faceId,
        "timestamp": str(int(time.time() + 300))
    }
    store_in_db(otpDetails, PASSCODE_TABLE)
    url = OTP_URL+ '?faceId=' + faceId
    print(url)
    message = "Hi " + name + "Link : " + url + "! Please click on the link and use this OTP to access the door " + OTP
    send_sms(message,phoneNumber)
    photos = response['photos']
    photo = {
        "objectKey": fileName,
        "bucket": S3_FACE_BUCKET,
        "createdTimestamp": str(time.time())
    }
    photos.append(photo)
    userDetails = {
        "faceId": faceId,
        "name": name,
        "phoneNumber": phoneNumber,
        "photos" : photos,
        "timestamp" : str(time.time())
    }
    store_in_db(userDetails, VISITOR_TABLE)
    
def store_image(streamARN, fragmentNumber):
    if streamARN is None or fragmentNumber is None:
        return
    print("In store_image")
    s3_client = boto3.client('s3')
    rekClient=boto3.client('rekognition')
    
    kvs = boto3.client("kinesisvideo")
    
    endpoint = kvs.get_data_endpoint(
        APIName="GET_MEDIA",
        StreamARN=streamARN
    )['DataEndpoint']
    print("Kinesis Data endpoint: ",endpoint)

    kvam = boto3.client("kinesis-video-media", endpoint_url=endpoint)

    kvs_stream = kvam.get_media( StreamARN=streamARN, StartSelector={ 'StartSelectorType': 'FRAGMENT_NUMBER', 'AfterFragmentNumber': fragmentNumber})

    
    print("KVS Stream: ",kvs_stream)
    with open('/tmp/stream.mkv', 'wb') as f:
        streamBody = kvs_stream['Payload'].read()
        f.write(streamBody)
        cap = cv2.VideoCapture('/tmp/stream.mkv')
        ret, frame = cap.read() 
        cv2.imwrite('/tmp/frame.jpg', frame)
        fileName= fragmentNumber+ '-T-'+ str(time.time())+'.jpg'
        print ('uploading : ',fileName)
        s3_client.upload_file(
            '/tmp/frame.jpg',
            S3_FACE_BUCKET, 
            fileName
        )
        cap.release()
        print ('uploaded : ',fileName)

    return fileName
