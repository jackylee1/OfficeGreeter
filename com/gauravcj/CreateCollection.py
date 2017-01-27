'''
Created on Jan 16, 2017

@author: jagavkar
'''
import boto3


if __name__ == '__main__':
    client = boto3.client('rekognition')
    response = client.create_collection(CollectionId='wildwest')
    print response
    pass