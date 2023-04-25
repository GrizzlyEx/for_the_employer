import re
import sqlite3
import time

import aiogram
import requests
import traceback
from random import choice
from bs4 import BeautifulSoup as bs
from time import perf_counter

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from security import TOKEN

letter_output = None
offline = False
time_stalker = None
time_offline = None
offline_noletter = False

class BotHDTD():
    def __init__(self):
        self.month = {1:['yanvar', 31], 2:['fevral', 29], 3:['mart', 31],
             4:['aprel', 30], 5:['may', 31], 6:['iyun', 30],
             7:['iyul', 31], 8:['avgust', 31], 9:['sentyabr', 30],
             10:['oktyabr', 31], 11:['noyabr', 30], 12:['dekabr', 31]}
    def params_today(self, day):
        cookies = {
            'PHPSESSID': 'bn50sroom2odt7dfo228id4l62',
            '_ym_uid': '1669620665125302786',
            '_ym_d': '1669620665',
            '_ym_isad': '2',
        }

        headers = {
            'authority': 'kakoysegodnyaprazdnik.ru',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'ru-RU,ru;q=0.9',
            'cache-control': 'no-cache',
            # Requests sorts cookies= alphabetically
            # 'cookie': 'PHPSESSID=bn50sroom2odt7dfo228id4l62; _ym_uid=1669620665125302786; _ym_d=1669620665; _ym_isad=2',
            'pragma': 'no-cache',
            'referer': 'https://yandex.ru/',
            'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        }
        if day:
            response = requests.get(f'https://kakoysegodnyaprazdnik.ru/baza/{self.month[day[1]][0]}/{day[0]}/', cookies=cookies, headers=headers)
        else:
            response = requests.get('https://kakoysegodnyaprazdnik.ru/', cookies=cookies, headers=headers)
        #return bs(response.text, 'html.parser').head
        response.encoding = 'utf-8'
        return response.text

    def parsing(self, day):
        self.day = day
        text = self.params_today(self.day)
        #print(bs(text, 'html.parser').h2.text)
        #print(bs(text, 'html.parser').div.div.span.text)
        message = str(bs(text, 'html.parser').h1.text)+'\n'
        for i in bs(text, 'html.parser').div.select(".listing_wr")[0]:
            #print(i)
            if i.text != '\n':
                message+='\n\n•'.join((i.text.split('•')))
        #print(message)
        return message
        #print(bs(text, 'html.parser').div.div.span.text)

    def command_help(self, message):
        text = 'DAY_BOT:\nWrite by form:\n/day DAY.NUM_MONTH (for ex "/day 31.12")\nor just\n/day\n-------------\n' \
               'WORDS_BOT:\n/huy word_phrase - add in base\n/yuh word_phrase - delete phrase in base\n' \
               '/status - information about sleep'
        if BotHuyot().worthy_or_not_worthy(message):
            text += '\n\nIT\'S FOR ADMINS OF THIS BOT!\n/db - chech not the main one DB\n/db_1 - check main DB\n' \
                    '/db_2 - check kontur\'s DB'
            if message['from']['id'] == 829969304:
                text += '\n-------------\nIT\'S ONLY FOR ME!\nBot NO_LETTER:\n' \
                        '/actual [letter][0 or 1, where 0 - not actual, 1 - actual] ' \
                        '(for ex "/actual ё1") - change actuality letter\n' \
                        '/letter - choose a random letter\n' \
                        '/change [letter letter letter ...] - change the trigger letter/s'
        return text

    def command_day(self, message):
        self.message = message
        mess_analyse = self.message.text.split(' ')
        if len(mess_analyse) > 1:
            if '.' in mess_analyse[1]:
                mess_analyse = mess_analyse[1].split('.')
                if mess_analyse[0].isnumeric() and mess_analyse[1].isnumeric():
                    if int(mess_analyse[1]) > 12 and int(mess_analyse[0]) > 12:
                        return 'Uncorrect numbers: there are 12 months in a year'

                    elif int(mess_analyse[1]) > 12:
                        day = [int(mess_analyse[1]), int(mess_analyse[0])]
                    else:
                        day = [int(mess_analyse[0]), int(mess_analyse[1])]
                    if day[0] > self.month[day[1]][1]:
                        return f'Uncorrect numbers: max of {self.month[day[1]][1]} days in the month'

                else:
                    return 'Date shoud have only numbers'

            else:
                return 'Uncorrect date. Write by form:\nDAY.NUM_MONTH (for ex "/day 31.12")'

        else:
            day = None
        print(day)
        try:
            return f'{self.parsing(day)}'
        except:
            print('Error')
            return 'MY HEART IS BROKEEEEEN'


# Dangerous! A lot of Russians mat
class BotHuyot():
    def __init__(self):
        #Основная БД
        self.conn = sqlite3.connect('huyot.db')
        self.cur = self.conn.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS words(
           text TEXT PRIMARY KEY,
           answer_text TEXT);
        """)
        self.conn.commit()
        #Разгребная БД
        self.cur_other = self.conn.cursor()
        self.cur_other.execute("""CREATE TABLE IF NOT EXISTS words_other(
                   text TEXT PRIMARY KEY,
                   answer_text TEXT);
                """)
        self.conn.commit()

    #Проверка на админа, шо бэ чужие шаловливые ручонки не лазили
    def worthy_or_not_worthy(self, message):
        user_id = message['from']['id']
        if user_id == 829969304 or user_id == 548522557 or user_id == 379200653:
            return True
        return False

    #Команда добавления в основную/не основную БД
    def command_huy(self, message):
        self.message = message
        text = self.message.text
        if re.search(r'(_)', text):
            text = text[4:].split('_')
            # print(text)
            if len(text) > 1:
                text_db = [' '.join(text[0].split()).lower(), ' '.join(text[1].split())]
                if self.worthy_or_not_worthy(message):
                    db_info = 'words'
                else:
                    db_info = 'words_other'
                text_in_db = self.cur.execute(f'SELECT answer_text FROM {db_info} WHERE text = "{text_db[0]}"').fetchone()
                if text_in_db:
                    text_in_db = text_in_db[0] + '\n' + str(text_db[1])
                    self.cur.execute(f'UPDATE {db_info} SET answer_text = "{text_in_db}" WHERE text = "{text_db[0]}"')
                    txt = 'Добавил еще и ето'
                else:
                    self.cur.execute(f'INSERT OR REPLACE INTO {db_info} VALUES(?, ?);', text_db)
                    txt = 'Добавил'
                self.conn.commit()
                return f'{txt}, иди на хуй'

                # print(text_db)
            else:
                return 'Форма: /huy слово _ фраза, а ты пидор'
        else:
            return 'Форма: /huy слово _ фраза, а ты пидор'

    #Команда удаления из основной БД
    def command_yuh(self, message):
        self.message = message
        text = self.message.text
        if self.worthy_or_not_worthy(message):
            if re.search(r'(_)', text):
                text = text[4:].split('_')
                # print(text)
                if len(text) > 1:
                    text_db = [' '.join(text[0].split()).lower(), ' '.join(text[1].split())]
                    text_in_db = self.cur.execute(f'SELECT answer_text FROM words WHERE text = "{text_db[0]}"').fetchone()
                    if text_in_db:
                        txt_ = []
                        for i in text_in_db[0].split('\n'):
                            #print(i, text_db[1], sep='**')
                            #print(i.lower() == text_db[1].lower())
                            if i.lower() != text_db[1].lower():
                                txt_.append(i)
                                #print(txt_)
                        text_in_db = '\n'.join(txt_)
                        #print(text_in_db)
                        self.cur.execute(f'UPDATE words SET answer_text = "{text_in_db}" WHERE text = "{text_db[0]}"')
                        self.conn.commit()
                        return 'Удолилб'
                    else:
                        return 'Такой залупы не было'
                    # print(text_db)
                else:
                    return 'Форма: /yuh слово _ фраза, а ты пидор'
            else:
                return 'Форма: /yuh слово _ фраза, а ты пидор'
        else:
            return 'Авторизатион фeйлед, мотхерфатхер'

    #Команда вывода для Админов не основной БД
    def command_db_other(self, message):
        if self.worthy_or_not_worthy(message):
            text = ''
            db = self.cur_other.execute('SELECT * FROM words_other').fetchall()
            for i in db:
                text += i[0] + ':\n' + i[1] + '\n--------\n'
            if text == '':
                return 'Пустё'
            return text

        else:
            return 'Не лезь, она тебя сожрет'

    #Понятно без лишних слов :D
    #Уточнение: вывод всех значений id = 1 - основная бд, 2 - второго бота
    def for_Marusyas_curiosity(self, message, id_db):
        if self.worthy_or_not_worthy(message):
            text = ''
            if id_db == 1:
                db = self.cur.execute('SELECT * FROM words').fetchall()
            elif id_db == 2:
                conn_2 = sqlite3.connect('huyot_2.db')
                cur_2 = conn_2.cursor()
                db = cur_2.execute('SELECT * FROM words').fetchall()
            for i in db:
                text += '-' + i[0] + ': ' + ' | '.join(i[1].split('\n')) + '\n'
            if text == '':
                return 'Пустё'
            return text
        else:
            return 'Авторизатион фeйлед, мотхерфатхер'

    def command_offline(self, message):
        if self.worthy_or_not_worthy(message):
            global offline, time_offline, time_stalker
            if len(message.text) > 4:
                if len(message.text.split()) > 1:
                    message_ = message.text.split()[1]
                    if message_.isdigit():

                        time_stalker = perf_counter()
                        time_offline = int(message_) * 60
                        offline = True
                        return f'Умолкаю на {message_} минут'
                    return 'Число целое пиши, а не вотэтовот'
                return '/off [кол-во минут]'

            else:
                time_offline = None
                time_stalker = None

                if offline == True:
                    offline = False
                    return 'ВЕЧЕР В ХАТУ'
                else:
                    offline = True
                    return 'Умолкаю'
        return 'Тока для избранных'

    def chech_offline(self, message):
        global offline, time_offline, time_stalker
        if time_stalker:
            if time_stalker+time_offline < perf_counter():
                time_stalker = None
                time_offline = None
                offline = False

    def command_status(self, message):
        global offline, time_stalker, time_offline
        if offline:
            if time_stalker:
                timet = int((time_offline+time_stalker)-perf_counter())
                return f'Я молчу еще {timet//60} минут и {timet%60} секунд'
            return 'Я молчу'
        return 'Жив. Цел. Орел'

    #Удаление значений из не основной БД
    def command_db_other_deleted(self, message):
        pass

    #Перенос значений из не основной БД в основную БД
    def command_db_other_in_db(self, message):
        pass

    #Механика ответа
    def bot_answer(self, message):
        global offline
        if offline == True:
            return
        text = ' '.join(message.text.split()).lower()
        #print(text)
        equal = None
        if re.search(r'([!?,\.()\[\]\\\{\}])', text[-1]):
            # проверка на ( и )
            equal = self.cur.execute(f'SELECT answer_text FROM words WHERE text = "{text[-1]}"').fetchone()
        if not equal:
            # если в предыдущую проверку значение equal не присвоилось, убираем символы из исключения
            iskl = '[{\[1234567890-=!><()@#$%^&*_+|\\"/\'№;:?`~.,}\]]'
            text = re.sub(iskl, ' ', text)
            text = ' '.join(text.split())
            # проверка на полную схожесть сообщения и строк в бд
            equal = self.cur.execute(f'SELECT answer_text FROM words WHERE text = "{text}"').fetchone()
            if not equal:
                # ('пизда\nманда\nхуй на\nнет\nкульманда',)
                # проверка на последнее слово из сообщения
                equal = self.cur.execute(f'SELECT answer_text FROM words WHERE text = "{text.split()[-1]}"').fetchone()
        if equal:
            #print(message.text)
            return choice(equal[0].split('\n'))


class NoLetter():
    def __init__(self):
        # Основная БД
        self.conn = sqlite3.connect('letter.db')
        self.cur = self.conn.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS letters(
                   letter TEXT PRIMARY KEY,
                   actual INT);
                """)

    def added_more_letter(self):
        letters = 'АБВГДЕËЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
        not_actial_list = 'ËЙФХЦЧШЩЪЫЬЭЮЯ'
        for letter in letters:
            actual = 1
            if letter in not_actial_list:
                actual = 0
            self.cur.execute(f'INSERT OR REPLACE INTO letters VALUES(?, ?);', [letter, actual])
        self.conn.commit()

    def worty_letter(self, message):
        if message['from']['id'] == 829969304:
            return True
        return False

    def change_actual(self, message):
        if self.worty_letter(message):
            if len(message.text) > 9:
                if message.text[9].isdigit():
                    #print(message[8].upper())
                    if self.cur.execute(f'SELECT * FROM letters WHERE letter = "{message.text[8].upper()}"').fetchone() or \
                            message.text[8].upper() == 'Ë':
                        char = message.text[8].upper()
                        #print(char)
                        self.cur.execute(f'UPDATE letters SET actual = {message.text[9]} WHERE letter = "{char}"')
                        self.conn.commit()
                        return 'OK'
        return 'Not OK'

    def output_letter(self, message):
        if self.worty_letter(message):
            global letter_output, offline_noletter
            offline_noletter = False
            list_from_db = self.cur.execute(f'SELECT * from letters').fetchall()
            letter = choice(list_from_db)
            #print(letter)
            letter_output = [letter[0]]
            if letter[1] == 0:
                letter_2 = self.cur.execute(f'SELECT * from letters WHERE letter != "{letter[0]}" and actual = 0').fetchall()
                letter_output.append(choice(letter_2)[0])
            return letter_output
        return 'Ti imeesh problemi?'

    def change_letter_value(self, message):
        if self.worty_letter(message):
            global letter_output, offline_noletter
            if len(message.text) > 8:
                offline_noletter = False
                letter_output = message.text[8:].upper().split()
                #print(letter_output)
                return 'ok'
            else:
                offline_noletter = True
                return 'off'
        return 'NOT OK'

    def check_pidor(self, message):
        global offline_noletter
        if self.worty_letter(message) and not offline_noletter:
            global letter_output
            if letter_output:
                for i in letter_output:
                    if i in message.text.upper():
                        return 'Za bazarom sledi!'
        return ''


