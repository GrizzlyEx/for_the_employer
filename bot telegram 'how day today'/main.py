import aiogram
import requests
from bs4 import BeautifulSoup as bs
from security import TOKEN

month = {1:['yanvar', 31], 2:['fevral', 29], 3:['mart', 31],
         4:['aprel', 30], 5:['may', 31], 6:['iyun', 30],
         7:['iyul', 31], 8:['avgust', 31], 9:['sentyabr', 30],
         10:['oktyabr', 31], 11:['noyabr', 30], 12:['dekabr', 31]}
def params_today(day):
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
        response = requests.get(f'https://kakoysegodnyaprazdnik.ru/baza/{month[day[1]][0]}/{day[0]}/', cookies=cookies, headers=headers)
    else:
        response = requests.get('https://kakoysegodnyaprazdnik.ru/', cookies=cookies, headers=headers)
    #return bs(response.text, 'html.parser').head
    response.encoding = 'utf-8'
    return response.text


def parsing(day):
    text = params_today(day)
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
#print(params_today())
#print(parsing())
bot = aiogram.Bot(token=TOKEN)
db = aiogram.Dispatcher(bot)



@db.message_handler(commands=['day'])
async def echo(message: aiogram.types.Message):
    mess_analyse = message.text.split(' ')
    if len(mess_analyse) > 1:
        if '.' in mess_analyse[1]:
            mess_analyse = mess_analyse[1].split('.')
            if mess_analyse[0].isnumeric() and mess_analyse[1].isnumeric():
                if int(mess_analyse[1]) > 12 and int(mess_analyse[0]) > 12:
                    await message.answer('Uncorrect numbers: there are 12 months in a year')
                    return
                elif int(mess_analyse[1]) > 12:
                    day = [int(mess_analyse[1]), int(mess_analyse[0])]
                else:
                    day = [int(mess_analyse[0]), int(mess_analyse[1])]
                if  day[0] > month[day[1]][1]:
                    await message.answer(f'Uncorrect numbers: max of {month[day[1]][1]} days in the month')
                    return

            else:
                await message.answer('Date shoud have only numbers')
                return
        else:
            await message.answer('Uncorrect date. Write by form:\nDAY.NUM_MONTH')
            return
    else:
        day = None
    print(day)
    try:
        await message.answer(f'{parsing(day)}')
    except:
        print('Error')
        await message.answer('MY HEART IS BROKEEEEEN')



if __name__ == '__main__':
    aiogram.executor.start_polling(db, skip_updates=None)   # skip_updates=True