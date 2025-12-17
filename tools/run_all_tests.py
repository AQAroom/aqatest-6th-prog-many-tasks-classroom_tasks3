#!/usr/bin/env python3
import json
import subprocess
import sys
import os
from pathlib import Path

# Добавим текущую директорию в sys.path, чтобы импортировать utils
sys.path.insert(0, str(Path(__file__).parent))
from utils import encode_result_for_classroom

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

        score = 1 if passed else 0  # autograding-io-grader возвращает 0/1, потом умножаем на max_score
        output = actual if passed else f"Expected: {expected_output}, Got: {actual}"
        if error:
            output += f"\nSTDERR: {error}"

        return {
            "status": "pass" if passed else "fail",
            "score": score,
            "output": output
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "fail",
            "score": 0,
            "output": f"Timeout after {timeout}s"
        }
    except Exception as e:
        return {
            "status": "fail",
            "score": 0,
            "output": f"Exception: {e}"
        }

def main():
    with open(".github/tasks.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    os.makedirs("results", exist_ok=True)

    for task in config["tasks"]:
        task_id = task["id"]
        command = f"python {task['file']}"
        task_results = []

        for test in task["tests"]:
            print(f"Running {task_id}: {test['name']}")
            res = run_single_test(
                command=command,
                input_str=test["input"],
                expected_output=test["expected_output"],
                method=test["comparison_method"],
                timeout=5
            )
            # autograding-io-grader возвращает score=1 если passed, иначе 0
            # но реальный балл = score * max_score
            res["name"] = test["name"]
            res["raw_score"] = res["score"]  # 0 или 1
            res["max_score"] = test["max_score"]
            res["score"] = res["raw_score"] * test["max_score"]
            task_results.append(res)

        # Формат как у autograding-io-grader
        full_result = {
            "version": 1,
            "status": "pass" if all(t["raw_score"] for t in task_results) else "fail",
            "max_score": task["max_score"],
            "tests": task_results
        }

        encoded = encode_result_for_classroom(full_result)
        with open(f"results/{task_id}.json", "w", encoding="utf-8") as f:
            json.dump(full_result, f, ensure_ascii=False, indent=2)

        # Сохраняем в формате, совместимом с оригинальным output.step
        with open(f"results/{task_id}.encoded", "w") as f:
            f.write(encoded)

        print(f"✅ {task_id}: {sum(t['score'] for t in task_results)}/{task['max_score']}")

if __name__ == "__main__":
    main()
