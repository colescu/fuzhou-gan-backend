import json
from typing import Type

import env_setup  # noqa
from Updater import Updater
from phonology import LANGUAGE_MAP, Language, Syllable


session = Updater()


def get_syllables(lang_en: Language) -> list[Type[Syllable]]:
    lang_data = LANGUAGE_MAP[lang_en]
    lang_cn = lang_data["name"]
    syllable_cls = lang_data["syllable_cls"]

    syllables: set[Type[Syllable]] = set()

    session.cursor.execute(f"SELECT 讀音 AS P FROM {lang_cn}")
    for row in session.data:
        syllables.add(syllable_cls.parse_pinyin(row["P"]))

    try:
        session.cursor.execute(f"SELECT 推導{lang_cn} AS P FROM 小韻")
        for row in session.data:
            if row["P"] is not None:
                syllables.add(syllable_cls.parse_pinyin(row["P"]))
    except Exception:
        pass

    # syllables not in dictionary
    if lang_en == "FG":
        for initial in ["", "t", "n", "tɕ", "tɕʰ", "ɕ"]:
            syllables.add(syllable_cls(initial, "", "y", "", "0"))
        for initial in ["p", "pʰ", "m", "f"]:
            syllables.add(syllable_cls(initial, "w", "i", "", "0"))
        for initial in ["tɕ", "tɕʰ", "ɕ"]:
            syllables.add(syllable_cls(initial, "j", "ɛ", "", "0"))
        syllables.add(syllable_cls("ŋ", "", "ɛ", "", "0"))
        syllables.add(syllable_cls("", "", "ɛ", "n", "0"))
        syllables.add(syllable_cls("n", "", "o", "", "0"))

    # order by pinyin
    return sorted(list(syllables), key=lambda syl: syl.pinyin())


ALL_SYLLABLES = {}

for lang_en in LANGUAGE_MAP:
    syllables = get_syllables(lang_en)

    rows = []
    seen = set()

    for syl in syllables:
        tuple_syl = syl.tuple[:4]
        ipa_strict = syl.ipa_strict_no_tone
        pinyin = syl.pinyin()
        if pinyin[-1].isdigit():
            pinyin = pinyin[:-1]
        if tuple_syl not in seen:
            seen.add(tuple_syl)
            data = {
                "tuple": tuple_syl,
                "ipaRaw": "".join(tuple_syl),
                "ipaStrict": ipa_strict,
            }
            match lang_en:
                case "JP":
                    for format in ["hira", "kata", "NR", "HR"]:
                        data[format] = syl.pinyin(format)
                case "KR":
                    for format in ["hangul", "RR"]:
                        data[format] = syl.pinyin(format)
                case _:
                    data["pinyin"] = pinyin
            rows.append(data)

    # for illustrative purpose
    if lang_en == "FG":
        rows.append(
            {
                "tuple": ["s", "", "ə", "n"],
                "ipaRaw": "sən",
                "ipaStrict": "sən",
                "pinyin": "seen",
            }
        )

    ALL_SYLLABLES[lang_en] = rows


with open("data/syllables.json", "w", encoding="utf-8") as f:
    json.dump(ALL_SYLLABLES, f, separators=(",", ":"), ensure_ascii=False)

print("導出現代方言音節數據完成！")
