import aiogram
import requests
from bs4 import BeautifulSoup as bs
from security import TOKEN


def params_today():
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

    response = requests.get('https://kakoysegodnyaprazdnik.ru/', cookies=cookies, headers=headers)
    #return bs(response.text, 'html.parser').head
    response.encoding = 'utf-8'
    return response.text


def parsing(text=params_today()):
    #print(bs(text, 'html.parser').h2.text)
    #print(bs(text, 'html.parser').div.div.span.text)
    #print(bs(text, 'html.parser'))
    message = ''
    for i in bs(text, 'html.parser').div.div:
        if i.text != '\n':
            message+='\n\n•'.join((i.text.split('•')))

    return message
    #print(bs(text, 'html.parser').div.div.span.text)


bot = aiogram.Bot(token=TOKEN)
db = aiogram.Dispatcher(bot)



@db.message_handler(commands=['day'])
async def echo(message: aiogram.types.Message):
    try:
        await message.answer(f'{parsing()}')
    except:
        print('Error')
        await message.answer('Йа сломался')



if __name__ == '__main__':
    aiogram.executor.start_polling(db, skip_updates=None)   # skip_updates=True