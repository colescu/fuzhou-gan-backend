"""
This file defines the `FGSyllable` class for processing Fuzhou Gan (FG)
syllables. In particular, it provides conversion between IPA and Pinyin
representations in Fuzhou Gan.

Supports:
  - Automatic validation of the syllable
  - Representations in IPA or Pinyin
  - Constructors from IPA or Pinyin
"""

from dataclasses import dataclass
from unicodedata import normalize


@dataclass(frozen=True)
class FGSyllable:
    initial: str
    medial: str
    nucleus: str
    final: str
    tone: str

    IPA_TO_PINYIN_MAP = {
        "initial": {
            "": "",
            "p": "b",
            "pʰ": "p",
            "m": "m",
            "f": "f",
            "t": "d",
            "tʰ": "t",
            "n": "n",
            "l": "l",
            "k": "g",
            "kʰ": "k",
            "ŋ": "ng",
            "h": "h",
            "tɕ": "j",
            "tɕʰ": "q",
            "ɕ": "x",
            "ts": "z",
            "tsʰ": "c",
            "s": "s",
        },
        "medial": {
            "": "",
            "j": "i",
            "w": "u",
            "ɥ": "y",
        },
        "nucleus": {
            "a": "a",
            "o": "o",
            "ɛ": "e",
            "i": "i",
            "ɿ": "i",
            "u": "u",
            "y": "y",
        },
        "final": {
            "": "",
            "m": "m",
            "n": "n",
            "ŋ": "ng",
            "p": "p",
            "t": "t",
            "k": "k",
            "ʔ": "h",
            "i": "i",
            "u": "u",
        },
    }

    PINYIN_TO_IPA_MAP = {
        part: {pinyin: ipa for ipa, pinyin in dct.items()}
        for part, dct in IPA_TO_PINYIN_MAP.items()
    }

    TONE_NOTATION_MAP = {
        "0": {"name": "輕聲", "numeral": "", "letter": "", "diacritic": ""},
        "1": {"name": "陰平", "numeral": "22", "letter": "˨", "diacritic": "̄"},
        "2": {"name": "陽平", "numeral": "24", "letter": "˨˦", "diacritic": "́"},
        "3": {"name": "陰上", "numeral": "45", "letter": "˦˥", "diacritic": "̂"},
        "5": {"name": "陰去", "numeral": "52", "letter": "˥˨", "diacritic": "̀"},
        "6": {"name": "陽去", "numeral": "22", "letter": "˨", "diacritic": "̄"},
        "7": {"name": "陰入", "numeral": "2", "letter": "˨", "diacritic": "̄"},
        "8": {"name": "陽入", "numeral": "5", "letter": "˥", "diacritic": "̂"},
    }

    _DIACRITIC_TO_TONE_MAP = {
        info["diacritic"]: tone
        for tone, info in TONE_NOTATION_MAP.items()
        if tone in "1235"
    }

    @property
    def tuple(self) -> tuple[str, str, str, str, str]:
        return self.initial, self.medial, self.nucleus, self.final, self.tone

    @property
    def rhyme(self) -> str:
        return self.medial + self.nucleus + self.final

    @property
    def is_syllabic_nasal(self) -> bool:
        # only syllabic ŋ is allowed
        return (self.initial, self.medial, self.nucleus, self.final) == (
            "ŋ",
            "",
            "",
            "",
        )

    @property
    def is_checked_tone(self) -> bool:
        return self.final in list("ptkʔ")

    def __post_init__(self):
        """
        Checks that all parts are in the corresponding inventory and
        the tone number is legal.

        TODO: Add phonological constraints.
        """

        if not self.is_syllabic_nasal:
            for part in ["initial", "medial", "nucleus", "final"]:
                if getattr(self, part) not in FGSyllable.IPA_TO_PINYIN_MAP[part]:
                    raise ValueError(
                        f"Illegal {part} in Fuzhou Gan syllable {self.ipa_raw}: {getattr(self, part)}."
                    )
        if (
            self.tone not in FGSyllable.TONE_NOTATION_MAP
            or (self.is_checked_tone and self.tone not in "078")
            or (not self.is_checked_tone and self.tone in "78")
        ):
            raise ValueError(
                f"Illegal tone number in Fuzhou Gan syllable {self.ipa_raw}: {self.tone}."
            )

    @property
    def ipa_raw(self) -> str:
        return "".join(self.tuple)

    @property
    def pinyin(self) -> str:
        """
        Examples:
            FGSyllable("tɕʰ", "j", "a", "ŋ", "3") -> "qiâng"
            FGSyllable("ŋ", "", "", "", "2") -> "ńg"
        """

        if self.is_syllabic_nasal:
            return (
                normalize(
                    "NFKC",
                    "n" + FGSyllable.TONE_NOTATION_MAP[self.tone]["diacritic"],
                )
                + "g"
            )
        return "".join(
            [
                FGSyllable.IPA_TO_PINYIN_MAP["initial"][self.initial],
                FGSyllable.IPA_TO_PINYIN_MAP["medial"][self.medial],
                normalize(
                    "NFKC",
                    FGSyllable.IPA_TO_PINYIN_MAP["nucleus"][self.nucleus]
                    + FGSyllable.TONE_NOTATION_MAP[self.tone]["diacritic"],
                ),
                FGSyllable.IPA_TO_PINYIN_MAP["final"][self.final],
            ]
        )

    @classmethod
    def parse_ipa(cls, text: str) -> "FGSyllable":
        """
        Constructs FGSyllable from raw IPA representation.

        CAUTION: Always include the tone number.

        Example:
            "tɕʰjaŋ3" -> FGSyllable("tɕʰ", "j", "a", "ŋ", "3")
        """

        initial_length = 3
        while initial_length > 0:
            if text[:initial_length] in FGSyllable.IPA_TO_PINYIN_MAP["initial"]:
                break
            initial_length -= 1
        initial = text[:initial_length]

        def parse_rhyme(rhyme: str) -> tuple[str, str, str]:
            match len(rhyme):
                case 3:
                    return tuple(rhyme)
                case 2:
                    if rhyme[1] in FGSyllable.IPA_TO_PINYIN_MAP[
                        "final"
                    ] and rhyme not in [
                        "ju",
                        "wi",
                        "ɥi",
                    ]:
                        return "", *tuple(rhyme)
                    else:
                        return *tuple(rhyme), ""
                case 1:
                    return "", *tuple(rhyme), ""
            return "", rhyme, ""

        medial, nucleus, final = parse_rhyme(text[initial_length:-1])

        tone = text[-1]

        return FGSyllable(initial, medial, nucleus, final, tone)

    @classmethod
    def parse_pinyin(cls, text: str) -> "FGSyllable":
        """
        Constructs FGSyllable from Pinyin representation.

        CAUTION: Tone 6 is indistinguishable from Tone 1 in the
        diacritic notation. Add "6" to disambiguate.

        Examples:
            "qiāng" -> FGSyllable("tɕʰ", "j", "a", "ŋ", "1")
            "qiang" -> FGSyllable("tɕʰ", "j", "a", "ŋ", "0")
            "qiang6" -> FGSyllable("tɕʰ", "j", "a", "ŋ", "6")
            "qiāng6" -> FGSyllable("tɕʰ", "j", "a", "ŋ", "6")
        """

        text = normalize("NFKD", text)
        tone = "0"
        for i in range(len(text)):
            tmp = FGSyllable._DIACRITIC_TO_TONE_MAP.get(text[i], "")
            if tmp != "":
                tone = tmp
                text = text[:i] + text[i + 1 :]
                break
        if text[-1].isdigit():
            tone = text[-1]
            text = text[:-1]

        initial_length = 2
        while initial_length > 0:
            if text[:initial_length] in FGSyllable.PINYIN_TO_IPA_MAP["initial"]:
                break
            initial_length -= 1
        initial = text[:initial_length]
        rhyme = text[initial_length:]

        def parse_rhyme(rhyme: str) -> list[str]:
            match len(rhyme) if rhyme[-2:] != "ng" else len(rhyme) - 1:
                case 3:
                    return [rhyme[0], rhyme[1], rhyme[2:]]
                case 2:
                    if rhyme[1:] in FGSyllable.PINYIN_TO_IPA_MAP[
                        "final"
                    ] and rhyme not in [
                        "iu",
                        "ui",
                    ]:
                        return ["", rhyme[0], rhyme[1:]]
                    else:
                        return [rhyme[0], rhyme[1:], ""]
                case 1:
                    return ["", rhyme, ""]
            return ["", rhyme, ""]

        medial, nucleus, final = parse_rhyme(rhyme)

        # repetitive!
        initial = FGSyllable.PINYIN_TO_IPA_MAP["initial"].get(initial, initial)
        medial = FGSyllable.PINYIN_TO_IPA_MAP["medial"].get(medial, medial)
        nucleus = FGSyllable.PINYIN_TO_IPA_MAP["nucleus"].get(nucleus, nucleus)
        final = FGSyllable.PINYIN_TO_IPA_MAP["final"].get(final, final)

        if nucleus == "ɿ" and not (medial == "" and initial in ["ts", "tsʰ", "s", "l"]):
            nucleus = "i"

        if final in list("ptkʔ"):
            match tone:
                case "1":
                    tone = "7"
                case "3":
                    tone = "8"

        return FGSyllable(initial, medial, nucleus, final, tone)
