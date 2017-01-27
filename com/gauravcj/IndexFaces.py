'''
Created on Jan 16, 2017

@author: jagavkar
'''

from argparse import ArgumentParser
import boto3
import os

def get_rekognition_client():
    client = boto3.client('rekognition', region_name='us-east-1')
    return client

def get_dynamodb_table():
    dynamodb = boto3.resource('dynamodb',region_name='us-east-1')
    facesTable = dynamodb.Table("WildWestFaces")
    return facesTable

def get_args():
    parser = ArgumentParser(description='Call index faces')
    parser.add_argument('-f', '--folder')
    parser.add_argument('-i', '--image')
    parser.add_argument('-c', '--collection')
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    client = get_rekognition_client()
    print args.folder
    if (args.folder is not None):
        for subdir, dirs, files in os.walk(args.folder):
            for foundfile in files:
                print (foundfile)
                with open(os.path.join(subdir, foundfile), 'rb') as image:
                    response = client.index_faces(Image={'Bytes': image.read()}, CollectionId=args.collection)
                    faceid = response["FaceRecords"][0]["Face"]["FaceId"]
                personName =  (str(foundfile)).replace('.jpg', '')
                print ("Person ::"+personName+ "   faceid::"+faceid)
                table = get_dynamodb_table()
                response = table.put_item(
                            Item={
                                'faceid': str(faceid),
                                'personname': personName
                                }
                            )
    
