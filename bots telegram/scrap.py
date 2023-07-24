from selenium import webdriver
from selenium.webdriver.common.by import By
from random import randint

import sqlite3


class Scraping():
    def __init__(self):
        # Скрипает проверку, перезаписывает все значения
        self.update_all_mthrfck = False
        self.month = {1:['yanvar', 31], 2:['fevral', 29], 3:['mart', 31],
                     4:['aprel', 30], 5:['may', 31], 6:['iyun', 30],
                     7:['iyul', 31], 8:['avgust', 31], 9:['sentyabr', 30],
                     10:['oktyabr', 31], 11:['noyabr', 30], 12:['dekabr', 31]}

        self.conn = sqlite3.connect('how_day_today.db')
        self.cur = self.conn.cursor()
        # form date DAY.MONTH (for ex: 31.12)
        self.cur.execute("""CREATE TABLE IF NOT EXISTS dates(
        date TEXT PRIMARY KEY,
        holidays TEXT);
        """)

        #url = 'https://xn--80aaiebcrjcibi8adgdtsm9z.xn--p1ai/'
        self.driver = webdriver.Chrome()

    def scraping(self, url_):
        self.driver.get('https://xn--80aaiebcrjcibi8adgdtsm9z.xn--p1ai/baza/' + url_)
        elems = self.driver.find_elements(By.XPATH, '//span[@itemprop="text"]')
        list_of_holidays = []
        for i in elems:
            list_of_holidays.append(i.text)
        return list_of_holidays

    def check_db(self, month_i_, day_):
        if self.update_all_mthrfck:
            return False
        result_ = self.cur.execute(f'SELECT holidays FROM dates WHERE date="{day_}.{month_i_}"').fetchone()
        # print(len(str(result_)))
        if result_:
            if len(str(result_)) > 6:
                # print(f"{day_}.{month_i_} V")
                return True
        print(f"NO INFO: {day_}.{month_i_}")
        return False

    def main(self):
        for month_i in self.month:
            for day in range(self.month[month_i][1]):
                # скип до несобранной информации колхозный
                '''
                if month_i < 5:
                    continue
                if month_i == 5 and day < 13:
                    continue
                '''
                # скип до несобранной информации менее колхозный
                if self.check_db(month_i, day+1):
                    continue
                # print((str(day+1)+'.'+str(month_i)))
                url = str(self.month[month_i][0]) + '/' + str(day+1)
                result = '\n'.join(self.scraping(url))
                date = str(day+1)+'.'+str(month_i)
                self.cur.execute(f'INSERT OR REPLACE INTO dates VALUES(?, ?);', [date, result])
                # sleep(randint(1, 5))
                self.conn.commit()
                print(date, "ready!")
            # print(month[month_i][0])


if __name__ == '__main__':
    Scraping().main()