#!/usr/bin/env python3
import json
import subprocess
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import encode_result_for_classroom, make_task_result_stub

def run_single_test(command, input_str, expected_output, method, timeout):
    try:
        result = subprocess.run(
            command,
            input=input_str,
            text=True,
            capture_output=True,
            timeout=timeout,
            shell=True
        )
        actual = result.stdout.strip()
        error = result.stderr

        if method == "exact":
            passed = actual == expected_output
        elif method == "contains":
            passed = expected_output in actual
        else:
            passed = False

        score = 1 if passed else 0
        output = actual
        if error and not passed:
            output += f"\nSTDERR: {error}"

        return {
            "status": "pass" if passed else "fail",
            "raw_score": score,
            "output": output
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "fail",
            "raw_score": 0,
            "output": f"Timeout after {timeout}s"
        }
    except Exception as e:
        return {
            "status": "fail",
            "raw_score": 0,
            "output": f"Exception: {e}"
        }

def main():
    config_path = ".github/tasks.json"
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    os.makedirs("results", exist_ok=True)

    for task in config["tasks"]:
        task_id = task["id"]
        task_file = task["file"]
        print(f"\n🧪 Processing {task_id} ({task_file})...")

        # Проверяем, существует ли файл
        if not os.path.exists(task_file):
            print(f"  ❌ {task_file} not found → 0 points")
            result_data = make_task_result_stub(task)
        else:
            # Проверяем синтаксис
            try:
                subprocess.run([sys.executable, "-m", "py_compile", task_file], check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                print(f"  ❌ Syntax error in {task_file} → 0 points")
                result_data = make_task_result_stub(task)
                # Добавим ошибку в первый тест
                if result_data["tests"]:
                    result_data["tests"][0]["output"] = f"SyntaxError:\n{e.stderr.decode()}"
            else:
                # Запускаем тесты
                command = f"{sys.executable} {task_file}"
                task_results = []
                for test in task["tests"]:
                    print(f"  → Running: {test['name']}")
                    res = run_single_test(
                        command=command,
                        input_str=test["input"],
                        expected_output=test["expected_output"],
                        method=test["comparison_method"],
                        timeout=5
                    )
                    res["name"] = test["name"]
                    res["max_score"] = test["max_score"]
                    res["score"] = res["raw_score"] * test["max_score"]
                    task_results.append(res)

                total_score = sum(t["score"] for t in task_results)
                result_data = {
                    "version": 1,
                    "status": "pass" if total_score == task["max_score"] else "fail",
                    "max_score": task["max_score"],
                    "tests": task_results
                }

        # Сохраняем результат
        with open(f"results/{task_id}.json", "w", encoding="utf-8") as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)

        # Сохраняем base64-версию (для совместимости)
        encoded = encode_result_for_classroom(result_data)
        with open(f"results/{task_id}.encoded", "w") as f:
            f.write(encoded)

        actual_score = sum(t.get("score", 0) for t in result_data["tests"])
        print(f"  ✅ {task_id}: {actual_score}/{task['max_score']}")

if __name__ == "__main__":
    main()
