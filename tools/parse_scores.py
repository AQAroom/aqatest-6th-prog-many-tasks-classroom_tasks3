#!/usr/bin/env python3
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import decode_autograding_result

def main():
    with open(".github/tasks.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    total = 0
    outputs = []

    for task in config["tasks"]:
        task_id = task["id"]
        with open(f"results/{task_id}.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        score = sum(t["score"] for t in data["tests"])
        total += score
        outputs.append(f"task{task_id[-2:]}_score={score}")

    outputs.append(f"total_score={total}")

    # Выводим в формате, совместимом с GITHUB_OUTPUT
    for line in outputs:
        print(line)

    # Также сохраняем в файлы, если нужно
    for task in config["tasks"]:
        task_num = task["id"][-2:]
        score = sum(t["score"] for t in json.load(open(f"results/{task['id']}.json"))["tests"])
        with open(f"task{task_num}_score.txt", "w") as f:
            f.write(f"TASK_SCORE={score}\n")

if __name__ == "__main__":
    main()
