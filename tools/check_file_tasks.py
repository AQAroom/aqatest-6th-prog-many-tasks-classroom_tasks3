#!/usr/bin/env python3
import base64, json, sys, re, os

def check_file(filename):
    try:
        with open(filename, 'r') as f:
            content = f.read()
        
        # Ищем AGGREGATED_RESULT
        match = re.search(r'AGGREGATED_RESULT=(.+)', content)
        if not match:
            print(f'❌ {filename}: Не найден AGGREGATED_RESULT')
            return None
        
        encoded = match.group(1)
        print(f'📄 {filename}: Найден результат, длина: {len(encoded)}')
        
        # Пробуем декодировать
        try:
            decoded = base64.b64decode(encoded).decode('utf-8')
            data = json.loads(decoded)
            
            score = data.get('tests', [{}])[0].get('score', 0)
            max_score = data.get('max_score', 0)
            
            print(f'   ✅ Valid JSON: {score}/{max_score} баллов')
            print(f'   Структура: {list(data.keys())}')
            return encoded
            
        except Exception as e:
            print(f'   ❌ Ошибка декодирования: {e}')
            return None
            
    except FileNotFoundError:
        print(f'❌ {filename}: Файл не найден')
        return None

if __name__ == "__main__":
    files_to_check = ['task1_aggregated.txt', 'task2_aggregated.txt', 'task3_aggregated.txt']
    
    for file in files_to_check:
        if os.path.exists(file):
            check_file(file)
        else:
            print(f'❌ {file}: Файл не существует')
