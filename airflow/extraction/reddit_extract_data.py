from importlib.metadata import PathDistribution
import praw
import sys
import pathlib
import pandas as pd
import numpy as np
import configparser
from datetime import datetime
from validation import validate_input

# Read Configuration File
parser = configparser.ConfigParser()
script_path = pathlib.Path(__file__).parent.resolve()
config_file = "configuration.conf"
parser.read(f"{script_path}/{config_file}")

#Configuration variables
CLIENT_ID = parser.get('reddit_config', 'client_id')
SECRET = parser.get('reddit_config', 'secret')

# Options for extracting data from PRAW
SUBREDDIT = 'dataengineering'
TIME_FILTER = 'day'
LIMIT = None

#Fields to extract from Reddit.
FIELDS = ('id', 'title', 'score', 'author', 'num_comments', 
               'created_utc', 'url', 'upvote_ratio', 'over_18', 'edited', 
               'spoiler', 'stickied')

try:
    output_name = sys.argv[1]
except Exception as e:
    print(f"Error with file input. Error: {e}")
    sys.exit(1)
date_dag_run = datetime.strptime(output_name, "%Y-%m-%d")

def main():
    '''
    Extracts data from Reddit and load to csv
    '''
    validate_input(output_name)
    reddit_instance = connect()
    if reddit_instance:
        print('Successfully connected to Reddit')
    posts_object = get_subreddit_object(reddit_instance)
    extracted_data = extract_data(posts_object)
    transformed_data  = transform_data(extracted_data)
    load_to_csv(transformed_data)
    
def connect():
    '''
    connect to Reddit API
    '''
    try:
        reddit_instance = praw.Reddit(client_id=CLIENT_ID, client_secret=SECRET, user_agent="my user agent")
        return reddit_instance
    except Exception as e:
        print(f'Unable to connect to API. Error: {e}')
        sys.exit(1)
        
def get_subreddit_object(instance):
    '''
    Extract posts using reddit instance
    '''
    try:
        subreddit = instance.subreddit(SUBREDDIT)
        posts = subreddit.top(time_filter = TIME_FILTER, limit = LIMIT)
        return posts
    except Exception as e:
        print('Unable to extract posts from {SUBREDDIT}. Error: {e}')
        sys.exit(1)

def extract_data(posts):
    '''
    Extract posts data to pandas dataframe
    '''
    list_of_posts = []
    try:
        for submission in posts:
            to_dict = vars(submission)
            sub_dict = {field: to_dict[field] for field in FIELDS}
            list_of_posts.append(sub_dict)
        #print(list_of_posts)
        data = pd.DataFrame(list_of_posts)
        return data
    except Exception as e:
        print('Unable to extract data to dataframe. Error: {e}')
        
def transform_data(data):
    data["created_utc"] = pd.to_datetime(data["created_utc"], unit="s")
    data['edited'] = np.where(data['edited'] == 'False', False, True).astype(bool)
    return data

def load_to_csv(data):
    data.to_csv(f'tmp/{output_name}.csv', index = False)


if __name__== "__main__":
    main()
    