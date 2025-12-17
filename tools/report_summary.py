#!/usr/bin/env python3
import json
import sys
import os
import argparse
from pathlib import Path
import os

def extract_and_output_env():
    task_files = ["task_01", "task_02", "task_03"]
    outputs = []

    for tf in task_files:
        path = f"./aggregated/{tf}_aggregated.txt"
        encoded = ""
        if os.path.exists(path):
            with open(path) as f:
                content = f.read()
            if "AGGREGATED_RESULT=" in content:
                encoded = content.split("AGGREGATED_RESULT=")[1].strip()
        outputs.append(f"{tf}_aggregated={encoded}")

    # Записываем в GITHUB_OUTPUT файл (новый способ)
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            for line in outputs:
                f.write(line + "\n")
    else:
        # Для локального тестирования — выводим в stdout (но без ::set-output!)
        for line in outputs:
            print(line)

def generate_summary():
    with open(".github/tasks.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    # Считаем баллы
    total_score = 0
    max_total = 0
    task_scores = {}

    for task in config["tasks"]:
        task_id = task["id"]
        max_score = task["max_score"]
        max_total += max_score
        with open(f"results/{task_id}.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        score = sum(t["score"] for t in data["tests"])
        task_scores[task_id] = score
        total_score += score

    percentage = int(100 * total_score / max_total) if max_total > 0 else 0

    # Генерация Markdown
    summary = []
    summary.append("## 📊 ИТОГОВЫЙ ОТЧЕТ ПО ВСЕМ ЗАДАНИЯМ\n")
    summary.append("### 📈 Сводная таблица\n")
    summary.append("| Задание | Баллы | Максимум | Статус |")
    summary.append("|---------|-------|----------|--------|")

    for task in config["tasks"]:
        tid = task["id"]
        name = task["name"]
        score = task_scores[tid]
        max_score = task["max_score"]
        status = "✅" if score == max_score else "⚠️"
        summary.append(f"| **{name}** | {score} | {max_score} | {status} |")

    summary.append(f"| **ВСЕГО** | **{total_score}** | **{max_total}** | **{percentage}%** |")
    summary.append("")

    summary.append("### 📁 Найденные файлы:\n")
    for task in config["tasks"]:
        f = task["file"]
        if os.path.exists(f):
            summary.append(f"✅ **{f}** - найден")
        else:
            summary.append(f"❌ **{f}** - не найден")

    summary.append("")
    summary.append(f"### 🏆 Итоговая оценка: **{total_score} / {max_total}**")
    summary.append("")
    if total_score == max_total:
        summary.append("🎉 **ПОЗДРАВЛЯЕМ! Все задачи выполнены на 100%!**")
    else:
        summary.append("💡 **Есть что улучшить! Смотри детали тестов.**")
    summary.append("")
    summary.append(f"**GitHub Classroom: {total_score}/{max_total} баллов**")
    summary.append("")
    summary.append("*Автоматическая проверка завершена*")

    # Запись в GITHUB_STEP_SUMMARY
    with open(os.environ.get("GITHUB_STEP_SUMMARY", "/dev/stdout"), "a") as f:
        f.write("\n".join(summary))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--extract", action="store_true")
    parser.add_argument("--output-env", action="store_true")
    parser.add_argument("--generate-summary", action="store_true")

    args = parser.parse_args()

    if args.extract and args.output_env:
        extract_and_output_env()
    elif args.generate_summary:
        generate_summary()
    else:
        print("Укажите действие: --extract --output-env или --generate-summary")

if __name__ == "__main__":
    main()
