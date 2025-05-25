本倉庫用於存儲[撫州話網站](https://colescu.github.io/fuzhou-gan/)的數據庫與後端處理脚本。

This repository stores the locally served backend of my [Fuzhou Gan website](https://colescu.github.io/fuzhou-gan/).

# 數據

關於撫州話的數據：

- `data\撫州話.sqlite3`：主數據庫（模式見 `data\schema.sql`）
- `src\推導撫州話.py`：中古漢語推導撫州話的規則

在構建過程中采用了以下數據作爲基準：

- 中古漢語：[qieyun-sqlite](https://github.com/nk2028/qieyun-sqlite)、[韻典網](https://ytenx.org)
- 撫州話：[漢字音典](https://github.com/osfans/MCPDict/tree/master)的[臨川.tsv](https://github.com/osfans/MCPDict/blob/master/tools/tables/output/%E8%87%A8%E5%B7%9D.tsv)、[臨川上頓渡.tsv](https://github.com/osfans/MCPDict/blob/master/tools/tables/output/%E8%87%A8%E5%B7%9D%E4%B8%8A%E9%A0%93%E6%B8%A1.tsv)
- 簡繁轉換：[OpenCC](https://github.com/BYVoid/OpenCC/tree/master/data/dictionary)
- 中古漢語推導普通話、粵語：[Wiktionary](https://en.wiktionary.org/wiki/Module:ltc-pron/predict)

# Usage

Run `update.bat` to update the output files `dictionary.csv` and `variants.csv`.

To edit the database, either use a SQLite server such as [DB Browser for SQLite](https://sqlitebrowser.org) (to run SQL) or use the `Updater` class (in Python with `sqlite3`).

### The `Updater` class

- Connect to the database:

  ```python
  session = Updater(db_name="撫州話.sqlite3")
  ```

- Run SQL queries:

  ```python
  session.cursor.execute("my_sql_query")
  ```

  Get the result:

  ```python
  session.data  # type: list[dict[str, any]]
  ```

- Add a pronunciation for a character (in IPA or Pinyin, see [my website](https://colescu.github.io/fuzhou-gan/phonology) or `src\FGSyllable.py` for details):

  ```python
  session.add_entry("字")
  ```

- Choose the Middle Chinese index for a character:

  ```python
  session.add_MC_index("字")
  ```

- Commit changes and close the connection:

  ```python
  del session
  ```

# TODOs

- 修正中古音韻混亂（真臻諄、庚清）
- 異體字支持（例如窗窻、爲為）
- 添加推導白讀與新文讀的規則
- 在 `FGSyllable` 中加入音系限制
