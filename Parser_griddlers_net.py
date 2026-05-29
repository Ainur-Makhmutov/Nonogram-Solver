import re
import json
import requests

def extract_puzzle_object(js_text):
    # Находим начало 'var puzzle = '
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

def get_puzzle_data(puzzle_id):
    url = (
        f"https://www.griddlers.net/nonogram/-/g/t1780056115291/i01?p_p_lifecycle=2&p_p_resource_id=griddlerPuzzle&p_p_cacheability=cacheLevelPage&_gpuzzles_WAR_puzzles_id=294508&_gpuzzles_WAR_puzzles_lite=false"
    )
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    return extract_puzzle_object(resp.text)

if __name__ == "__main__":
    puzzle = get_puzzle_data(294508)
    print(json.dumps(puzzle, indent=2, ensure_ascii=False))