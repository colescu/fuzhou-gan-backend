from dataclasses import dataclass
from itertools import product


@dataclass(frozen=True)
class GCSyllable:
    initial: str
    medial: str
    nucleus: str
    final: str
    tone: str

    PINYIN_TO_IPA_MAP = {
        "initial": {
            "": "",
            "b": "p",
            "p": "pʰ",
            "m": "m",
            "f": "f",
            "d": "t",
            "t": "tʰ",
            "n": "n",
            "l": "l",
            "g": "k",
            "k": "kʰ",
            "ng": "ŋ",
            "h": "h",
            "z": "ts",
            "c": "tsʰ",
            "s": "s",
        },
        "medial": {
            "": "",
            "j": "j",
            "w": "w",
        },
        "nucleus": {
            "aa": "a",
            "a": "ɐ",
            "e": "ɛ",  # or e
            "i": "i",  # or ɪ
            "o": "ɔ",  # or o
            "u": "u",  # or ʊ
            "oe": "œ",
            "eo": "ɵ",
            "yu": "y",
        },
        "final": {
            "": "",
            "i": "i",
            "u": "u",
            "m": "m",
            "n": "n",
            "ng": "ŋ",
            "p": "p",
            "t": "t",
            "k": "k",
        },
    }

    _RHYME_MAP = {
        nucleus_pinyin + final_pinyin: (nucleus_ipa, final_ipa)
        for ((nucleus_pinyin, nucleus_ipa), (final_pinyin, final_ipa)) in product(
            PINYIN_TO_IPA_MAP["nucleus"].items(), PINYIN_TO_IPA_MAP["final"].items()
        )
    }

    TONE_NOTATION_MAP = {
        "0": {"name": "輕聲", "numeral": "", "letter": "", "diacritic": ""},
        "1": {"name": "陰平", "numeral": "55", "letter": "˥", "diacritic": ""},
        "2": {"name": "陰上", "numeral": "35", "letter": "˧˥", "diacritic": ""},
        "3": {"name": "陰去", "numeral": "33", "letter": "˧", "diacritic": ""},
        "4": {"name": "陽平", "numeral": "21", "letter": "˨˩", "diacritic": ""},
        "5": {"name": "陽上", "numeral": "23", "letter": "˩˧", "diacritic": ""},
        "6": {"name": "陽去", "numeral": "22", "letter": "˨", "diacritic": ""},
        "7": {"name": "高陰入", "numeral": "5", "letter": "˥", "diacritic": ""},
        "8": {"name": "低陰入", "numeral": "3", "letter": "˧", "diacritic": ""},
        "9": {"name": "陽入", "numeral": "2", "letter": "˨", "diacritic": ""},
    }

    _CHECKED_TONE_MAP = {
        "1": "7",
        "3": "8",
        "6": "9",
    }

    @property
    def tuple(self) -> tuple[str, str, str, str, str]:
        return self.initial, self.medial, self.nucleus, self.final, self.tone

    @property
    def rhyme(self) -> str:
        return self.medial + self.nucleus + self.final

    @property
    def is_syllabic_nasal(self) -> bool:
        # only syllabic m, ŋ are allowed
        return (self.medial, self.nucleus, self.final) == (
            "",
            "",
            "",
        ) and self.initial in list("mŋ")

    @property
    def is_checked_tone(self) -> bool:
        return self.final in list("ptk")

    def __post_init__(self):
        if not self.is_syllabic_nasal:
            for part in ["initial", "medial", "nucleus", "final"]:
                if (
                    getattr(self, part)
                    not in GCSyllable.PINYIN_TO_IPA_MAP[part].values()
                ):
                    raise ValueError(
                        f"Illegal {part} in Cantonese syllable {self.ipa_raw}: {getattr(self, part)}."
                    )
        if (
            self.tone not in GCSyllable.TONE_NOTATION_MAP
            or (self.is_checked_tone and self.tone not in "0789")
            or (not self.is_checked_tone and self.tone in "789")
        ):
            raise ValueError(
                f"Illegal tone number in Cantonese syllable {self.ipa_raw}: {self.tone}."
            )

    @property
    def ipa_raw(self) -> str:
        return "".join(self.tuple)

    @property
    def pinyin(self, is_separate_checked_tone: bool) -> str:
        """
        Gets Jyutping representation.

        Example:
            GCSyllable("tsʰ", "ɐ", "u", "1") -> "cau1"
        """

        pass  # TODO

    @classmethod
    def parse_pinyin(cls, text: str) -> "GCSyllable":
        """
        Constructs GCSyllable from Jyutping representation.

        Example:
            "cau1" -> GCSyllable("tsʰ", "ɐ", "u", "1")
            "cau" -> GCSyllable("tsʰ", "ɐ", "u", "0")
        """

        tone = "0"
        if text[-1].isdigit():
            tone = text[-1]
            text = text[:-1]

        if text == "m":
            return GCSyllable("m", "", "", "", tone)
        if text == "ng":
            return GCSyllable("ŋ", "", "", "", tone)

        initial_length = 2
        while initial_length > 0:
            if text[:initial_length] in GCSyllable.PINYIN_TO_IPA_MAP["initial"]:
                break
            initial_length -= 1
        initial = GCSyllable.PINYIN_TO_IPA_MAP["initial"][text[:initial_length]]
        rhyme = text[initial_length:]

        medial = ""
        if rhyme[0] in list("jw"):
            medial = GCSyllable.PINYIN_TO_IPA_MAP["medial"][rhyme[0]]
            rhyme = rhyme[1:]

        nucleus, final = GCSyllable._RHYME_MAP.get(rhyme, (rhyme, ""))

        if (medial == "j" and nucleus == "i") or (medial == "w" and nucleus == "u"):
            medial = ""

        if final in list("ptk"):
            tone = GCSyllable._CHECKED_TONE_MAP.get(tone, tone)

        return GCSyllable(initial, medial, nucleus, final, tone)
