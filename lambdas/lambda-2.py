import json
import boto3

PASSCODE_TABLE = 'passcodes'
VISITOR_TABLE = 'visitors'



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
        
def get_otp_validity(otp):
    response = get_item({'otp': otp}, PASSCODE_TABLE)
    if response:
        return True, response
    else:
        return False, response

def get_user_details(faceId):
    response = get_item({ 'faceId': faceId}, VISITOR_TABLE)
    print(response)
    if response:
        return response
    else:
        return None
    
def lambda_handler(event, context):
    
    print("otp = " + event['otp'])
    otp = event['otp']
    validOTP, user = get_otp_validity(otp)
    print("Validity", validOTP)
    print("user")
    if validOTP:
        user_details = get_user_details(user['faceId'])
    
   
        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Headers" : "*",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
                "Content-Type": "application/json"
            },
            'body': json.dumps({'message': 'Welcome to the house ' + user_details['name']})
        }
    
    return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Headers" : "*",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST",
                "Content-Type": "application/json"
            },
            'body': json.dumps({
                'message': 'Sorry access denied!'
            })
        }
