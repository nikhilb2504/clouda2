import boto3
import json

def load_music(musicList, dynamodb=None):
    
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table('music')

    for music in musicList['songs']:
        title = music['title']
        artist = music['artist']
        year = int(music['year'])
        web_url = music['web_url']
        image_url = music['img_url']
        
        print("Adding Music : ",title," by ",artist,", year : ",year)
        table.put_item(Item=music)

if __name__ == '__main__':
    with open("a2.json") as json_file:
        music_list = json.load(json_file)
    load_music(music_list)