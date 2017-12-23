#!C:\Python27\python.exe
# -*- coding: utf-8 -*-

from SeneroBot import Senero
from telebot import types
import argparse
import telebot
import json
import urllib2
import time
import datetime
import numbers
import os
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


# Parse args
parser = argparse.ArgumentParser(description='Telegram bot')
parser.add_argument('-token', '-t', help='Telegram API token', required=True)
parser.add_argument('-saveFile', help='Set the save file path', default='data.json')
args = parser.parse_args()
user_step = {}

print 'Made with <3 from Israel'
while True:
    try:
        senero = Senero(args.saveFile)
        bot = telebot.TeleBot(args.token)
        print 'Starting bot'

        def listener(messages):
            for m in messages:
                if not Senero.is_valid_chat(m):
                    continue
                adding_or_removing_user = Senero.user_to_json(m.from_user)
                added_user = Senero.user_to_json(m.new_chat_member)
                left_user = Senero.user_to_json(m.left_chat_member)
                if adding_or_removing_user is not None:
                    if added_user is not None:
                        # User added
                        print json.dumps(adding_or_removing_user) + ' added ' + json.dumps(added_user)
                        if adding_or_removing_user['id'] not in senero.users:
                            senero.users[adding_or_removing_user['id']] = adding_or_removing_user
                            senero.users[adding_or_removing_user['id']]['addedUsers'] = []
                        if added_user not in senero.users[adding_or_removing_user['id']]['addedUsers']:
                            senero.users[adding_or_removing_user['id']]['addedUsers'].append(added_user)
                        if added_user['id'] not in senero.users:
                            senero.users[added_user['id']] = added_user
                            senero.users[added_user['id']]['addedUsers'] = []
                        senero.save_file()
                        bot.send_message(m.chat.id, 'Senero Community Token Bot: Welcome ' + added_user['first_name'] +
                                         '! Type /help to see how you can earn some tokens for helping Senero')
                if left_user is not None:
                    # User left or removed
                    print json.dumps(left_user) + ' left or removed'
                    for user in senero.users:
                        senero.users[user]['addedUsers'].remove(left_user)
                        senero.save_file()


        @bot.message_handler(commands=['rewards'])
        def rewards(message):
            if not Senero.is_valid_chat(message):
                bot.reply_to(message, 'This bot is only available for group https://t.me/senero')
                return
            senero.ensure_user(message)
            txt = ''
            for item in senero.users:
                item = senero.users[item]
                if 'addedUsers' not in item or 0 == len(item['addedUsers']):
                    continue
                if item['username'] is not None:
                    txt += item['username'] + ' - '
                if item['first_name'] is not None:
                    txt += item['first_name'] + ' '
                if item['last_name'] is not None:
                    txt += item['last_name'] + ' '
                txt += ' added ' + str(len(item['addedUsers'])) + ' user(s)\n'
            bot.reply_to(message, txt)


        @bot.message_handler(commands=['learn'])
        def learn(message):
            if not Senero.is_valid_chat(message):
                bot.reply_to(message, 'This bot is only available for group https://t.me/senero')
                return
            senero.ensure_user(message)
            bot.send_message(message.chat.id, 'Read Reddit posts on '
                                              '<a href="https://www.reddit.com/r/Senero/">Reddit</a>\n'
                                              'Hear Senero tweets on '
                                              '<a href="https://twitter.com/coinsenero">Twitter</a>\n'
                                              'Read our '
                                              '<a href="http://senero.org/senero.pdf">Yellow paper</a>\n'
                                              'Read our '
                                              '<a href="https://trello.com/b/aDTYufzK/senero-roadmap">Road map</a>\n'
                                              'Read Senero articles on '
                                              '<a href="https://medium.com/@senerocoin">Medium</a>\n'
                                              'Read our news and updates on '
                                              '<a href="http://senero.org/blog/">our blog</a>\n',
                             parse_mode='HTML', disable_web_page_preview=True)


        @bot.message_handler(commands=['media'])
        def media(message):
            if not Senero.is_valid_chat(message):
                bot.reply_to(message, 'This bot is only available for group https://t.me/senero')
                return
            senero.ensure_user(message)
            bot.send_message(message.chat.id,
                             'https://www.huffingtonpost.com/entry/everything-you-need-to-know-about-cryptocurrency'
                             '-scalability_us_5a3a9310e4b0df0de8b06188')


        @bot.message_handler(commands=['PM', 'pm'])
        def pm(message):
            senero.ensure_user(message)
            if 'step_pm' not in senero.users[str(message.from_user.id)]:
                senero.users[str(message.from_user.id)]['step_pm'] = 'answer_pm'
                bot.send_message(message.from_user.id, 'Hi, Senero rewards its best, loyal, community with airdrops, '
                                                       'you will recieve 1 token for replying and '
                                                       'saying "Hi Senero Community Token Bot"')
                senero.save_file()
            else:
                bot.reply_to(message, 'You already did or you are already in the process of the tutorial')


        @bot.message_handler(commands=['earn'])
        def earn(message):
            if not Senero.is_valid_chat(message):
                bot.reply_to(message, 'This bot is only available for group https://t.me/senero')
                return
            senero.ensure_user(message)
            bot.reply_to(message, '* 1 point - for every user invited to this chat by you\n* 1 point - follow '
                                  '<a href="https://twitter.com/coinsenero">our twitter page</a> '
                                  'and tweet your telegram '
                                  'username to @<a href="https://twitter.com/coinsenero">coinsenero</a> on twitter '
                                  'with hash tag #senero, For example:\n'
                                  '@coinsenero Search for #senero ! The big next thing, from @senero_bot on Telegram\n'
                                  '* Chat to Senero Community Token /PM (you can get free tokens!)',
                         parse_mode='HTML', disable_web_page_preview=True)


        @bot.message_handler(commands=['myranking'])
        def own_rank(message):
            if not Senero.is_valid_chat(message):
                bot.reply_to(message, 'This bot is only available for group https://t.me/senero')
                return
            senero.ensure_user(message)
            bot.reply_to(message, 'You currently have ' + str(senero.get_points(message)) + ' point(s)')


        @bot.message_handler(commands=['slap'])
        def slap(message):
            if not Senero.is_valid_chat(message):
                bot.reply_to(message, 'This bot is only available for group https://t.me/senero')
                return
            senero.ensure_user(message)
            status = Senero.extract_args(message.text)
            if message.from_user.username is not None:
                if '@senero_bot' == status[0].lower():
                    bot.send_message(message.chat.id, '@senero_bot slaps @' + str(message.from_user.username))
                    return
                bot.send_message(message.chat.id, '@' + str(message.from_user.username) + ' slaps ' + status[0])
            else:
                if '@senero_bot' == status[0].lower():
                    bot.send_message(message.chat.id, '@senero_bot slaps ' + str(message.from_user.first_name))
                    return
                bot.send_message(message.chat.id, '@' + str(message.from_user.first_name) + ' slaps ' + status[0])


        @bot.message_handler(commands=['mybet'])
        def my_bet(message):
            if not Senero.is_valid_chat(message):
                bot.reply_to(message, 'This bot is only available for group https://t.me/senero')
                return
            senero.ensure_user(message)
            user_id = str(message.from_user.id)
            if user_id in senero.users and 'bet' in senero.users[user_id] and senero.users[user_id]['bet']['inBet']:
                st = datetime.datetime.fromtimestamp(int(senero.users[user_id]['bet']['at']) / 1000)
                week = datetime.timedelta(days=1)
                delta = st + week
                find = (delta - datetime.datetime(1970, 1, 1)).total_seconds() * 1000
                response = urllib2.urlopen('https://graphs.coinmarketcap.com/'
                                           'currencies/' + senero.users[user_id]['bet']['oncoin'] + '/').read()
                history = json.loads(response)
                new_val = None
                for item in history['market_cap_by_available_supply']:
                    if find <= item[0]:
                        new_val = item[1]
                        break
                if new_val is None:
                    bot.send_message(message.chat.id, 'Betting (%s points) for %s\n'
                                                      'Market cap at the time of bet: %s$ (predict: %s)'
                                     % (
                                         str(senero.users[user_id]['bet']['points']),
                                         senero.users[user_id]['bet']['oncoin'],
                                         '{:,}'.format(int(
                                             str(senero.users[user_id]['bet']['current_value']).split('.')[0]
                                         )),
                                         senero.users[user_id]['bet']['status']
                                     ))
                else:
                    if (new_val >= int(str(senero.users[user_id]['bet']['current_value']).split('.')[0])
                        and 'higher' == senero.users[user_id]['bet']['status']) \
                            or \
                            (new_val <= int(str(senero.users[user_id]['bet']['current_value']).split('.')[0])
                             and 'lower' == senero.users[user_id]['bet']['status']):
                        # Win
                        bot.send_message(message.chat.id, 'You won the bet!')
                        senero.add_points(user_id, senero.users[user_id]['bet']['points'], 'For Wining bet')
                    else:
                        # Lose
                        senero.reduce_points(user_id, senero.users[user_id]['bet']['points'])
                    senero.users[user_id]['bet']['inBet'] = False
                    senero.save_file()
            else:
                bot.send_message(message.chat.id, 'You don\'t have active bet\n/bet to start a new bet')


        @bot.message_handler(commands=['cancelbet'])
        def cancel_bet(message):
            if not Senero.is_valid_chat(message):
                bot.reply_to(message, 'This bot is only available for group https://t.me/senero')
                return
            senero.ensure_user(message)
            user_id = str(message.from_user.id)
            if user_id not in senero.users:
                senero.users[user_id] = message.from_user
            if 'bet' in senero.users[user_id] and senero.users[user_id]['bet']['inBet']:
                if time.time() - senero.users[user_id]['bet']['at'] / 1000 > 600:
                    bot.send_message(message.chat.id, '10 minutes passed')
                else:
                    senero.users[user_id]['bet']['inBet'] = False
                    bot.send_message(message.chat.id, 'Bet canceled')
            else:
                bot.send_message(message.chat.id, 'You don\'t have active bet')
            senero.save_file()


        @bot.message_handler(commands=['convert'])
        def convert(message):
            if not Senero.is_valid_chat(message):
                bot.reply_to(message, 'This bot is only available for group https://t.me/senero')
                return
            senero.ensure_user(message)
            bot.send_chat_action(message.chat.id, 'typing')
            status = Senero.extract_args(message.text)
            if 3 == len(status) and isinstance(float(status[0]), numbers.Real):
                status[1] = status[1].lower()
                status[2] = status[2].lower()
                coins = Senero.symbol_to_id(int(bot.get_chat_members_count(message.chat.id)), status[1], status[2])
                if coins is {} or 2 != len(coins):
                    bot.send_message(message.chat.id, 'Unknown coin(s)')
                else:
                    if status[1] in Senero.COINS and status[2] in Senero.COINS:
                        bot.reply_to(message, 'It\'s cryptocurrency converter, why would you want to do that?')
                        return
                    if status[2] in Senero.COINS:
                        value_rate = float(coins[status[1]]['price_' + status[2].lower()]) * float(status[0])
                    elif status[1] in Senero.COINS:
                        value_rate = (1 / float(coins[status[2]]['price_' + status[1].lower()])) * float(status[0])
                    else:
                        value_rate = (float(coins[status[1]]['price_usd']) / float(
                            coins[status[2]]['price_usd'])) * float(status[0])
                    value_rate = ('%.8f' % float(value_rate))
                    value_rate = value_rate.rstrip('0').rstrip('.') if '.' in value_rate else value_rate

                    bot.reply_to(message, str(status[0]) + ' ' + coins[status[1]]['name'] +
                                 ' is ' + value_rate + status[2])
            else:
                bot.reply_to(message, 'Invalid command format\n/help for more information')


        @bot.message_handler(commands=['info'])
        def info(message):
            if not Senero.is_valid_chat(message):
                bot.reply_to(message, 'This bot is only available for group https://t.me/senero')
                return
            senero.ensure_user(message)
            bot.send_chat_action(message.chat.id, 'typing')
            status = Senero.extract_args(message.text)
            if 1 == len(status):
                status[0] = status[0].lower()
                if status[0] in Senero.COINS:
                    bot.send_message(message.chat.id, 'Only cryptocurrency)')
                    return
                coin = Senero.symbol_to_id(int(bot.get_chat_members_count(message.chat.id)), status[0])
                if coin is {} or 1 != len(coin):
                    bot.send_message(message.chat.id, 'Unknown coin(s)')
                else:
                    coin = coin[status[0]]
                    txt = '<b>' + coin['name'] + ':</b>\n'
                    txt += 'Symbol: ' + coin['symbol'] + '\n'
                    txt += 'Price: ' + coin['price_usd'] + '$ / ' + coin['price_eur'] \
                           + '€ / '.decode('utf8') + coin['price_btc'] + 'BTC\n'
                    txt += '24 Hours value: ' + coin['24h_volume_usd'] + '$ / ' \
                           + coin['24h_volume_eur'] + '€\n'.decode('utf8')
                    txt += 'Market cap: ' + coin['market_cap_usd'] + '$ / ' \
                           + coin['market_cap_eur'] + '€\n'.decode('utf8')
                    txt += '<i>Change:</i>\n'
                    txt += 'Last 1 hour: ' + coin['percent_change_1h'] + '%\n'
                    txt += 'Last 24 hours: ' + coin['percent_change_24h'] + '%\n'
                    txt += 'Last 7 days: ' + coin['percent_change_7d'] + '%\n'
                    bot.reply_to(message, txt, parse_mode='HTML')
            else:
                bot.reply_to(message, 'Invalid command format\n/help for more information')


        @bot.message_handler(commands=['registerme', 'addme'])
        def add_user_to_db(message):
            if not Senero.is_valid_chat(message):
                bot.reply_to(message, 'This bot is only available for group https://t.me/senero')
                return
            senero.ensure_user(message)
            bot.reply_to(message, 'Added')


        @bot.message_handler(commands=['award', 'reward'])
        def award(message):
            if not Senero.is_valid_chat(message):
                bot.reply_to(message, 'This bot is only available for group https://t.me/senero')
                return
            senero.ensure_user(message)
            status = Senero.extract_args(message.text)
            if senero.is_admin(message):
                if 2 == len(status) and status[1].isdigit():
                    user_id = senero.user_id_by_name(status[0])
                    if user_id is None:
                        bot.reply_to(message, 'User not found\nAsk '
                                     + status[0] + ' to write /addme and then try again')
                    else:
                        senero.add_points(user_id, status[1], 'By admin')
                        bot.reply_to(message, 'Added ' + str(status[1]) + ' point(s) for ' + status[0])
                        senero.save_file()
                else:
                    bot.reply_to(message, 'Invalid command format\n/help for more information')
            else:
                bot.reply_to(message, 'Sorry, but you are not an admin!')


        @bot.message_handler(commands=['reduce'])
        def reduce_points(message):
            if not Senero.is_valid_chat(message):
                bot.reply_to(message, 'This bot is only available for group https://t.me/senero')
                return
            senero.ensure_user(message)
            status = Senero.extract_args(message.text)
            if senero.is_admin(message):
                if 2 == len(status) and status[1].isdigit():
                    user_id = senero.user_id_by_name(status[0])
                    if user_id is None:
                        bot.reply_to(message, 'User not found\nAsk ' + status[0]
                                     + ' to write /addme and then try again')
                    else:
                        senero.reduce_points(user_id, status[1])
                        bot.reply_to(message, 'Reduced ' + str(status[1]) + ' point(s) for ' + status[0])
                        senero.save_file()
                else:
                    bot.reply_to(message, 'Invalid command format\n/help for more information')
            else:
                bot.reply_to(message, 'Sorry, but you are not an admin!')


        @bot.message_handler(commands=['bet'])
        def bet(message):
            if not Senero.is_valid_chat(message):
                bot.reply_to(message, 'This bot is only available for group https://t.me/senero')
                return
            senero.ensure_user(message)
            status = Senero.extract_args(message.text)
            user_id = str(message.from_user.id)
            if 3 == len(status) and status[1].isdigit() \
                    and ('higher' == status[2].lower() or 'lower' == status[2].lower()):
                max_points = senero.get_points(message)
                if int(status[1]) <= max_points:
                    if 0 < int(status[1]):
                        # Check coin symbol
                        coin_symbol = status[0]
                        current_coin = Senero.symbol_to_id(bot.get_chat_members_count(message.chat.id),
                                                           coin_symbol
                                                           )[coin_symbol.lower()]
                        if current_coin is {} or 0 == len(current_coin) or 'id' not in current_coin:
                            bot.send_message(message.chat.id, 'Unknown coin \'' + coin_symbol.upper() + '\'')
                        else:
                            if user_id not in senero.users:
                                senero.users[user_id] = Senero.user_to_json(message.from_user)
                                senero.users[user_id]['addedUsers'] = []
                            if 'bet' not in senero.users[user_id]:
                                senero.users[user_id]['bet'] = {'inBet': False}

                            if senero.users[user_id]['bet']['inBet']:
                                bot.send_message(message.chat.id, 'You already have an active bet!\n'
                                                                  '/mybet - See current bet status,'
                                                                  ' and see results if finished')
                            else:
                                senero.users[user_id]['bet']['inBet'] = True
                                senero.users[user_id]['bet']['oncoin'] = current_coin['id']
                                senero.users[user_id]['bet']['current_value'] = current_coin['market_cap_usd']
                                senero.users[user_id]['bet']['points'] = int(status[1])
                                senero.users[user_id]['bet']['status'] = status[2].lower()
                                senero.users[user_id]['bet']['at'] = int(time.time() * 1000)
                                bot.send_message(message.chat.id, 'Added bet (%s points) for %s\n'
                                                                  'Currnet market cap: %s$ (predict: %s)'
                                                 % (
                                                     status[1],
                                                     current_coin['name'],
                                                     '{:,}'.format(int(
                                                         str(current_coin['market_cap_usd']).split('.')[0]
                                                     )),
                                                     senero.users[user_id]['bet']['status']
                                                 ))
                                senero.save_file()
                    else:
                        bot.send_message(message.chat.id, 'Bet amount need to be larger then 0')
                else:
                    bot.send_message(message.chat.id, 'Insufficient points (' + str(max_points) + ' points available)')
            else:
                txt = '<i>This is a function that allow user to bet on Market Cap in 24 hours.</i>\n'
                txt += '\n<b>Rules:</b>\n'
                txt += '* All the coin values will be taken from: ' \
                       '<a href="https://coinmarketcap.com">coinmarketcap.com</a>\n'
                txt += '* You can cancel your bet only if 10 minutes are not passed since your bet order: /cancelbet\n'
                txt += '* Only one active bet per user is allowed\n'
                txt += '\n<b>Format:</b>\n<i>/bet *Coin Symbol* *How much points* *Higher/Lower*</i>\n'
                txt += 'For example if I have 7 points (/myranking) and I want to bet on ' \
                       '4 points that the value will be higher:\n'
                txt += '<i>/bet ltc 4 higher</i>\n'
                txt += 'Or:\n<i>/bet xmr 1 lower</i>\n'
                bot.send_message(message.chat.id, txt, parse_mode='HTML', disable_web_page_preview=True)


        @bot.message_handler(commands=['help'])
        def help(message):
            if not Senero.is_valid_chat(message):
                bot.reply_to(message, 'This bot is only available for group https://t.me/senero')
                return
            senero.ensure_user(message)
            bot.reply_to(message, '/help - Display this message\n'
                                  '/rewards - Show the user\'s points\n'
                                  '/ranking - Show top 10 users by points\n'
                                  '/myranking - Show my points\n'
                                  '/earn - Display a list of bounty tasks\n'
                                  '/learn - Learn about Senero\n'
                                  '/media - Show Senero mention on media'
                                  '/bet - create new bet\n'
                                  '/mybet - See current bet status, and see results if finished\n'
                                  '/cancelbet - Cancel a bet (Only if 10 minutes are not passed after placing a bet)\n'
                                  '/poll - Vote and create polls\n'
                                  '/info *SYMBOL* - Info about a coin'
                                  '/convert *NUMBER* *SYMBOL1* *SYMBOL2* - Convert value from 1 coin to another\n'
                                  'For example, see how much 1 Monero is in USD:\n'
                                  '/convert 1 XMR USD\n'
                                  'Or 500 EUR in Bitcoin\n'
                                  '/convert 500 EUR BTC\n'
                                  '\n'
                                  '<b>Admin only options</b>\n'
                                  '/reward *Username* *points* - Award user (need mention) with points, for example:\n'
                                  '/reward @senero_bot 2\n'
                                  'The opposite command:\n'
                                  '/reduce *Username* *points*\n',
                         parse_mode='HTML')
            if 'step_pm' in senero.users[str(message.from_user.id)] and \
                    'second_questions' == senero.users[str(message.from_user.id)]['step_pm']:
                bot.send_message(message.from_user.id, message.from_user.first_name + '  has 3 correct answers, ' +
                                 message.from_user.first_name + ' rewarded 1 token!!')
                senero.add_points(str(message.from_user.id), 1, 'PM')
                senero.users[str(message.from_user.id)]['step_pm'] = '3_questions'
                senero.save_file()
                bot.send_message(message.from_user.id, 'Awesome! Senero tokens will be valuable and there is NO LIMIT '
                                                       'to how many free tokens you can win. Go ahead invite users, '
                                                       'vote or bet your tokens. Thank you for joining our community. '
                                                       'God bless.')


        def get_key(item):
            return item[1]


        @bot.message_handler(commands=['ranking'])
        def ranking(message):
            if not Senero.is_valid_chat(message):
                bot.reply_to(message, 'This bot is only available for group https://t.me/senero')
                return
            senero.ensure_user(message)
            top_users = 10
            txt = 'Top ' + str(top_users) + ' users:\n\n'
            users_data = []
            for item in senero.users:
                if 'addedUsers' in senero.users[item]:
                    users_data.append([item, len(senero.users[item]['addedUsers'])])
            users_data = sorted(users_data, key=get_key, reverse=True)
            i = 0
            for item in users_data:
                if top_users == i:
                    break
                item = senero.users[item[0]]
                if item['username'] is not None:
                    txt += item['username'] + ' - '
                if item['first_name'] is not None:
                    txt += item['first_name'] + ' '
                if item['last_name'] is not None:
                    txt += item['last_name'] + ' '
                txt += ' added ' + str(len(item['addedUsers'])) + ' user(s)\n'
                i += 1

            bot.reply_to(message, txt)


        @bot.message_handler(commands=['poll'])
        def poll(message):
            if not Senero.is_valid_chat(message):
                bot.reply_to(message, 'This bot is only available for group https://t.me/senero')
                return
            status = Senero.extract_args(message.text)
            if 0 == len(status):
                senero.ensure_user(message)
                options_select = types.ReplyKeyboardMarkup(one_time_keyboard=True)
                options_select.add('/newpoll', '/deletepoll', '/polls', 'Cancel')
                bot.send_message(message.chat.id, '<b>Poll manager</b>\n'
                                                  '/newpoll - Create new poll '
                                                  '(admin only - remove last poll for user)\n'
                                                  '/deletepoll - Delete the user poll (admin only)\n'
                                                  '/polls - See current polls',
                                 parse_mode='HTML', reply_markup=options_select)
            else:
                if status[0] in senero.data['polls']:
                    poll_obj = senero.data['polls'][status[0]]['poll']
                    votes = []
                    index = 1
                    for option in poll_obj['options']:
                        if 'text' == option['type']:
                            votes.append('/vote ' + str(index) + ' ' + status[0])
                            bot.send_message(message.chat.id, 'Option number ' + str(index) + ':\n'
                                             + option['val'] + '(' + str(option['votes']) + ' votes)')
                        elif 'image' == option['type']:
                            votes.append('/vote ' + str(index) + ' ' + status[0])
                            bot.send_photo(message.chat.id, open(option['val'], 'rb'),
                                           caption='Option number ' + str(index)
                                                   + '(' + str(option['votes']) + ' votes)')
                        index += 1

                    votes.append('Cancel')
                    options_select = types.ReplyKeyboardMarkup(one_time_keyboard=True)
                    options_select.add(*votes)
                    bot.send_message(message.chat.id, 'Choose an option', reply_markup=options_select)
                else:
                    bot.reply_to(message, 'Unknown poll')


        @bot.message_handler(commands=['vote'])
        def vote(message):
            if not Senero.is_valid_chat(message):
                bot.reply_to(message, 'This bot is only available for group https://t.me/senero')
                return
            status = Senero.extract_args(message.text)
            if 2 == len(status) and status[0].isdigit() and status[1].isdigit():
                if status[1] in senero.data['polls'] and \
                        int(status[0]) <= len(senero.data['polls'][status[1]]['poll']['options']):

                    if str(message.from_user.id) not in senero.data['polls'][status[1]]['voters']:
                        senero.data['polls'][status[1]]['poll']['options'][int(status[0]) - 1]['votes'] += 1
                        senero.data['polls'][status[1]]['voters'].append(str(message.from_user.id))
                        bot.reply_to(message, 'Vote added to option number ' + status[0])
                        senero.save_file()
                    else:
                        bot.reply_to(message, 'You already voted for this')
                else:
                    bot.reply_to(message, 'Please use options from the keyboard')
            else:
                bot.reply_to(message, 'Please use options from the keyboard')

        @bot.message_handler(commands=['polls'])
        def polls(message):
            if not Senero.is_valid_chat(message):
                bot.reply_to(message, 'This bot is only available for group https://t.me/senero')
                return
            senero.ensure_user(message)

            options = []
            for poll_obj in senero.data['polls']:
                poll_id = poll_obj
                poll_obj = senero.data['polls'][poll_obj]['poll']
                options.append('/poll ' + poll_id + '\n' + poll_obj['title'])
            options_select = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            options_select.add(*options)
            bot.send_message(message.chat.id, 'Select a poll:',
                             reply_markup=options_select)

        @bot.message_handler(commands=['newpoll'])
        def new_poll(message):
            if not Senero.is_valid_chat(message):
                bot.reply_to(message, 'This bot is only available for group https://t.me/senero')
                return
            senero.ensure_user(message)
            if senero.is_admin(message):
                user_step[str(message.from_user.id)] = {}
                user_step[str(message.from_user.id)]['voters'] = []
                user_step[str(message.from_user.id)]['step'] = 'new_poll'
                bot.send_message(message.chat.id, 'Poll title: ',
                                 reply_markup=types.ForceReply(selective=False))
            else:
                bot.reply_to(message, 'Only admins can create new polls!')


        @bot.message_handler(commands=['deletepoll'])
        def delete_poll(message):
            if not Senero.is_valid_chat(message):
                bot.reply_to(message, 'This bot is only available for group https://t.me/senero')
                return
            if senero.is_admin(message):
                senero.ensure_user(message)
                if str(message.from_user.id) in senero.data['polls']:
                    del senero.data['polls'][str(message.from_user.id)]
                senero.save_file()
                bot.reply_to(message, 'Poll deleted')
            else:
                bot.reply_to(message, 'You are not an admin!')


        @bot.message_handler(commands=['publishpoll'])
        def publish_poll(message):
            if not Senero.is_valid_chat(message):
                bot.reply_to(message, 'This bot is only available for group https://t.me/senero')
                return
            if senero.is_admin(message):
                senero.ensure_user(message)
                senero.data['polls'][str(message.from_user.id)] = user_step[str(message.from_user.id)]
                del user_step[str(message.from_user.id)]
                senero.save_file()
                bot.reply_to(message, 'Poll published!')
            else:
                bot.reply_to(message, 'You are not an admin!')


        @bot.message_handler(content_types=['text'])
        def text_input(message):
            if str(message.from_user.id) in user_step:
                if 'new_poll' == user_step[str(message.from_user.id)]['step']:
                    user_step[str(message.from_user.id)]['step'] = 'poll_title'
                    user_step[str(message.from_user.id)]['poll'] = {}
                    user_step[str(message.from_user.id)]['poll']['title'] = message.text
                    user_step[str(message.from_user.id)]['poll']['options'] = []
                    bot.send_message(message.chat.id,
                                     'Add another option (image/text) or write /publishpoll for finish: ',
                                     reply_markup=types.ForceReply(selective=False))
                elif 'poll_title' == user_step[str(message.from_user.id)]['step']:
                    user_step[str(message.from_user.id)]['poll']['options'].append({'type': 'text',
                                                                                    'val': message.text,
                                                                                    'votes': 0
                                                                                    })
                    bot.send_message(message.chat.id,
                                     'Add another option (image/text) or write /publishpoll for finish: ',
                                     reply_markup=types.ForceReply(selective=False))
            elif 'step_pm' in senero.users[str(message.from_user.id)]:
                if 'answer_pm' == senero.users[str(message.from_user.id)]['step_pm']:
                    if 'hi senero community token bot' == message.text.lower():
                        bot.send_message(message.from_user.id, message.from_user.first_name + ' rewarded 1 token')
                        senero.add_points(str(message.from_user.id), 1, 'PM')
                        senero.users[str(message.from_user.id)]['step_pm'] = '3_questions'
                        senero.save_file()
                        bot.send_message(message.from_user.id, 'Great, good work! You have done well. To receive 1 '
                                                               'more token, you will be asked 3 easy questions that '
                                                               'will help you to join the community and earn limitless '
                                                               'tokens')
                        bot.send_message(message.from_user.id, 'First you must find the Senero tagline on the website\n'
                                                               'http://senero.org/')
                    else:
                        bot.send_message(message.from_user.id, 'You are not replying with the correct answer')
                elif '3_questions' == senero.users[str(message.from_user.id)]['step_pm']:
                    txt = message.text.lower()
                    if 'decentralized' in txt and 'protocol' in txt and 'untraceable' in txt and 'private' in txt:
                        bot.send_message(message.from_user.id, message.from_user.first_name + ' has 1 correct answer, '
                                                                                              'only 2 more to finish, '
                                                                                              'we are nearly there')
                        senero.users[str(message.from_user.id)]['step_pm'] = 'first_questions'
                        senero.save_file()
                        bot.send_message(message.from_user.id, 'Please go to the Community chat and write me a message '
                                                               'with reply to any of my messages')
                    else:
                        bot.send_message(message.from_user.id, 'This is not the correct tagline')
                elif 'first_questions' == senero.users[str(message.from_user.id)]['step_pm']:
                    bot.send_message(message.from_user.id, message.from_user.first_name + ' has 2 correct answers, only'
                                                                                          ' 1 more to to go!!')
                    senero.users[str(message.from_user.id)]['step_pm'] = 'second_questions'
                    senero.save_file()
                    bot.send_message(message.from_user.id, 'Okay we are nearly finished, type in /help in the '
                                                           'community chat to see how to earn limitless tokens')

        @bot.message_handler(content_types=['photo'])
        def get_photo(message):
            if str(message.from_user.id) in user_step:
                if 'poll_title' == user_step[str(message.from_user.id)]['step']:
                    file_id = message.photo[-1].file_id
                    file_path = json.loads(
                        urllib2.urlopen(
                            'https://api.telegram.org/bot' + args.token + '/getFile?file_id=' + file_id
                        ).read()
                    )['result']['file_path']
                    if not os.path.exists('images/' + str(message.from_user.id)):
                        os.makedirs('images/' + str(message.from_user.id))
                    with open('images/' + str(message.from_user.id) + '/' +
                              str(len(user_step[str(message.from_user.id)]['poll']['options']))
                              + '.png', 'wb') as new_file:
                        new_file.write(
                            urllib2.urlopen('https://api.telegram.org/file/bot' + args.token + '/' + file_path).read()
                        )
                        user_step[str(message.from_user.id)]['poll']['options'].append(
                            {'type': 'image',
                             'val': 'images/' + str(message.from_user.id) + '/' +
                                    str(len(user_step[str(message.from_user.id)]['poll']['options'])) + '.png',
                             'votes': 0
                             })
                    bot.send_message(message.chat.id,
                                     'Add another option (image/text) or write /publishpoll for finish: ',
                                     reply_markup=types.ForceReply(selective=False))


        bot.set_update_listener(listener)
        bot.polling()
    except Exception as e:
        print str(e)
