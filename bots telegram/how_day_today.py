import re
import sqlite3
import aiogram
import requests
import traceback
from random import choice
from bs4 import BeautifulSoup as bs
from security import TOKEN


class Bot_HDTD():
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

    def command_help(self):
        return 'DAY_BOT:\nWrite by form:\n/day DAY.NUM_MONTH (for ex "/day 31.12")\nor just\n/day\n-------------\n' \
               'WORDS_BOT:\n/huy word_phrase - add in base\n/yuh word_phrase - delete phrase in base'

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
                return 'Uncorrect date. Write by form:\nDAY.NUM_MONTH'

        else:
            day = None
        print(day)
        try:
            return f'{self.parsing(day)}'
        except:
            print('Error')
            return 'MY HEART IS BROKEEEEEN'


# Dangerous! A lot of Russian mat
class Bot_Huyot():
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
    def worthy_or_not_worthy(self, id):
        self.id = id
        if self.id == 829969304 or self.id == 548522557 or self.id == 379200653:
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
                if self.worthy_or_not_worthy(message['from']['id']):
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
        if self.worthy_or_not_worthy(message['from']['id']):
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
            return 'Авторизатион файлед, мотхерфатхер'
    #Команда вывода для Админов не основной БД
    def command_db_other(self, message):
        if self.worthy_or_not_worthy(message['from']['id']):
            text = ''
            db = self.cur_other.execute('SELECT * FROM words_other').fetchall()
            for i in db:
                text += i[0] + ':\n' + i[1] + '\n--------\n'
            if text == '':
                return 'Пустё'
            return text

        else:
            return 'Не лезь, она тебя сожрет'
    #Удаление значений из не основной БД
    def command_db_other_deleted(self, message):
        pass
    #Перенос значений из не основной БД в основную БД
    def command_db_other_in_db(self, message):
        pass
    #
    def bot_answer(self, message):
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


bot = aiogram.Bot(token=TOKEN)
db = aiogram.Dispatcher(bot)


@db.message_handler()
async def echo(message: aiogram.types.Message):
    text = None
    print(*[str(message['from']['username']), str(message.text), str(message['chat']['type'])], sep=' -*- ')
    if re.search(r'(^/day)', message.text):
       text = Bot_HDTD().command_day(message)
    elif re.search(r'(^/help)', message.text) or re.search(r'(^/start)', message.text):
        text = Bot_HDTD().command_help()
        print('*' * 5, text)
    elif re.search(r'(^/huy)', message.text):
        text = Bot_Huyot().command_huy(message)
        print('*' * 5, text)
    elif re.search(r'(^/yuh)', message.text):
        text = Bot_Huyot().command_yuh(message)
        print('*' * 5, text)
    elif re.search(r'(^/db)', message.text):
        text = Bot_Huyot().command_db_other(message)
    else:
        text = Bot_Huyot().bot_answer(message)
        if text:
            print('*' * 5, text)
    if text:
        await message.answer(text)


if __name__ == '__main__':
    try:
        aiogram.executor.start_polling(db, skip_updates=None)   # skip_updates=True
    except:
        traceback.print_exc()