class Translater():
    def __init__(self, text_message):
        self.text_message = text_message
        dict_ascii = {
            ' ': '%20',
            '/': '%2F',
            '?': '%3F',
            ',': '%2C',
            '\\': '%5C',
            '@': '%40',
            '#': '%23',
            '$': '%24',
            '%': '%25',
            '^': '%5E',
            '&': '%26',
            '=': '%3D',
            ':': '%3A',
            '\'': '%27',
            '`': '%60',
            '{': '%7B',
            '}': '%7D',
            '[': '%5B',
            ']': '%5D',
            '+': '%2B',
            '|': '%7C',
        }
        self.text = ''
        for i in text_message:
            if i in dict_ascii:
                self.text += dict_ascii[i]
            else:
                self.text += i
    def translate_v2(self):

        print(response.text)

        # Note: json_data will not be serialized by requests
        # exactly as it was in the original request.
        # data = '{ "text": "Some text to translate",  "source_language": "en", "translation_language": "fr"}'
        # response = requests.post('https://api.translate.com/translate/v1/mt', headers=headers, data=data)
    def translate(self, target='ru'):
        if self.text != '':
            driver = webdriver.Chrome('C:\\Users\\\SaltanovaAO\\\PycharmProjects\\main\\chromedriver.exe')
            driver.get(f"https://translate.google.ru/?sl=auto&tl={target}&text={self.text}")
            elem = driver.find_element(By.XPATH, '//div[@aria-live=\"polite\"]')
            #time.sleep(1000)
            #print(*elem.text.split('\n'), sep='\n')
            return ' '.join(elem.text.split('\n')[:-1])


