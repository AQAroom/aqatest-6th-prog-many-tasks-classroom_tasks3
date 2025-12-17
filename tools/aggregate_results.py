#!/usr/bin/env python3
"""
Агрегирует результаты тестов в один JSON для GitHub Classroom Reporter
"""
import sys
import json
import base64

def decode_autograding_result(encoded_result):
    """Декодирует результат autograding-io-grader"""
    if not encoded_result or encoded_result in ('null', 'undefined', ''):
        return {'score': 0, 'max_score': 0, 'tests': []}
    
    try:
        decoded = base64.b64decode(encoded_result).decode('utf-8')
        return json.loads(decoded)
    except Exception as e:
        # Пишем ошибку в stderr, а не stdout
        print(f"ERROR decoding result: {e}", file=sys.stderr)
        return {'score': 0, 'max_score': 0, 'tests': []}

def main():
    if len(sys.argv) < 4:
        # Только ошибка в stderr
        print("Usage: python3 aggregate_results.py <task_name> <max_score> <encoded_result1> ...", file=sys.stderr)
        sys.exit(1)
    
    task_name = sys.argv[1]
    max_score = int(sys.argv[2])
    encoded_results = sys.argv[3:]
    
    total_score = 0
    test_count = 0
    
    # Суммируем баллы
    for encoded in encoded_results:
        if not encoded:
            continue
            
        data = decode_autograding_result(encoded)
        
        if 'tests' in data:
            for test in data['tests']:
                score = test.get('score', 0)
                total_score += score
                test_count += 1
    
    # Создаем результат
    result = {
        "version": 1,
        "status": "pass" if total_score == max_score else "fail",
        "max_score": max_score,
        "tests": [{
            "name": task_name,
            "status": "pass" if total_score == max_score else "fail",
            "score": total_score,
            "output": f"Набрано баллов: {total_score}/{max_score} ({test_count} тестов)"
        }]
    }
    
    # Кодируем в base64
    encoded_result = base64.b64encode(
        json.dumps(result, ensure_ascii=False).encode('utf-8')
    ).decode('utf-8')
    
    # ВЫВОДИМ ТОЛЬКО ЭТО - без дополнительного текста!
    print(f"AGGREGATED_RESULT={encoded_result}")

if __name__ == "__main__":
    main()

