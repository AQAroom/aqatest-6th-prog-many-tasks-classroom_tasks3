#!/usr/bin/env python3
"""
Парсит результаты тестов и вычисляет суммарные баллы
"""

import sys
import json
import base64

def parse_task_scores(*encoded_results):
    """Парсит и суммирует баллы из результатов тестов"""
    total_score = 0
    test_count = 0
    
    print(f"Parsing {len(encoded_results)} test results...", file=sys.stderr)
    
    for i, encoded in enumerate(encoded_results):
        if not encoded or encoded == 'null':
            print(f"  Test {i+1}: empty result", file=sys.stderr)
            continue
            
        try:
            decoded = base64.b64decode(encoded).decode('utf-8')
            data = json.loads(decoded)
            
            if 'tests' in data:
                for test in data['tests']:
                    score = test.get('score', 0)
                    total_score += score
                    test_count += 1
                    print(f"  Test {test_count}: {test.get('name')} = {score} points", file=sys.stderr)
            elif 'score' in data:
                total_score += data['score']
                test_count += 1
                print(f"  Test {i+1}: direct score = {data['score']} points", file=sys.stderr)
                
        except Exception as e:
            print(f"ERROR parsing test {i+1}: {e}", file=sys.stderr)
    
    print(f"Total: {total_score} points from {test_count} tests", file=sys.stderr)
    return total_score

def main():
    if len(sys.argv) < 2:
        print("TASK_SCORE=0")
        return
    
    task_num = sys.argv[1]
    
    if task_num == "1" and len(sys.argv) >= 5:
        score = parse_task_scores(sys.argv[2], sys.argv[3], sys.argv[4])
        print(f"TASK_SCORE={score}")
    elif task_num == "2" and len(sys.argv) >= 5:
        score = parse_task_scores(sys.argv[2], sys.argv[3], sys.argv[4])
        print(f"TASK_SCORE={score}")
    elif task_num == "3" and len(sys.argv) >= 5:
        score = parse_task_scores(sys.argv[2], sys.argv[3], sys.argv[4])
        print(f"TASK_SCORE={score}")
    else:
        print("TASK_SCORE=0")

if __name__ == "__main__":
    main()
