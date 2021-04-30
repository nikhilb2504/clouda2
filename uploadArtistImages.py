import json
import boto3
import requests

def artist_image_upload(musicList):

    s3 = boto3.resource('s3')
    
    for music in musicList['songs']:
        img_url = music['img_url']
        artist = music['artist']
        title = music['title']
        img_url = music['img_url']

        key= img_url.split('/')[::-1][0]

        imageRequest = requests.get(img_url, stream=True)
        fileObject = imageRequest.raw
        requestData = fileObject.read()
        s3.Bucket('s3838330cloudassgn2-artists-images').put_object(Key=key, Body=requestData)

        print("Uploading image: ",img_url," by ",artist," title : ",title)

if __name__ == '__main__':

    with open("a2.json") as jsonFile:
        musicList = json.load(jsonFile)
    artist_image_upload(musicList)