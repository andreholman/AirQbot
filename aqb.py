# coding=UTF-8

import requests
import datetime
import config
from BeautifulSoup import BeautifulSoup

print("Running with API KEY: " + config.api())
print("Press CTRL+C to quit. WARNING! Only messages received within 60 seconds of restart will be parsed.")

class BotHandler:

    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def get_updates(self, offset=None, timeout=30):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        resp = requests.get(self.api_url + method, params)
        if resp.json() != []:
            result_json = resp.json()['result']
            return result_json
        else:
            return False

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def get_last_update(self):
        get_result = self.get_updates()
        if get_result != []:
            if len(get_result) > 0:
                last_update = get_result[-1]
            else:
                last_update = get_result[len(get_result)-1]
            return last_update
        else:
            return False

aq_bot = BotHandler(config.api())
greetings = ('hello', 'hi', 'greetings', 'sup')
now = datetime.datetime.now()


def main():
    new_offset = None
    today = now.day
    hour = now.hour

    while True:
        aq_bot.get_updates(new_offset)

        last_update = aq_bot.get_last_update()

        if last_update != False:
            last_update_id = last_update['update_id']
            last_chat_text = last_update['message']['text']
            last_chat_id = last_update['message']['chat']['id']
            last_chat_name = last_update['message']['chat']['first_name']

            print("From {}: ".format(last_chat_name) + last_chat_text)

            if last_chat_text.lower() in greetings and today == now.day and 6 <= hour < 12:
                aq_bot.send_message(last_chat_id, 'Good Morning, {}'.format(last_chat_name))
                today += 1
            elif last_chat_text.lower() in greetings and today == now.day and 12 <= hour < 17:
                aq_bot.send_message(last_chat_id, 'Good Afternoon, {}'.format(last_chat_name))
                today += 1
            elif last_chat_text.lower() in greetings and today == now.day and 17 <= hour < 23:
                aq_bot.send_message(last_chat_id, 'Good Evening, {}'.format(last_chat_name))
                today += 1

            elif last_chat_text.lower() == "ping":
                aq_bot.send_message(last_chat_id, 'pong')
            elif last_chat_text.lower() == "test":
                aq_bot.send_message(last_chat_id, '👍')

            elif last_chat_text == "/start" or last_chat_text == "/help":
                aq_bot.send_message(last_chat_id, 'Hello!\nTo get the current air quality, send the zipcode and I will send you the Air Quality Index and overall healthiness of the air.')
            elif last_chat_text == "/contact":
                aq_bot.send_message(last_chat_id, 'Questions or comments? Contact my maker, @realhuashan')

            else: # Scrape and send
                response = requests.get("https://airnow.gov/index.cfm?action=airnow.local_city&zipcode={}&submit=go".format(last_chat_text))
                soup = BeautifulSoup(response.content)
                slew = soup.findAll('table', attrs={'class': 'TblInvisible'})
                if slew != []:
                    aqi = slew[1].text
                    aqt = soup.find('table', attrs={'class': 'TblInvisible'}).text.replace(aqi, "").lower()
                    aq_bot.send_message(last_chat_id, 'The AQI for {} is <b>{}</b>.\nThe air quality is {}.'.format(last_chat_text, aqi, aqt))
                    print("Sent data to {} ({}).".format(last_chat_name, last_chat_id))
                else:
                    aq_bot.send_message(last_chat_id, 'Sorry, the zipcode <i>{}</i> is invalid, or has no data.'.format(last_chat_text))
                    print("Sent err/warn to {} ({}).".format(last_chat_name, last_chat_id))
            new_offset = last_update_id + 1

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("")
        print("QUITTING")
        print("")
        exit()