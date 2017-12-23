#!C:\Python27\python.exe
# -*- coding: utf-8 -*-

import json
import urllib2


class Senero(object):
    ADMINS = ['YOUR_TELEGRAM_USERNAME']
    COINS = ['usd', 'eur']
    VALID_CHATS = ['YOUR_CHAT_ID']

    def __init__(self, location):
        self.location = location
        f = open(self.location, 'r')
        self.data = json.loads(f.read())
        self.users = self.data['users']
        f.close()

    def save_file(self):
        f = open(self.location, 'w+')
        f.write(json.dumps(self.data, sort_keys=True, indent=4, separators=(',', ': ')))
        f.close()

    def is_admin(self, message):
        return message.from_user.username in self.ADMINS

    def user_id_by_name(self, user_name):
        user_id = None
        for user in self.users:
            user = self.users[user]
            if user['username'] is not None and user_name == '@' + user['username']:
                user_id = user['id']
                break
        return user_id

    def add_points(self, user_id, points, message):
        for i in range(int(points)):
            self.users[user_id]['addedUsers'].append({'AddedBySystem': message})

    def reduce_points(self, user_id, points):
        self.users[user_id]['addedUsers'] = self.users[user_id]['addedUsers'][
                                            :len(self.users[user_id]['addedUsers']) - int(points)
                                            ]

    def get_points(self, message):
        user_id = str(message.from_user.id)
        if str(user_id) in self.users:
            if 'addedUsers' not in self.users[user_id]:
                self.users[user_id]['addedUsers'] = []
                self.save_file()
            return len(self.users[user_id]['addedUsers'])
        else:
            self.users[user_id] = Senero.user_to_json(message.from_user)
            self.save_file()
        return 0

    def ensure_user(self, message):
        if str(message.from_user.id) not in self.users:
            self.users[str(message.from_user.id)] = Senero.user_to_json(message.from_user)
        if 'addedUsers' not in self.users[str(message.from_user.id)]:
            self.users[str(message.from_user.id)]['addedUsers'] = []
        self.save_file()

    @staticmethod
    def symbol_to_id(users_len, *coin_symbols):
        response = urllib2.urlopen('https://api.coinmarketcap.com/v1/ticker/?convert=EUR&limit=0').read()
        coins = json.loads(response)
        current_coin = {}
        for coin_symbol in coin_symbols:
            if coin_symbol.lower() in Senero.COINS:
                current_coin[coin_symbol.lower()] = {'name': coin_symbol.upper()}
            elif 'senero' == coin_symbol.lower():
                price_usd = 1
                price_usd += 0.05 * int(users_len / 100)
                current_coin['senero'] = {'id': 'senero', 'name': 'Senero', 'price_usd': price_usd}
            else:
                for coin in coins:
                    if coin_symbol.lower() == coin['symbol'].lower() or coin_symbol.lower() == coin['id']:
                        current_coin[coin_symbol.lower()] = coin
                        break
        return current_coin

    @staticmethod
    def user_to_json(user):
        if user is None:
            return None
        if user.is_bot:
            # We don't want to count bots!
            return None
        result = {
            'id': str(user.id),
            'is_bot': user.is_bot,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username
        }
        return result

    @staticmethod
    def extract_args(arg):
        return arg.split()[1:]

    @staticmethod
    def is_valid_chat(message):
        return str(message.chat.id) in Senero.VALID_CHATS
