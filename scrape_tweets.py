import twitter
import os
import json
import gzip
import shutil
from dotenv import load_dotenv
load_dotenv()

def get_tweets(screen_name=None):
    api = twitter.Api(consumer_key=os.getenv('TWITTER_CONSUMER_KEY'),
        consumer_secret=os.getenv('TWITTER_CONSUMER_SECRET'),
        access_token_key=os.getenv('TWITTER_ACCESS_TOKEN'),
        access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    )
    timeline = api.GetUserTimeline(screen_name=screen_name, count=200)
    earliest_tweet = min(timeline, key=lambda x: x.id).id
    print("getting tweets before:", earliest_tweet)

    while True:
        tweets = api.GetUserTimeline(
                screen_name=screen_name, max_id=earliest_tweet, count=200
                )
        new_earliest = min(tweets, key=lambda x: x.id).id

        if not tweets or new_earliest == earliest_tweet:
            break
        else:
            earliest_tweet = new_earliest
            print("getting tweets before:", earliest_tweet)
            timeline += tweets

    return timeline


if __name__ == "__main__":
    screen_name = "disneyplus"
    all_tweets = get_tweets(screen_name)
    all_tweets_json = list(map(lambda tweet: tweet._json, all_tweets))
    with open('all_raw_tweets.json', 'w+') as f:
        f.write(json.dumps(all_tweets_json))
    with open('all_raw_tweets.json', 'rb') as f_in:
        with gzip.open('all_raw_tweets.json.gz', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

