from dataclasses import dataclass
from unicodedata import normalize


@dataclass(frozen=True)
class PMSyllable:
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
            "h": "h",  # or x
            "j": "tɕ",
            "q": "tɕʰ",
            "x": "ɕ",
            "zh": "ʈʂ",
            "ch": "ʈʂʰ",
            "sh": "ʂ",
            "r": "ɻ",
            "z": "ts",
            "c": "tsʰ",
            "s": "s",
        },
        "rhyme": {
            "a": ("", "a", ""),
            "ia": ("j", "a", ""),
            "ua": ("w", "a", ""),
            "o": ("", "o", ""),
            "uo": ("w", "o", ""),
            "e": ("", "ə", ""),
            "ie": ("j", "e", ""),
            "üe": ("y", "e", ""),
            "i": ("", "i", ""),  # or ɿ
            "u": ("", "u", ""),
            "ü": ("", "y", ""),
            "ai": ("", "a", "i"),
            "uai": ("w", "a", "i"),
            "ei": ("", "e", "i"),
            "ui": ("w", "e", "i"),
            "uei": ("w", "e", "i"),  # wei vs kui
            "ao": ("", "a", "u"),
            "iao": ("j", "a", "u"),
            "ou": ("", "o", "u"),
            "iu": ("j", "o", "u"),
            "iou": ("j", "o", "u"),  # you vs qiu
            "an": ("", "a", "n"),
            "ian": ("j", "e", "n"),
            "uan": ("w", "a", "n"),
            "üan": ("y", "e", "n"),
            "en": ("", "ə", "n"),
            "un": ("w", "ə", "n"),
            "uen": ("w", "ə", "n"),  # wen vs kun
            "in": ("", "i", "n"),
            "ün": ("", "y", "n"),
            "ang": ("", "a", "ŋ"),
            "iang": ("j", "a", "ŋ"),
            "uang": ("w", "a", "ŋ"),
            "eng": ("", "ə", "ŋ"),
            "ueng": ("w", "ə", "ŋ"),  # only weng
            "ing": ("", "i", "ŋ"),
            "ong": ("", "u", "ŋ"),
            "iong": ("j", "u", "ŋ"),
            "er": ("", "ə", "ɻ"),
        },
    }

    TONE_NOTATION_MAP = {
        "0": {"name": "輕聲", "numeral": "", "letter": "", "diacritic": ""},
        "1": {"name": "陰平", "numeral": "55", "letter": "˥", "diacritic": "̄"},
        "2": {"name": "陽平", "numeral": "35", "letter": "˧˥", "diacritic": "́"},
        "3": {"name": "陰上", "numeral": "214", "letter": "˨˩˦", "diacritic": "̌"},
        "4": {"name": "去聲", "numeral": "51", "letter": "˥˩", "diacritic": "̀"},
    }

    _DIACRITIC_TO_TONE_MAP = {
        info["diacritic"]: tone
        for tone, info in TONE_NOTATION_MAP.items()
        if tone in "1234"
    }

    @property
    def tuple(self) -> tuple[str, str, str, str, str]:
        return self.initial, self.medial, self.nucleus, self.final, self.tone

    @property
    def rhyme(self) -> str:
        return self.medial + self.nucleus + self.final

    def __post_init__(self):
        if self.initial not in PMSyllable.PINYIN_TO_IPA_MAP["initial"].values():
            raise ValueError(
                f"Illegal initial in Putonghua syllable {self.ipa_raw}: {self.initial}."
            )
        if (self.medial, self.nucleus, self.final) not in PMSyllable.PINYIN_TO_IPA_MAP[
            "rhyme"
        ].values():
            raise ValueError(
                f"Illegal rhyme in Putonghua syllable {self.ipa_raw}: {(self.medial, self.nucleus, self.final)}."
            )
        if self.tone not in "01234":
            return ValueError(
                f"Illegal tone number in Putonghua syllable {self.ipa_raw}: {self.tone}."
            )

    @property
    def ipa_raw(self) -> str:
        return "".join(self.tuple)

    @property
    def pinyin(self) -> str:
        """
        Example:
            PMSyllable("tɕʰ", "j", "o", "u", "1") -> "qiu1"
        """

        pass  # TODO

    @classmethod
    def parse_pinyin(cls, text: str) -> "PMSyllable":
        """
        Constructs PMSyllable from Pinyin representation.

        Examples:
            "qiu" -> PMSyllable("tɕʰ", "j", "o", "u", "")
            "qiū" -> PMSyllable("tɕʰ", "j", "o", "u", "1")
            "qiu0" -> PMSyllable("tɕʰ", "j", "o", "u", "0")
        """

        text = normalize("NFKD", text)
        tone = ""
        for i in range(len(text)):
            tmp = PMSyllable._DIACRITIC_TO_TONE_MAP.get(text[i], "")
            if tmp != "":
                tone = tmp
                text = text[:i] + text[i + 1 :]
                break
        if text[-1].isdigit():
            tone = text[-1]
            text = text[:-1]
        text = normalize("NFKC", text)  # for ü

        if text[:2] == "yu":
            text = "ü" + text[2:]
        if text[0] == "y":
            if text[1] == "i":
                text = text[1:]
            else:
                text = "i" + text[1:]
        if text[0] == "w":
            if text[1] == "u":
                text = text[1:]
            else:
                text = "u" + text[1:]
        if text[0] in "jqx" and text[1] == "u":
            text = text[0] + "ü" + text[2:]

        initial_length = 2
        while initial_length > 0:
            if text[:initial_length] in PMSyllable.PINYIN_TO_IPA_MAP["initial"]:
                break
            initial_length -= 1
        initial = PMSyllable.PINYIN_TO_IPA_MAP["initial"][text[:initial_length]]
        rhyme = text[initial_length:]

        medial, nucleus, final = PMSyllable.PINYIN_TO_IPA_MAP["rhyme"][rhyme]

        if nucleus == "i" and initial in ["zcsr"]:
            nucleus = "ɿ"

        return PMSyllable(initial, medial, nucleus, final, tone)
