import re
import csv
import json
import requests
import time
import pandas as pd

def extract_puzzle_object(js_text):

    # Начало 'var puzzle = '
    start_match = re.search(r'var\s+puzzle\s*=\s*', js_text)

    if not start_match:
        raise ValueError('Не найдено var puzzle =')
    start_pos = start_match.end()

    # Ищем первую открывающую скобку {
    brace_start = js_text.find('{', start_pos)
    if brace_start == -1:
        raise ValueError('Не найдена открывающая скобка')

    # Балансируем скобки
    balance = 0
    i = brace_start
    while i < len(js_text):
        ch = js_text[i]
        if ch == '{':
            balance += 1
        elif ch == '}':
            balance -= 1
            if balance == 0:
                brace_end = i + 1
                break
        i += 1
    else:
        raise ValueError('Не найдена закрывающая скобка для объекта puzzle')

    puzzle_js = js_text[brace_start:brace_end]

    # Очистка от комментариев
    puzzle_js = re.sub(r'//.*?$', '', puzzle_js, flags=re.MULTILINE)
    # Замена undefined на null
    puzzle_js = re.sub(r':\s*undefined\b', ': null', puzzle_js)
    # Ключи без кавычек берём в кавычки
    puzzle_js = re.sub(r'(\{|,)\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', puzzle_js)
    # Замена одинарных кавычек на двойные (для строковых значений)
    puzzle_js = puzzle_js.replace("'", '"')
    # Удаляем висячие запятые (перед } или ])
    puzzle_js = re.sub(r',\s*}', '}', puzzle_js)
    puzzle_js = re.sub(r',\s*]', ']', puzzle_js)

    try:
        return json.loads(puzzle_js)
    except json.JSONDecodeError as e:
        print('Ошибка парсинга JSON. Фрагмент:', puzzle_js[:500])
        raise

def replace_color_ids(header, used_colors):
    """
    Рекурсивно заменяет ID цвета (начиная с 1) на фактический цвет из used_colors.
    Каждый элемент вида [id, value] превращается в [used_colors[id-1], value].
    """
    if not isinstance(header, list):
        return header

    new_header = []
    for item in header:
        if isinstance(item, list) and len(item) == 2 and isinstance(item[0], int):
            # Это пара [id, значение] — заменяем первое число
            color_id = item[0]
            if 1 <= color_id <= len(used_colors):
                new_header.append([used_colors[color_id - 1], item[1]])
            else:
                # Если ID выходит за пределы, оставляем как есть (на случай ошибки)
                new_header.append(item)
        elif isinstance(item, list):
            # Рекурсивно обрабатываем вложенные списки (например, несколько пар подряд)
            new_header.append(replace_color_ids(item, used_colors))
        else:
            new_header.append(item)
    return new_header

def get_puzzle_data(puzzle_id):
    url = (
        f"https://www.griddlers.net/nonogram/-/g/t1780056115291/i01?p_p_lifecycle=2&p_p_resource_id=griddlerPuzzle&p_p_cacheability=cacheLevelPage&_gpuzzles_WAR_puzzles_id={puzzle_id}_gpuzzles_WAR_puzzles_lite=false"
    )
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()

    resp = extract_puzzle_object(resp.text)

    result = {'puzzle_id': puzzle_id}

    colors_list = []

    if len(resp['usedColors']) == 2:
        resp['colors'] = resp['colors'][:2]

        used = resp['usedColors']
        resp['topHeader'] = replace_color_ids(resp['topHeader'], used)
        resp['leftHeader'] = replace_color_ids(resp['leftHeader'], used)

        result['puzzle_mode'] = 'black-white'
    else:

        for i in range(len(resp['usedColors'])):
            colors_list.append(resp['colors'][resp['usedColors'][i]])

        resp['colors'] = colors_list
        resp['usedColors'] = [i for i in range(0,len(resp['usedColors']))]

        used = resp['usedColors']
        resp['topHeader'] = replace_color_ids(resp['topHeader'], used)
        resp['leftHeader'] = replace_color_ids(resp['leftHeader'], used)



        result['puzzle_mode'] = 'coloured'

    result.update(resp)

    del result['palette']
    del result['originalColors']
    del result['usedColors']

    return result

def save_puzzle_to_csv(puzzle_obj, csv_file='puzzles.csv'):
    """
    Сохраняет данные пазла в CSV-файл.
    Списки преобразуются в JSON-строки для плоского хранения.
    """

    row = puzzle_obj.copy()

    # Превращаем списки/словари в строки JSON
    for key in ['topHeader', 'leftHeader', 'colors']:
        if key in row:
            row[key] = json.dumps(row[key], ensure_ascii=False)

    fieldnames = [
        'puzzle_id', 'puzzle_mode', 'width', 'height', 'hw', 'hh',
        'colors', 'topHeader', 'leftHeader'
    ]

    try:
        with open(csv_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            existing_ids = {int(row['puzzle_id']) for row in reader}
    except FileNotFoundError:
        existing_ids = set()

    if puzzle_obj['puzzle_id'] in existing_ids:
        print(f"Пазл с ID {puzzle_obj['puzzle_id']} уже существует в {csv_file}. Пропускаем.")
        return

    file_exists = bool(existing_ids)
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)
    print(f"Пазл {puzzle_obj['puzzle_id']} успешно добавлен в {csv_file}.")



if __name__ == "__main__":

    PATH_CSV = "../../Data/Griddlers_net/Puzzles_GN_Dataset.csv"

    puzzle_obj = get_puzzle_data(294508)

    print(puzzle_obj)

    save_puzzle_to_csv(puzzle_obj, PATH_CSV)

    time.sleep(0.5)

    puzzle_obj = get_puzzle_data(295987)

    print(puzzle_obj)

    save_puzzle_to_csv(puzzle_obj, PATH_CSV)
