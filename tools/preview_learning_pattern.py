"""学習メニュー案の整合性を確認し、ランダムな提案をプレビューする。"""

import argparse
import json
import random
from collections import Counter
from pathlib import Path


CATALOG = Path(__file__).resolve().parents[1] / "docs" / "learning-patterns.json"
STAGES = ("short_response", "give_reasons", "express_opinion", "handle_questions")


def read_catalog():
    catalog = json.loads(CATALOG.read_text())
    patterns = catalog["patterns"]
    errors = []
    if len(patterns) != 100:
        errors.append("メニューが100件ではありません")
    if len({p["id"] for p in patterns}) != len(patterns):
        errors.append("メニューIDが重複しています")
    if len({p["title"] for p in patterns}) != len(patterns):
        errors.append("メニュー名が重複しています")
    pairs = {(p["topic_id"], p["mode"]) for p in patterns}
    if len(pairs) != 100 or set(Counter(p["topic_id"] for p in patterns).values()) != {5}:
        errors.append("20テーマ×5構成になっていません")
    for pattern in patterns:
        if pattern["duration_minutes"] != 10 or sum(s["minutes"] for s in pattern["steps"]) != 10:
            errors.append(f'{pattern["id"]} の所要時間が10分ではありません')
        if pattern["stage"] not in STAGES:
            errors.append(f'{pattern["id"]} の段階が不明です')
        if [s["kind"] for s in pattern["steps"]] != ["expressions", "listening", "conversation", "reflection"]:
            errors.append(f'{pattern["id"]} の学習順序が不正です')
        if any(s["minutes"] <= 0 or not s["task"] for s in pattern["steps"]):
            errors.append(f'{pattern["id"]} の練習内容が不足しています')
    for profile, stages in catalog["initial_stage_assignments"].items():
        if not stages or not set(stages).issubset(STAGES):
            errors.append(f"{profile} の開始段階が不正です")
        if not any(p["stage"] in stages for p in patterns):
            errors.append(f"{profile} に提案できるメニューがありません")
    if errors:
        raise ValueError("\n".join(errors))
    return catalog


def select_pattern(catalog, profile, seed=None):
    stages = catalog["initial_stage_assignments"][profile]
    candidates = [p for p in catalog["patterns"] if p["stage"] in stages]
    if not candidates:
        raise ValueError("現在の難易度に合うメニューがありません")
    return random.Random(seed).choice(candidates)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--profile", choices=("owner", "friends"), default="owner", help="本人用または友人用の開始状態（既定は本人用）")
    parser.add_argument("--seed", type=int, help="同じ提案を再現するための確認用の値")
    args = parser.parse_args()
    catalog = read_catalog()
    if args.check:
        print("PASS: 100件、20テーマ×5構成、ID・名前の一意性、各10分、学習順序を確認")
        print("未検証: 音声、対話全体、英語教材の人による確認、学習効果、iPhoneでの動作")
        return
    selected = select_pattern(catalog, args.profile, args.seed)
    print("学習メニュー案のプレビュー（アプリは未実装）")
    print("対象: " + ("ご本人" if args.profile == "owner" else "ご友人"))
    print(f'{selected["id"]}: {selected["title"]}（10分）')
    print(f'目標: {selected["goal"]}')
    for step in selected["steps"]:
        print(f'{step["minutes"]}分: {step["task"]}')


if __name__ == "__main__":
    main()
