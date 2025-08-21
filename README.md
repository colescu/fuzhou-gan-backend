This repository stores the (static) backend of [Colescu's Fuzhou Gan website](https://colescu.github.io/fuzhou-gan/).

本倉庫用於存儲[苦芋頭的撫州話網站](https://colescu.github.io/fuzhou-gan/)的數據庫與部分後端處理脚本。

# 數據

主數據庫爲 `data/hanzi.sqlite3` 。

目前收錄的語言及對應代號：

- `MC` - 中古漢語（依《廣韻》）
- `FG` - 撫州話（贛語）
- `PM` - 普通話（官話）
- `GC` - 廣州話（粵語）
- `SW` - 上海話（吳語）
- `MH` - 梅縣話（客家話）
- `JP` - 日本語
- `KR` - 朝鮮語
- `VN` - 越南語

主要的數據內容及其來源：

- 讀音：

  - 中古漢語：[韻典網](https://ytenx.org)、[MCPDict](https://github.com/MaigoAkisame/MCPDict/blob/master/assets/databases/mcpdict.zip)（第一版用的是 [qieyun-sqlite](https://github.com/nk2028/qieyun-sqlite)）
  - 撫州話：基於[漢字音典](https://github.com/osfans/MCPDict/tree/master)的[臨川.tsv](https://github.com/osfans/MCPDict/blob/master/tools/tables/output/%E8%87%A8%E5%B7%9D.tsv)、[臨川上頓渡.tsv](https://github.com/osfans/MCPDict/blob/master/tools/tables/output/%E8%87%A8%E5%B7%9D%E4%B8%8A%E9%A0%93%E6%B8%A1.tsv)，做了大量修改，並會長期更新
  - 普通話、廣州話、上海話、日本語、朝鮮語、越南語：[MCPDict](https://github.com/MaigoAkisame/MCPDict/blob/master/assets/databases/mcpdict.zip)
  - 梅縣話：[薪典](https://www.syndict.com)、[漢字音典](https://github.com/osfans/MCPDict/tree/master)的[梅縣.tsv](https://github.com/osfans/MCPDict/blob/master/tools/tables/output/%E6%A2%85%E7%B8%A3.tsv)，做了少量修改

- 從中古音推導現代音（見表格 `小韻`）：

  - 撫州話、梅縣話：本人整理，見 `src/推導*.py`
  - 普通話、廣州話：[Wiktionary](https://en.wiktionary.org/wiki/Module:ltc-pron/predict)
  - 上海話：[Nyoeghau](https://zhuanlan.zhihu.com/p/386456940)
  - 日本語、朝鮮語、越南語：待施工

- 現代音對應的中古音（字典中 `小韻號` 一欄）：本人整理

  > 分析歷史音變需確定現代音與中古音的對應關係，然而由於多音字、假借字、認字認半邊等現象，這件事情並不好做。目前數據庫中只有撫州話的數據較爲完整、可靠。

此外，簡繁轉換與異體字數據（供前端使用，後端只用大陸繁體）來自 [OpenCC](https://github.com/BYVoid/OpenCC/tree/master/data/dictionary) 與 [MCPDict](https://github.com/MaigoAkisame/MCPDict/blob/master/res/raw/orthography_hz_variants.txt)。

# 音韻分析

爲方便音韻分析與前端顯示，本人寫了一些 Python 類（代碼見 `src/phonology` ，接口見 `Syllable.py`），主要提供以下功能：

- 拆解音節 (`Syllable`) 爲聲母 (`initial`) 、介音 (`medial`) 、韻腹 (`nucleus`) 、韻尾 (`coda`) 、聲調 (`tone`) 。不同語言支持不同記法，詳見各文件開頭的說明。例如撫州話音節類 `FGSyllable` 支持拆解拼音或音標（音標需符合本數據庫的格式）。

- 轉換記法。例如撫州話音節類 `FGSyllable` 支持拼音與音標之間的轉換，其中拼音又可選擇是否用變音符（拼音 `qiáng` 或 `qiang2`、音標 `tɕʰjaŋ2`）。實際使用時需先拆解，例如：

  ```python
  from phonology import FGSyllable

  syllable = FGSyllable.parse_ipa("tɕʰjaŋ2")
  print(syllable.pinyin(tone_diacritic=True))  # qiáng
  ```

拆解後的音節也保存在數據庫中，方便直接用 SQL 查詢。推薦使用 [DB Browser for SQLite](https://sqlitebrowser.org) 。例如查詢撫州話中讀 ɛ 的魚韻字：

```sql
WITH DICT AS (
  SELECT *
  FROM 撫州話
  LEFT JOIN 小韻全
  WHERE 撫州話.小韻號 = 小韻全.小韻號
)
SELECT * FROM DICT
WHERE 韻系 = '魚' AND 韻腹 = 'ɛ';
```

若用 Python 運行 SQL，可借助 `Updater` 類（見 `src/Updater.py`）：

```python
from Updater import Updater

# 連接數據庫
session = Updater(db_name="hanzi.sqlite3", lang_en="FG")

# 運行 SQL
session.cursor.execute("sql_query")
print(session.data)  # 查詢結果 (type: list[dict[str, Any]])

# 查字
dct = session.get_dictionary(language="FG")
print(dct["撫"])  # (type: list[dict[str, Any]])

# 保存並斷開連接
del session
```

# 更新方法

運行 `update.bat` 以更新數據庫與導出文件。
