"""
This script fetches conversion data between Simplified and Traditional
Chinese, including variant forms, from the OpenCC and MCPDict repositories.
It saves the merged result (type: list[str]) to `/data/variants.txt`.
"""

import requests
from collections import defaultdict
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parent.parent / "data"


def fetch_OpenCC(file: str) -> list[str]:
    url = f"https://raw.githubusercontent.com/BYVoid/OpenCC/refs/heads/master/data/dictionary/{file}Characters.txt"
    try:
        response = requests.get(url)
        response.raise_for_status()
        result = []
        for line in response.text.splitlines():
            if line.strip() == "":
                continue
            char, variants = line.split("\t")
            result.append(char + "".join(variants.split()))
        return result
    except requests.RequestException as e:
        print(f"Failed to fetch OpenCC {file}: {e}")
        return []


def fetch_MCPDict() -> list[str]:
    url = "https://raw.githubusercontent.com/MaigoAkisame/MCPDict/refs/heads/master/res/raw/orthography_hz_variants.txt"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text.strip().splitlines()
    except requests.RequestException as e:
        print(f"Failed to fetch MCPDict variants: {e}")
        return []


class UnionFind:
    def __init__(self):
        self.parent: dict[str, str] = {}
        self.rank = {}

    def find(self, x: str) -> str:
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0
            return x
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: str, y: str) -> bool:
        root_x, root_y = self.find(x), self.find(y)
        if root_x == root_y:
            return False
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1
        return True

    @property
    def groups(self) -> list[set[str]]:
        group_map = defaultdict(set)
        for element in self.parent:
            root = self.find(element)
            group_map[root].add(element)
        return list(group_map.values())


def fetch_variants() -> None:
    OpenCC_T2S = fetch_OpenCC("TS")
    OpenCC_S2T = fetch_OpenCC("ST")
    MCPDict_variants = fetch_MCPDict()

    uf = UnionFind()
    for data in [MCPDict_variants, OpenCC_T2S, OpenCC_S2T]:
        for row in data:
            for i in range(1, len(row)):
                uf.union(row[0], row[i])

    groups = sorted(["".join(sorted(group)) for group in uf.groups])

    with open(DATA_PATH / "variants.txt", "w", encoding="utf-8") as file:
        file.write("\n".join(groups))


if __name__ == "__main__":
    fetch_variants()
