import csv
from os.path import isfile
from time import sleep
from multiprocessing import Process, Lock

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By

FILENAME = 'data.csv'


def parse_bju(elements_texts: list[str]) -> list:
    bju_lst = []
    for i in range(9, 14, 2):
        value = elements_texts[i].rstrip('▲').rstrip('▼')
        if value == '-':
            bju_lst = [0, 0, 0]
            break
        bju_lst.append(float(value))
    return bju_lst


def parse_and_write(num_range, lock):
    options = EdgeOptions()
    options.add_argument('--headless')
    browser = webdriver.Edge(
        options=options,
        service=EdgeService(EdgeChromiumDriverManager().install())
    )
    browser.implicitly_wait(20)
    url = 'https://мониторингпитание.рф/данные/'

    with browser:
        browser.get(url)
        for reg_num in range(*num_range):
            try:
                region = browser.find_element(
                    By.CSS_SELECTOR, f'#regioo > option:nth-child({reg_num})'
                )
                region_name = region.text
                region.click()
                schools_num = len(
                    browser.find_elements(By.CSS_SELECTOR, '#oulis > option')
                )
                rows = []
            except Exception as e:
                print(f'Неизвестная ошибка на страице региона {region_name}', e)
                continue
            for school_num in range(2, schools_num + 1):
                try:
                    school = browser.find_element(
                        By.CSS_SELECTOR, f'#oulis > option:nth-child({school_num})'
                    )
                    school.click()
                    school_name = school.text

                    uneaten = browser.find_elements(
                        By.CSS_SELECTOR, '.simple-little-table a[target=_blank]'
                    )[-1]
                    sleep(1)
                    elements = browser.find_elements(
                        By.CSS_SELECTOR, 'tbody .boxShadow8'
                    )
                    uneaten_value = uneaten.get_attribute('textContent')
                    sleep(1)
                    elements_texts = [item.text.split() for item in elements]
                    all_menu = int(elements_texts[0][-1]) if elements_texts[0][-1].isdigit() else int(elements_texts[0][6])
                    sanpin_percent = float(elements_texts[2][-1].rstrip('%'))
                    breakfast_price = float(elements_texts[3][-2]) if elements_texts[3][-2][0].isdigit() else 0
                    lunch_price = float(elements_texts[4][-2]) if elements_texts[4][-2][0].isdigit() else 0
                    bju_breakfast = parse_bju(elements_texts[5])
                    bju_lunch = parse_bju(elements_texts[6])
                except (NoSuchElementException, StaleElementReferenceException, IndexError):
                    print('Нет элементов на странице:', region_name, school_name)
                except Exception as e:
                    print('Неизвестная ошибка:', e)
                else:
                    rows.append(
                        (
                            region_name, school_name, uneaten_value, all_menu, sanpin_percent,
                            breakfast_price, lunch_price, *bju_breakfast, *bju_lunch
                        )
                    )
            with lock:
                with open(FILENAME, 'a', encoding='utf-8-sig', newline='') as file:
                    writer = csv.writer(file, delimiter=';')
                    for row in rows:
                        writer.writerow(row)


if __name__ == '__main__':
    columns = ['Регион', 'Учебное учреждение', 'Доля несъедаемых', 'Всего меню',
               '% по Санпин', 'Стоимость завтрак', 'Стоимость обед', 'Бз', 'Жз',
               'Уз', 'Бо', 'Жо', 'Уо']

    if not isfile(FILENAME):
        with open(FILENAME, 'w', encoding='utf-8-sig', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(columns)

    lock = Lock()
    nums_range = ((61, 67), (69, 72), (76, 81), (81, 88))
    processes = [Process(target=parse_and_write, args=(num_range, lock)) for num_range in nums_range]
    for process in processes:
        process.start()
