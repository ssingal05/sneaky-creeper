#This module written by Gabriel Butterick and Bonnie Ishiguro

from twython import Twython, TwythonError
import time

################### Attributes ###################

description = "Posts data to Twitter as a series of 140 character Tweets."

# TODO add optional params?
requiredParams = {
    'sending': {
       'key':'Application key for Twitter API.',
       'secret': 'Application secret for Twitter API.',
       'token': 'OAuth token for Twitter API.',
       'tsecret': 'OAuth token secret for Twitter API.',
       'name': 'Screen name of Twitter account to post data to.'
               },
    'receiving': {
       'key':'Application key for Twitter API.',
       'secret': 'Application secret for Twitter API.',
       'token': 'OAuth token for Twitter API.',
       'tsecret': 'OAuth token secret for Twitter API.',
       'name': 'Screen name of Twitter account to post data to.'
                 }
    }

maxLength = 140

maxHourly = 100
# Can only post 100 times per hour or 1000 times per day

################### Functions ###################

def send(data, params):
    APP_KEY = params['key']
    APP_SECRET = params['secret']
    OAUTH_TOKEN = params['token']
    OAUTH_TOKEN_SECRET = params['tsecret']
    SCREEN_NAME = params['name']

    twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

    twitter.update_status(status=data)

    return

def receive(params):
    APP_KEY = params['key']
    APP_SECRET = params['secret']
    OAUTH_TOKEN = params['token']
    OAUTH_TOKEN_SECRET = params['tsecret']
    SCREEN_NAME = params['name']

    twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    try:
        user_timeline = twitter.get_user_timeline(screen_name=SCREEN_NAME)
    except TwythonError as e:
        print(e)

    tweets = []
    for x in user_timeline:
        if 'text' in x:
            tweets.append(x['text'])

    return tweets

