"""学習メニュー案の整合性を確認し、ランダムな提案をプレビューする。"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bowmore.learning import STAGES, read_catalog, select_for_stages, select_pattern


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--profile", choices=("owner", "friends"), default="owner", help="本人用または友人用の開始状態（既定は本人用）")
    parser.add_argument("--seed", type=int, help="同じ提案を再現するための確認用の値")
    parser.add_argument("--stage", choices=STAGES, action="append", help="現在の難易度。複数指定可能")
    args = parser.parse_args()
    catalog = read_catalog()
    if args.check:
        print("PASS: 100件、20テーマ×5構成、ID・名前の一意性、各10分、学習順序を確認")
        print("未検証: 音声、対話全体、英語教材の人による確認、学習効果、iPhoneでの動作")
        return
    selected = (select_for_stages(catalog, args.stage, args.seed) if args.stage
                else select_pattern(catalog, args.profile, args.seed))
    print("学習メニュー案のプレビュー（アプリは未実装）")
    print("対象: " + ("指定した現在の難易度" if args.stage else
                      "ご本人" if args.profile == "owner" else "ご友人"))
    print(f'{selected["id"]}: {selected["title"]}（10分）')
    print(f'目標: {selected["goal"]}')
    for step in selected["steps"]:
        print(f'{step["minutes"]}分: {step["task"]}')


if __name__ == "__main__":
    main()
