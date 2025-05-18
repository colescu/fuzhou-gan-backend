"""
This script fetches the data for conversion between Simplified and
Traditional Chinese from the OpenCC repository, and saves it as
`variants.csv`.
"""

import requests
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parent.parent / "data"


def parse(file: str) -> dict[str, list[str]]:
    url = f"https://raw.githubusercontent.com/BYVoid/OpenCC/refs/heads/master/data/dictionary/{file}Characters.txt"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.text

        result = {}
        for row in data.split("\n"):
            if row != "":
                char, variants = row.split("\t")
                variants = variants.split(" ")
                result[char] = variants

        return result

    else:
        print(f"Failed to fetch: {response.status_code}")


def fetch_variants() -> None:
    T2S = parse("TS")
    S2T = parse("ST")

    result = {}

    for char in S2T:
        result[char] = S2T[char]

    for char in T2S:
        s = T2S[char]
        curr = []
        for c in s:
            if c in S2T:
                curr += S2T[c]
        if len(set(curr)) > 1:
            result[char] = list(dict.fromkeys([char] + curr))

    with open(DATA_PATH / "variants.csv", "w", encoding="utf-8") as file:
        for c in result:
            file.write(c + "," + "|".join(result[c]) + "\n")


if __name__ == "__main__":
    fetch_variants()
