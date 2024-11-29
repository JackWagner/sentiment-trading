# get web scraper
from scrapers.web_scraper import WebScraper

# import channel IDs and authorizaton
from os import path
from json import load

# temporary local user config
homedir          = path.expanduser('~')
discord_user_conf = open(path.join(homedir,'.config/sst/discord_channels.json'),'r')
discord_user      = load(discord_user_conf, strict=False)

class Channel(WebScraper):
    def __init__(self, channel_id):
        self.url = f'https://discord.com/api/v9/channels/{channel_id}'
        self.headers = {
            'authorization': discord_user.get("authorization")
        }
        super().__init__(self.url, self.headers)

    def get_messages(self):
        '''
        Returns df (message_time, message_contents) of messages over [start,end]
        '''
        html = self.get_html()
        soup = self.parse_html(html)
        data = self.extract_data(soup)
        return data