#NoLetter().output_letter('sss')
bot = aiogram.Bot(token=TOKEN)
db = aiogram.Dispatcher(bot)


@db.message_handler()
async def echo(message: aiogram.types.Message):
    #print(*[str(message['from']['username']), str(message.text), str(message['chat']['type'])], sep=' -*- ')
    print(message)
    BotHuyot().chech_offline(message)
    if re.search(r'(^/day)', message.text.lower()):
       text = BotHDTD().command_day(message)
    elif re.search(r'(^/help)', message.text.lower()) or re.search(r'(^/start)', message.text.lower()):
        text = BotHDTD().command_help(message)
        print('*' * 5, text)
    elif re.search(r'(^/huy)', message.text.lower()):
        text = BotHuyot().command_huy(message)
        print('*' * 5, text)
    elif re.search(r'(^/yuh)', message.text.lower()):
        text = BotHuyot().command_yuh(message)
        print('*' * 5, text)
    elif re.search(r'(^/db_1)', message.text.lower()) or re.search(r'(^/db_2)', message.text.lower()):
        if re.search(r'(^/db_1)', message.text):
            id_db = 1
        else:
            id_db = 2
        text = BotHuyot().for_Marusyas_curiosity(message, id_db)
    elif re.search(r'(^/db)', message.text.lower()):
        text = BotHuyot().command_db_other(message)
    elif re.search(r'(^/off)', message.text.lower()):
        text = BotHuyot().command_offline(message)
    elif re.search(r'(^/status)', message.text.lower()):
        text = BotHuyot().command_status(message)
    elif re.search(r'(^/actual)', message.text.lower()):
        text = NoLetter().change_actual(message)
    elif re.search(r'(^/letter)', message.text.lower()):
        text = ', '.join(NoLetter().output_letter(message))
    elif re.search(r'(^/change)', message.text.lower()):
        text = NoLetter().change_letter_value(message)
    elif re.search(r'(^переведи)', message.text.lower()):
        text = Translater(message).translate()
    else:
        text_message = ''
        if 'reply_to_message' in message:
            if 'text' in message['reply_to_message']:
                text_message = message['reply_to_message']['text']
        elif 'forward_from' in message:
            text_message = message['text']
        if text_message != '':
            text = Translater(text_message).translate()
        else:
            text = BotHuyot().bot_answer(message)
        text_other = NoLetter().check_pidor(message)
        if text_other:
            if text:
                text += '\n' + text_other
            else:
                text = text_other
        if text:
            print('*' * 5, text)
    if text:
        await message.answer(text)


if __name__ == '__main__':
    try:
        aiogram.executor.start_polling(db, skip_updates=None)   # skip_updates=True
    except:
        traceback.print_exc()