import json

import env_setup  # noqa
from Updater import Updater
from phonology import LANGUAGE_MAP, Language


ENTRY_COLUMNS = [
    "字頭",
    "記錄讀音",
    "推導讀音",
    "層",
    "訓作",
    "釋義",
    "字頭號",
    "小韻號",
]


VARIANTS_MAP = {}
with open("data/variants.txt", "r", encoding="utf-8") as f:
    for row in f.read().split("\n"):
        for char in row:
            VARIANTS_MAP[char] = row


with open("data/MC.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    MC_SYLLABLES = {int(k): v for k, v in data.items()}


session = Updater()

MC_DICTIONARY = session.MC_dictionary


def match_MC_index(row: dict, lang_en: Language) -> int | None:
    char = row["字頭"]

    match_1 = [
        mc_entry
        for mc_entry in MC_DICTIONARY.get(char, [])
        if mc_entry["字頭號"] is not None
    ]
    if len(match_1) == 1:
        return match_1[0]["字頭號"]

    if len(match_1) > 1:
        match_2 = [
            mc_entry for mc_entry in match_1 if mc_entry["小韻號"] == row["小韻號"]
        ]
        if len(match_2) == 1:
            return match_2[0]["字頭號"]

        match_3 = [
            mc_entry
            for mc_entry in match_2
            if MC_SYLLABLES.get(mc_entry["小韻號"], {}).get(lang_en) == row["讀音"]
        ]
        if len(match_3) == 1:
            return match_3[0]["字頭號"]

    return None


def find_MC_index(row: dict, lang_en: Language) -> int | None:
    char = row["字頭"]

    index = match_MC_index(row, lang_en)
    if index is not None:
        return index

    if char in VARIANTS_MAP:
        matches = set(
            match_MC_index({**row, "字頭": variant}, lang_en)
            for variant in VARIANTS_MAP[char]
        )
        matches.discard(None)
        if len(matches) == 1:
            return list(matches)[0]

    return None


def to_entry(row: dict, lang_en: Language, MC_seen: set) -> dict:
    row["記錄讀音"] = row.get("讀音")

    MC_syllable = MC_SYLLABLES.get(row["小韻號"])
    row["推導讀音"] = MC_syllable[lang_en] if MC_syllable else None

    if row.get("音韻地位") is not None:
        row["釋義"] = None
    else:
        MC_index = find_MC_index(row, lang_en)
        row["字頭號"] = MC_index
        if MC_index:
            MC_seen.add(MC_index)

    return {key: row.get(key) for key in ENTRY_COLUMNS}


for lang_en in LANGUAGE_MAP:
    lang_cn = LANGUAGE_MAP[lang_en]["name"]

    MC_seen = set()

    session.cursor.execute(f"SELECT * FROM {lang_cn}")
    dictionary = [to_entry(row, lang_en, MC_seen) for row in session.data]

    session.cursor.execute("SELECT * FROM 字頭全")
    dictionary += [
        to_entry(row, lang_en, MC_seen)
        for row in session.data
        if row["字頭號"] not in MC_seen
    ]

    with open(f"data/{lang_en}.json", "w", encoding="utf-8") as f:
        json.dump(dictionary, f, separators=(",", ":"), ensure_ascii=False)
    print(f"導出{lang_cn}字典完成！")
