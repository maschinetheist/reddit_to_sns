#!/usr/bin/env python
'''
Parse subreddits for new submissions matching the search string and then
Send an AWS SNS message. This lambda function is best matched with a CloudWatch
Event Rule trigger set to rate(1 hour).

.. todo::
   - Figure out if we can bypass feeding in Reddit API client_id/client_secret
   - Write a bootstrapping script which will package praw4 for us

.. moduleauthor:: Mike Pietruszka <mike@mpietruszka.com>
'''

import boto3
import praw
import logging
from datetime import datetime, timedelta
from dateutil import tz

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def reddit_to_sns(event, context):
    '''
    reddit_to_sns lambda function

    :param event:       pass lambda event parameter data that consists of:
                        - awsregion
                        - telephone number
                        - subreddits
                        - search string
                        - reddit API client_id
                        - reddit API client secret
    :param context:     runtime information of lambda function
    :return:            list of found submissions
    :rtype:             list
    '''
    awsregion = event['awsregion']
    tel_number = event['tel_number']
    subreddits = event['subreddits']
    searchstring = event['search_string']
    reddit_client_id = event['client_id']
    reddit_cilent_secret = event['client_secret']

    list_of_subreddits = []
    found_threads = []

    # Set "last hour" object
    last_hour = datetime.utcnow() - timedelta(hours=1)

    # Instantiate Reddit objects
    r = praw.Reddit(client_id='',
                    client_secret='',
                    user_agent='reddit_to_sns_get_posts')
    sns = boto3.client('sns', region_name=awsregion)

    if isinstance(subreddits, list) is False:
        list_of_subreddits.append(subreddits)
    else:
        list_of_subreddits = subreddits

    for sub in list_of_subreddits:
        sub = sub.encode('ascii', 'ignore')
        for thread in r.subreddit(sub).new(limit=15):
            logger.info("Found thread containing the search string:", str(thread.title).lower())
            if string in str(thread.title).lower():
                created_time = datetime.utcfromtimestamp(thread.created_utc)
                if created_time > last_hour:
                    logger.info("Found a new Reddit thread")
                    message = "New Reddit thread has been posted: " + str(thread.title)
                    sns.publish(PhoneNumber=tel_number, Message=message)
                    found_threads.append(thread.id)

    if len(found_threads) >= 1:
        return found_threads
