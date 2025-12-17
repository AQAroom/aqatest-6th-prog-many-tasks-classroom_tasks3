#!/usr/bin/env python3
# tools/check_json.py - работает через stdin или аргументы
import sys
import json
import base64

def check_json(encoded=None, name="Unknown"):
    """Проверяет JSON из base64 строки или stdin"""
    if encoded is None:
        # Читаем из stdin
        encoded = sys.stdin.read().strip()
    
    if not encoded or encoded.lower() in ("null", "undefined", "not_set"):
        print(f"❌ {name}: Нет данных")
        return False
    
    try:
        decoded = base64.b64decode(encoded).decode('utf-8')
        data = json.loads(decoded)
        
        print(f"✅ {name}: Валидный JSON")
        print(f"   Статус: {data.get('status', 'unknown')}")
        print(f"   Макс. баллы: {data.get('max_score', 'N/A')}")
        
        if 'tests' in data:
            total_score = 0
            for i, test in enumerate(data['tests'], 1):
                score = test.get('score', 0)
                total_score += score
                print(f"   Тест {i}: {test.get('name', 'unnamed')} = {score} баллов")
            print(f"   ИТОГО: {total_score} баллов")
        elif 'score' in data:
            print(f"   Баллы: {data.get('score', 0)}")
        
        return True
        
    except Exception as e:
        print(f'❌ {name}: Ошибка - {e}')
        print(f"   Входные данные (первые 100): {encoded[:100]}...")
        return False

def main():
    # Если есть аргументы, используем их
    if len(sys.argv) >= 3:
        encoded = sys.argv[1]
        name = sys.argv[2]
        check_json(encoded, name)
    elif len(sys.argv) == 2:
        # Только encoded, имя по умолчанию
        check_json(sys.argv[1], "JSON Check")
    else:
        # Читаем из stdin
        check_json(name="Stdin JSON")

if __name__ == "__main__":
    main()
