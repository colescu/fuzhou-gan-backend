from typing import Type, TypedDict, Literal

from .Syllable import Syllable
from .FGSyllable import FGSyllable
from .PMSyllable import PMSyllable
from .GCSyllable import GCSyllable
from .SWSyllable import SWSyllable
from .MHSyllable import MHSyllable
from .JPSyllable import JPSyllable
from .KRSyllable import KRSyllable
from .VNSyllable import VNSyllable


# 贛官粵吳客日朝越
Language = Literal["FG", "PM", "GC", "SW", "MH", "JP", "KR", "VN"]


class LanguageData(TypedDict):
    name: str
    syllable_cls: Type[Syllable]


LANGUAGE_MAP: dict[Language, LanguageData] = {
    "FG": {"name": "撫州話", "syllable_cls": FGSyllable},
    "PM": {"name": "普通話", "syllable_cls": PMSyllable},
    "GC": {"name": "廣州話", "syllable_cls": GCSyllable},
    "SW": {"name": "上海話", "syllable_cls": SWSyllable},
    "MH": {"name": "梅縣話", "syllable_cls": MHSyllable},
    "JP": {"name": "日本語", "syllable_cls": JPSyllable},
    "KR": {"name": "朝鮮語", "syllable_cls": KRSyllable},
    "VN": {"name": "越南語", "syllable_cls": VNSyllable},
}


__all__ = [
    LANGUAGE_MAP,
    FGSyllable,
    PMSyllable,
    GCSyllable,
    SWSyllable,
    MHSyllable,
    JPSyllable,
    KRSyllable,
    VNSyllable,
]
