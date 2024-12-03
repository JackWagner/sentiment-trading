from twikit import Client
from os import path
import json
import pandas as pd
import asyncio

# temporary local user config
homedir          = path.expanduser('~')
twitter_user_conf = open(path.join(homedir,'.config/sst/twitter_user.json'),'r')
twitter_user      = json.load(twitter_user_conf, strict=False)

client = Client("en-US")

cookies = []
path_to_cookies = path.join(homedir,'.config/sst/twitter_cookies.json')
with open(path_to_cookies,'r') as file:
    cookies = json.load(file)

cookies_formatted = {}
for cookie in cookies:
    cookies_formatted[cookie["name"]] = cookie["value"]

## You can comment this `login`` part out after the first time you run the script (and you have the `cookies.json`` file)
async def scrape_user(handle):
    client.set_cookies(cookies_formatted)

    # get coroutine
    coro = client.get_user_by_screen_name(handle)
    _client = await coro
    tweets = client.get_tweets('Tweets', count=5)

    tweets_to_store = []
    for tweet in tweets:
        tweets_to_store.append({
            'created_at': tweet.created_at,
            'favorite_count': tweet.favorite_count,
            'full_text': tweet.full_text,
        })

    # We can make the data into a pandas dataframe and store it as a CSV file
    df = pd.DataFrame(tweets_to_store)
    df.to_csv(path.join(homedir,f'data/{handle}_tweets.csv'), index=False)

    # Pandas also allows us to sort or filter the data
    print(df.sort_values(by='favorite_count', ascending=False))

    # We can also print the data as a JSON object
    print(json.dumps(tweets_to_store, indent=4))

asyncio.run(scrape_user('elonmusk'))
