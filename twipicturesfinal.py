import tweepy
from tweepy import OAuthHandler
import json
import os
import urllib.request
import io

consumer_key = ""
consumer_secret = ""
access_token = ""
access_secret = ""


@classmethod
def parse(cls, api, raw):
    status = cls.first_parse(api, raw)
    setattr(status, 'json', json.dumps(raw))
    return status


# Status() is the data model for a tweet
tweepy.models.Status.first_parse = tweepy.models.Status.parse
tweepy.models.Status.parse = parse
# User() is the data model for a user profil
tweepy.models.User.first_parse = tweepy.models.User.parse
tweepy.models.User.parse = parse
# You need to do it for all the models you need

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth)

tweets = api.user_timeline(screen_name='TreaclyR',
                           count=200, include_rts=False,
                           exclude_replies=True)

last_id = tweets[-1].id

while (True):
    more_tweets = api.user_timeline(screen_name='TreaclyR',
                                    count=200,
                                    include_rts=False,
                                    exclude_replies=True,
                                    max_id=last_id - 1)
    # There are no more tweets
    if (len(more_tweets) == 0):
        break
    else:
        last_id = more_tweets[-1].id - 1
        tweets = tweets + more_tweets

media_files = set()
for status in tweets:
    media = status.entities.get('media', [])
    if(len(media) > 0):
        media_files.add(media[0]['media_url'])

num=0
for media_file in media_files:
    save_name = 'img%03d.jpg'%num
    urllib.request.urlretrieve(media_file,save_name)
    num = num + 1

os.popen('ffmpeg -r 0.5 -i img%03d.jpg -vf scale=500:500 -y -r 30 -t 60 out.mp4')

from google.cloud import vision
from google.cloud.vision import types
from PIL import Image, ImageDraw, ImageFont

# Instantiates a client
client = vision.ImageAnnotatorClient()

path = './'
filelist = os.listdir(path)
total_num = len(filelist)

for file in filelist:
    if file.endswith('.jpg'):
        with io.open(file, 'rb') as image_file:
            content = image_file.read()

        image = types.Image(content=content)

        response = client.label_detection(image=image)
        labels = response.label_annotations

        # Add label to image
        img = Image.open(file)
        draw = ImageDraw.Draw(img)

        # print(file)
        # print('Labels:')
        labelword = ''
        for label in labels:
            labelword += str(label.description)+'\n'

        # print(labelword)
        (w, h) = img.size
        ttfont = ImageFont.truetype("/Library/Fonts/Arial.ttf", 30)
        draw.text((w/2-100, h/2-100), labelword, fill=(255, 255, 255), font=ttfont)
        img.save(file)
