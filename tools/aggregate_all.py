#!/usr/bin/env python3
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import encode_result_for_classroom

def main():
    with open(".github/tasks.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    for task in config["tasks"]:
        task_id = task["id"]
        task_name = task["name"]
        max_score = task["max_score"]

        with open(f"results/{task_id}.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        total_score = sum(t["score"] for t in data["tests"])

        aggregated = {
            "version": 1,
            "status": "pass" if total_score == max_score else "fail",
            "max_score": max_score,
            "tests": [{
                "name": task_name,
                "status": "pass" if total_score == max_score else "fail",
                "score": total_score,
                "output": f"Набрано баллов: {total_score}/{max_score}"
            }]
        }

        encoded = encode_result_for_classroom(aggregated)
        with open(f"{task_id}_aggregated.txt", "w") as f:
            f.write(f"AGGREGATED_RESULT={encoded}\n")

        print(f"Aggregated {task_id}: {total_score}/{max_score}")

if __name__ == "__main__":
    main()
