"""
This file defines the `Updater` class to facilitate the updating of
the Fuzhou Gan database.
"""

import sqlite3
import csv
from collections import defaultdict
from functools import cached_property
from pathlib import Path

import questionary

from 推導撫州話 import 推導撫州話
from FGSyllable import FGSyllable


DATA_PATH = Path(__file__).resolve().parent.parent / "data"


class Updater:
    def __init__(self, db_name: str = "撫州話.sqlite3", get_reflex=推導撫州話):
        self.conn = sqlite3.connect(DATA_PATH / db_name)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.get_reflex = get_reflex

    def __del__(self):
        self.conn.commit()
        self.conn.close()

    @property
    def data(self) -> list[dict[str, any]]:
        return [dict(row) for row in self.cursor.fetchall()]

    @cached_property
    def dictionary(self) -> dict[str, list[dict[str, any]]]:
        """切韻字典"""
        self.cursor.execute("SELECT * FROM 字頭全;")
        dictionary = defaultdict(list)
        for row in self.data:
            dictionary[row["字頭"]].append(row)
        return dictionary

    @staticmethod
    def show_FG_syllable(
        syllable_data: dict[str, str], include_tone: bool = True
    ) -> str:
        syllable = (
            syllable_data["聲母"]
            + syllable_data["介音"]
            + syllable_data["韻腹"]
            + syllable_data["韻尾"]
        )
        if include_tone:
            return syllable + syllable_data["聲調"]
        else:
            return syllable

    @staticmethod
    def show_MC_entry(entry: dict[str, any]) -> str:
        return " ".join(
            [
                entry["字頭"],
                str(entry["字頭號"]),
                entry["音韻地位"],
                entry["推導撫州話"],
                entry["釋義"],
            ]
        )

    def export(self, filename: str = "dictionary") -> None:
        self.cursor.execute("SELECT * FROM 導出;")
        columns = [description[0] for description in self.cursor.description]
        with open(
            DATA_PATH / f"{filename}.csv", mode="w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.DictWriter(file, fieldnames=columns)
            writer.writeheader()
            for row in self.data:
                writer.writerow(dict(row))
        print("導出完成！")

    def update_reflexes(self) -> None:
        """推導所有小韻的撫州話"""
        self.cursor.execute("SELECT * FROM 小韻全;")
        count = 0
        for row in self.data:
            expected_reflex = Updater.show_FG_syllable(self.get_reflex(row))
            self.cursor.execute(
                "UPDATE 小韻 SET 推導撫州話 = ? WHERE 小韻號 = ?;",
                (expected_reflex, row["小韻號"]),
            )
            if row["推導撫州話"] != expected_reflex:
                count += 1
        print(f"推導撫州話完成！共更新 {count} 個小韻。")
        self.__dict__.pop("dictionary", None)  # dictionary needs update

    def compare_inventories(self) -> None:
        """比較推導音節集與記錄音節集（不計聲調）"""

        self.cursor.execute("SELECT * FROM 小韻全;")
        推導音節 = set()
        for row in self.data:
            推導音節.add(row["推導撫州話"][:-1])  # 除去聲調

        self.cursor.execute("SELECT * FROM 撫州話;")
        收錄音節 = set()
        for row in self.data:
            收錄音節.add(Updater.show_FG_syllable(row, include_tone=False))

        def show_set(s: set[str]) -> str:
            return ", ".join(sorted(s))

        print(
            "\n".join(
                [
                    f"推導音節數：{len(推導音節)} ；收錄音節數：{len(收錄音節)}",
                    f"推導出但不存在的音節：{show_set(推導音節.difference(收錄音節))}",
                    f"存在但推導不出的音節：{show_set(收錄音節.difference(推導音節))}",
                ]
            )
        )

    def _predict_MC(self, row: dict[str, any]) -> list[dict[str, any]]:
        """推導撫州話字條的切韻字頭號"""

        def is_match(推導音: str, 收錄音: str) -> bool:
            return (int(推導音[-1]) + 1) // 2 == (int(收錄音[-1]) + 1) // 2

        字 = row["字頭"]
        收錄撫州話 = Updater.show_FG_syllable(row)

        entries = self.dictionary[字]
        if len(entries) == 1:
            return entries

        exact_matches = [
            entry for entry in entries if entry["推導撫州話"] == 收錄撫州話
        ]
        if len(exact_matches) > 0:
            return exact_matches

        matches = [
            entry for entry in entries if is_match(entry["推導撫州話"], 收錄撫州話)
        ]
        if len(matches) > 0:
            return matches

        return entries

    def update_MC_index(self) -> None:
        """推導所有撫州話字條的切韻字頭號"""
        self.cursor.execute("SELECT ROWID, * FROM 撫州話 WHERE 訓作 IS NULL;")
        count = 0
        for row in self.data:
            MC_entries = self._predict_MC(row)
            if len(MC_entries) == 1 and MC_entries[0]["字頭號"] != row["字頭號"]:
                self.cursor.execute(
                    "UPDATE 撫州話 SET 字頭號 = ? WHERE ROWID = ?;",
                    (MC_entries[0]["字頭號"], row["rowid"]),
                )
                count += 1
        print(f"推導撫州話字頭號完成！共更新 {count} 個字條。")

    def add_MC_index(self, 字: str) -> tuple[bool, str]:
        """手動選擇撫州話字條的切韻字頭號"""

        self.cursor.execute("SELECT ROWID, * FROM 撫州話 WHERE 字頭 = ?;", (字,))
        data = self.data
        if len(data) == 0:
            print("撫州話字典未收錄該字！")
            return False, "撫州話字典未收錄"

        unsure = False
        updated = False
        for row in data:
            if row["字頭號"] is not None:
                continue

            print(f"{字} 收錄音：{Updater.show_FG_syllable(row)}")

            entries = self._predict_MC(row)
            if len(entries) == 0:
                print("切韻未收錄該字！")
                return False, "切韻未收錄"

            choice = questionary.select(
                "請選擇：",
                choices=[
                    {"name": Updater.show_MC_entry(entry), "value": entry}
                    for entry in entries
                ]
                + [{"name": "以上都不對 / 不確定", "value": {}}],
            ).ask()
            if choice is None:
                raise KeyboardInterrupt

            if "字頭號" in choice:
                self.cursor.execute(
                    "UPDATE 撫州話 SET 字頭號 = ? WHERE ROWID = ?;",
                    (choice["字頭號"], row["rowid"]),
                )
                updated = True
            else:
                unsure = True

        return updated, "不確定" if unsure else "已添加切韻字頭號"

    def add_entry(self, 字: str) -> tuple[bool, str]:
        """手動錄入撫州話字條"""

        self.cursor.execute("SELECT * FROM 撫州話 WHERE 字頭 = ?;", (字,))
        data = self.data
        if len(data) != 0:
            print(
                "已收錄讀音："
                + ", ".join(Updater.show_FG_syllable(row) for row in data)
            )
            if not questionary.confirm("是否要錄入讀音？", default=False).ask():
                return False, "用戶終止"

        MC_index = None
        FG_syllable = None

        entries = self.dictionary[字]
        if len(entries) > 0:
            choice = questionary.select(
                "請選擇切韻字條：",
                choices=[
                    {"name": Updater.show_MC_entry(entry), "value": entry}
                    for entry in entries
                ]
                + [{"name": "以上都不是 / 不確定", "value": {}}],
            ).ask()
            if choice is None:
                raise KeyboardInterrupt

            if "字頭號" in choice:
                MC_index = choice["字頭號"]

                if questionary.confirm("是否要使用推導音？").ask():
                    FG_syllable = FGSyllable.parse_ipa(choice["推導撫州話"])

        if FG_syllable is None:
            text = input("請輸入讀音：")

            try:
                syllable_from_ipa = FGSyllable.parse_ipa(text)
            except ValueError:
                syllable_from_ipa = None

            try:
                syllable_from_pinyin = FGSyllable.parse_pinyin(text)
            except ValueError:
                syllable_from_pinyin = None

            match (syllable_from_ipa is not None, syllable_from_pinyin is not None):
                case (True, True) if syllable_from_ipa != syllable_from_pinyin:
                    choice = questionary.select(
                        "剛才輸入的是音標還是拼音？",
                        choices=[
                            {
                                "name": f"音標 ({syllable_from_ipa.ipa_raw})",
                                "value": syllable_from_ipa,
                            },
                            {
                                "name": f"拼音 ({syllable_from_pinyin.ipa_raw})",
                                "value": syllable_from_pinyin,
                            },
                        ],
                    ).ask()
                    if choice is None:
                        raise KeyboardInterrupt
                    FG_syllable = choice
                case (True, _):
                    FG_syllable = syllable_from_ipa
                case (False, True):
                    FG_syllable = syllable_from_pinyin
                case (False, False):
                    print("請輸入正確讀音！")
                    return False, "用戶輸入錯誤"

            if not text[-1].isnumeric() and FG_syllable.tone == "1":
                choice = questionary.select(
                    "是否是陽去？",
                    choices=[
                        {"name": "陰平 1", "value": "1"},
                        {"name": "陽去 6", "value": "6"},
                    ],
                ).ask()
                if choice is None:
                    raise KeyboardInterrupt
                FG_syllable = FGSyllable(
                    FG_syllable.initial,
                    FG_syllable.medial,
                    FG_syllable.nucleus,
                    FG_syllable.coda,
                    choice,
                )

        print(f"讀音信息：{', '.join(FG_syllable.tuple)}")

        def get_optional_input(label):
            text = input(f"{label}：").strip()
            return text or None

        文白新 = 訓作 = 釋義 = None
        if questionary.confirm("是否要附加信息？", default=False).ask():
            文白新, 訓作, 釋義 = map(get_optional_input, ["文白新", "訓作", "釋義"])

        self.cursor.execute(
            "INSERT INTO 撫州話 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
            (字, MC_index, *FG_syllable.tuple, 文白新, 訓作, 釋義),
        )
