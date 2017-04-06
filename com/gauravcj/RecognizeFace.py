#!/usr/bin/env python

from argparse import ArgumentParser
import boto3
from os import environ
import json
from pygame import mixer
import time
import subprocess
import sys


faceMap = {}

def get_args():
    parser = ArgumentParser(description='Call index faces')
    #parser.add_argument('-i', '--image')
    parser.add_argument('-c', '--collection')
    return parser.parse_args()

def get_rekognition_client():
    rekognition = boto3.client('rekognition', region_name='us-east-1')
    return rekognition


def get_dynamodb_table():
    print("Loading faces...")
    dynamodb = boto3.resource('dynamodb',region_name='us-east-1')
    facesTable = dynamodb.Table("WildWestFaces")
    return facesTable

def load_table_values():
    table = get_dynamodb_table()
    tableReturn = table.scan(ProjectionExpression = "faceid, personname")
    global faceMap
    for item in tableReturn["Items"]:
        faceMap[str(item["faceid"])] = str(item["personname"])
        
def capturePicture():
    print("Capturing picture...")
    subprocess.call (["fswebcam","-r", "640x480", "image.jpg"])

def makePollyWelcome(identifiedPerson, emotion):
    print ("Speaking...")
    speak = "Hi "+identifiedPerson+", you look "+ emotion+" today"
    
    polly = boto3.client('polly')
    response = polly.synthesize_speech(
        OutputFormat='mp3',
        Text=speak,
        TextType= 'text',
        VoiceId='Raveena'
    )
    sound = response.get('AudioStream')
    mixer.init()
    #mixer.music.load('/home/pi/audio.mp3')
    mixer.music.load(sound)
    mixer.music.play()
    time.sleep(5)
    print("played")

if __name__ == '__main__':
    faceid = ""
    confidence = 0.0
    load_table_values()
    print ("Starting ...")
    args = get_args()
    client = get_rekognition_client()
    while (True):

        capturePicture()
        try: 
            with open("image.jpg", 'rb') as image:
                image_bytes = image.read()
                
                print ("Searching faces ...")
                response = client.search_faces_by_image(Image={'Bytes': image_bytes}, CollectionId=args.collection)
                #print (response)
                faceid = json.dumps(response["FaceMatches"][0]["Face"]["FaceId"])
                faceid = faceid.replace("\"", "")
                confidence = json.dumps(response["FaceMatches"][0]["Face"]["Confidence"])
                print ("Confidence is " + confidence)
                
                
                global faceMap
                if (confidence > 80 and faceid is not None):
                    #print ("Finding name for "+faceid)
                    identifiedPerson = faceMap[str(faceid)]
                    print (identifiedPerson + " "+ str(confidence))
                    
                    
                    #Trying to get emotion
                    print ("Getting facial emotion")
                    response1 = client.detect_faces(Image={'Bytes': image_bytes},Attributes=["ALL"])
                    print (response1)
                    emotion = json.dumps(response1["FaceDetails"][0]["Emotions"][0]["Type"])
                    print (emotion)
                    
                    
                    makePollyWelcome(identifiedPerson, emotion)
                    print ("Done")
        except:
            print("Face detection error:", sys.exc_info()[0])
            pass
        time.sleep(5)
